from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# 状態管理
is_busy = False
results = {}  # usernameごとに結果保存

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"busy": is_busy})


@app.route("/process", methods=["POST"])
def process():
    global is_busy

    if is_busy:
        return jsonify({"error": "busy"}), 429

    data = request.json
    username = data["username"]
    password = data["password"]

    is_busy = True

    # 非同期処理
    def task():
        global is_busy

        time.sleep(5)  # ← Seleniumの代わり

        result = f"{username}-{password}"
        results[username] = result

        is_busy = False

    threading.Thread(target=task).start()

    return jsonify({"status": "started"})


@app.route("/result", methods=["GET"])
def get_result():
    username = request.args.get("username")

    if username in results:
        return jsonify({
            "done": True,
            "result": results[username]
        })
    else:
        return jsonify({"done": False})


if __name__ == "__main__":
    app.run()