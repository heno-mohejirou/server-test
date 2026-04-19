from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/add", methods=["POST"])
def add():
    data = request.json

    try:
        password = data["password"]
        username = data["username"]

        return jsonify({
                        "username": username,
                        "password": password
                        })
    except:
        return jsonify({"error": "数値を入力してください"}), 400

if __name__ == "__main__":
    app.run()