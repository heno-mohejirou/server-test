from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/add", methods=["POST"])
def add():
    data = request.json

    try:
        
        testname = data["testname"]
        username = data["username"]
        
        return jsonify({
                        "testname": testname,
                        "username": username, 
                        })
    except:
        return jsonify({"error": "数値を入力してください"}), 400

if __name__ == "__main__":
    app.run()