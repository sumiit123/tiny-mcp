import os
import json
import logging
from flask import Flask, request, Response, jsonify

# ---- Setup ----
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
app = Flask(__name__)

# ---- Manifest payload ----
def build_manifest():
    """
    Return a manifest JSON object describing your MCP tools.
    Edit this if you add more tools.
    """
    payload = {
        "name": "tiny-add-mcp-python",
        "description": "A tiny MCP server implemented in Python that exposes an add(a,b) tool.",
        "version": "0.1.0",
        "tools": [
            {
                "id": "add",
                "name": "Add two numbers",
                "description": "Takes numbers a and b and returns a + b.",
                "params": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            }
        ]
    }
    return payload

def sse_event_for_manifest():
    """
    Return a single-server-sent-event containing the manifest.
    SSE events must be lines that start with 'data: ' and end with a blank line.
    """
    manifest_json = json.dumps(build_manifest())
    # A single event. If you later want to stream updates, yield multiple such blocks.
    return f"data: {manifest_json}\n\n"

# ---- Routes ----
@app.route("/", methods=["GET"])
def index():
    """Simple root page to confirm service is running."""
    return (
        "<html><body><h2>Tiny MCP server (Flask)</h2>"
        "<p>Manifest: <a href='/mcp'>/mcp</a></p>"
        "<p>Invoke: POST /mcp/invoke</p>"
        "</body></html>"
    )

@app.route("/mcp", methods=["GET"])
def manifest():
    """
    Return manifest as an SSE stream (Content-Type: text/event-stream).
    ChatGPT Developer Mode expects text/event-stream for the manifest endpoint.
    """
    logging.info("Serving SSE manifest to %s", request.remote_addr)
    return Response(sse_event_for_manifest(), mimetype="text/event-stream")

@app.route("/mcp/invoke", methods=["POST"])
def invoke():
    """
    Handle tool invocations.
    Expected body:
      { "tool": "add", "params": { "a": <num>, "b": <num> }, "callId": "<optional>" }
    Returns JSON:
      { "callId": ..., "tool": "add", "result": { "sum": <num> }, "status": "ok" }
    """
    try:
        data = request.get_json(force=True)
    except Exception as e:
        logging.exception("Failed to parse JSON body")
        return jsonify({"error": "Invalid JSON body"}), 400

    logging.info("Invoke request: %s", data)

    tool = data.get("tool")
    params = data.get("params", {}) or {}
    call_id = data.get("callId")

    if tool == "add":
        a = params.get("a")
        b = params.get("b")
        # Strict type check: must be int or float
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return jsonify({"error": "params 'a' and 'b' must be numbers"}), 400

        result = a + b
        response = {
            "callId": call_id,
            "tool": "add",
            "result": {"sum": result},
            "status": "ok"
        }
        logging.info("Returning result for callId=%s sum=%s", call_id, result)
        return jsonify(response)

    return jsonify({"error": f"Unknown tool '{tool}'"}), 404

# Health endpoint (optional)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# ---- Run App ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    # Host 0.0.0.0 so cloud services (Render) can reach it
    app.run(host="0.0.0.0", port=port)
