from flask import Flask, render_template, request, redirect, session
from model import predict
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret"

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

# -------- LOGIN PAGE --------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form["name"]
        session["age"] = request.form["age"]
        session["gender"] = request.form["gender"]
        return redirect("/dashboard")
    return render_template("login.html")

# -------- DASHBOARD --------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    result = None
    calories_burnt = None
    predicted_burn = None
    graph = None

    if request.method == "POST":
        food = float(request.form["food"])
        steps = float(request.form["steps"])
        sleep = float(request.form["sleep"])

        # Glucose prediction
        result = predict(food, steps, sleep)

        # Calories burned (simple formula)
        calories_burnt = steps * 0.04

        # Prediction (increase steps by 2000)
        predicted_steps = steps + 2000
        predicted_burn = predicted_steps * 0.04

        # -------- GRAPH --------
        labels = ["Current Burn", "Increased Steps Burn"]
        values = [calories_burnt, predicted_burn]

        plt.figure()
        plt.bar(labels, values)
        plt.title("Calories Burn Comparison")
        plt.ylabel("Calories")

        graph_path = "static/graph.png"
        plt.savefig(graph_path)
        plt.close()

        graph = graph_path

    return render_template("dashboard.html",
                           name=session.get("name"),
                           age=session.get("age"),
                           result=result,
                           calories_burnt=calories_burnt,
                           predicted_burn=predicted_burn,
                           graph=graph)

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
