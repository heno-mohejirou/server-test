from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/add", methods=["POST"])
def add():
    data = request.json

    try:
        grade = data["grade"]
        testname = data["testname"]
        username = data["username"]
        password = data["password"]
        
        return jsonify({"grade": grade,
                        "testname": testname,
                        "username": username, 
                        "password": password})
    except:
        return jsonify({"error": "数値を入力してください"}), 400

if __name__ == "__main__":
    app.run()