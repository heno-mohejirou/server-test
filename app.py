# app.py
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        num1 = request.form.get("num1")
        num2 = request.form.get("num2")

        try:
            result = int(num1) + int(num2)
        except:
            result = "エラー（数値を入力してください）"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)