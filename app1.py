from flask import Flask

app = Flask(__name__)
@app.route("/")
def HomePage():
    return "<h1>Hello Naveen </h1>"

if __name__ == "__main__":
    app.run(debug=True)
