# process.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    data = request.json

    username = data["username"]
    password = data["password"]

    # ハイフンで結合
    result = f"{username}-{password}"

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run()