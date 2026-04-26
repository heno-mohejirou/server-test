from flask import Flask, request, jsonify
from flask_cors import CORS
from scrap_main import main
import threading
import requests

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
    username = data["username"]
    password = data["password"]
    testnames = data["testname"]
    grade = data["grade"]

    print(f"{testnames}, {password}, {username}, {grade}", flush=True)

    is_busy = True

    def task(grade_param):
        global is_busy

        print("TASK START", flush=True)

        if isinstance(testnames, str):
            tn = [testnames]
        else:
            tn = testnames

        grade_local = str(grade_param)

        if grade_local == "0":
            grade = "sophomore"
        else:
            grade = "junior"

        result = main(tn, password, username, grade)
        results[username] = result

        is_busy = False

    threading.Thread(target=task, args=(grade,)).start()

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