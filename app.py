from flask import Flask, request, jsonify
from flask_cors import CORS
from scrap_main import main
import threading

app = Flask(__name__)
CORS(app)

# 状態管理
is_busy = False
results = {}


@app.route("/")
def home():
    print("DEBUG HIT", flush=True)
    return "OK"


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"busy": is_busy})


@app.route("/process", methods=["POST"])
def process():
    global is_busy

    if is_busy:
        return jsonify({"error": "busy"}), 429

    data = request.json

    # ==========================================
    # データ取得
    # ==========================================
    username = data["username"]
    password = data["password"]
    testnames = data["testname"]
    details = data["testDetails""]

    # ==========================================
    # 入力確認
    # ==========================================
    if not details:
        return jsonify({
            "error": "details is required"
        }), 400

    if username in results:
        del results[username]

    print(
        f"testname: {testnames}",
        flush=True
    )

    print(
        f"details: {details}",
        flush=True
    )

    print(
        f"username: {username}",
        flush=True
    )

    is_busy = True

    def task():
        global is_busy

        try:
            print("TASK START", flush=True)

            # testnameをリスト化
            if isinstance(testnames, str):
                tn = [testnames]
            else:
                tn = testnames

            # detailsを確認
            if not isinstance(details, list):
                raise ValueError("details must be a list")

            print(
                f"testnames: {tn}",
                flush=True
            )

            print(
                f"details: {details}",
                flush=True
            )

            # ==========================================
            # メイン処理
            # ==========================================
            result = main(
                tn,
                password,
                username,
                details
            )

            results[username] = result

        except Exception as e:
            print(
                f"Fatal task error: {e}",
                flush=True
            )

            results[username] = (
                f"Fatal Error: {e}"
            )

        finally:
            is_busy = False

    threading.Thread(
        target=task
    ).start()

    return jsonify({
        "status": "started"
    })


@app.route("/result", methods=["GET"])
def get_result():
    username = request.args.get("username")

    if username in results:
        return jsonify({
            "done": True,
            "result": results[username]
        })

    return jsonify({
        "done": False
    })


if __name__ == "__main__":
    app.run()
