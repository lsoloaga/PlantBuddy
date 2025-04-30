from flask import Flask, request, render_template, redirect
from query_runner import run_query
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    summaries = None  

    if request.method == "POST":
        user_text = request.form.get("text")  # Get user input from the form
        if user_text:
            summaries = run_query(user_text)  # Call logic and get summaries

    return render_template("form.html", summaries=summaries)  # Show results 

@app.route("/success")
def success():
    return "Query processed!"


if __name__ == "__main__":
    app.run(debug=True)



