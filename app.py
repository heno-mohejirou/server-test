from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import requests

app = Flask(__name__)
CORS(app)

# 状態管理
is_busy = False
results = {}

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
    #testname = data["testname"]
    #grade = data["grade"]

    is_busy = True

    def task():
        global is_busy

        time.sleep(5)  # ← Seleniumの代わり

        result = f"{username}-{password}" #-{testname}-{grade}"
        results[username] = result

        # 🔥 ここで通知（重要）
        try:
            requests.post(
                "https://my-worker.syousei-syousei-06-25.workers.dev/complete",
                json={"username": username}
            )
        except Exception as e:
            print("通知失敗:", e)

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