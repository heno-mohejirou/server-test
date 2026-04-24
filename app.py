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
    testname = data["testname"]
    grade = data["grade"]

    is_busy = True

    def task():
        global is_busy
        try:
            print("処理開始")

            time.sleep(5)

            result = f"{username}-{password}-{testname}-{grade}"
            print("result:", result)

            results[username] = result

            print("保存完了")

            requests.post(
                "https://my-worker.syousei-syousei-06-25.workers.dev/complete",
                json={"username": username}
            )

            print("通知完了")

        except Exception as e:
            print("エラー:", e)

        finally:
            is_busy = False
            print("処理終了")

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