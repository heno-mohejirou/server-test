from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/add", methods=["POST"])
def add():
    data = request.json

    try:
        num1 = int(data["num1"])
        num2 = int(data["num2"])
        result = num1 + num2
        return jsonify({"result": result})
    except:
        return jsonify({"error": "数値を入力してください"}), 400

if __name__ == "__main__":
    app.run()