from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/mcp", methods=["GET"])
def manifest():
    return jsonify({
        "name": "tiny-add-mcp-python",
        "description": "A tiny MCP server implemented in Python.",
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
    })

@app.route("/mcp/invoke", methods=["POST"])
def invoke():
    data = request.get_json()
    tool = data.get("tool")
    params = data.get("params", {})
    call_id = data.get("callId")

    if tool == "add":
        a = params.get("a")
        b = params.get("b")

        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return jsonify({"error": "a and b must be numbers"}), 400

        return jsonify({
            "callId": call_id,
            "tool": "add",
            "result": {"sum": a + b},
            "status": "ok"
        })

    return jsonify({"error": "Unknown tool"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
