from flask import Flask, render_template, request, redirect, session
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- HOME / LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['age'] = int(request.form['age'])
        session['gender'] = request.form['gender']
        return redirect('/dashboard')
    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'name' not in session:
        return redirect('/')

    result = None
    calories_burnt = None
    predicted_burn = None
    bmi = None
    body_fat = None

    if request.method == 'POST':
        # Inputs
        food = float(request.form['food'])
        steps = int(request.form['steps'])
        sleep = float(request.form['sleep'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        age = int(session['age'])
        gender = session['gender']

        # ---------------- CALCULATIONS ----------------

        # Glucose (simple logic model)
        result = round(80 + (food * 0.1) - (steps * 0.02) + (sleep * 2), 2)

        # Calories burned
        calories_burnt = round(steps * 0.04, 2)

        # Predicted burn if steps increase
        predicted_burn = round((steps + 1000) * 0.04, 2)

        # BMI
        bmi = round(weight / (height * height), 2)

        # Body Fat %
        if gender == "male":
            body_fat = round((1.20 * bmi) + (0.23 * age) - 16.2, 2)
        else:
            body_fat = round((1.20 * bmi) + (0.23 * age) - 5.4, 2)

        # ---------------- SAVE DATA ----------------
        data = pd.DataFrame({
            "Steps": [steps],
            "Calories": [calories_burnt]
        })

        if os.path.exists("data.csv"):
            data.to_csv("data.csv", mode='a', header=False, index=False)
        else:
            data.to_csv("data.csv", index=False)

        # ---------------- GRAPH ----------------
        df = pd.read_csv("data.csv")

        plt.figure()
        plt.plot(df["Steps"], df["Calories"])
        plt.xlabel("Steps")
        plt.ylabel("Calories Burnt")
        plt.title("Calories vs Steps Trend")

        if not os.path.exists("static"):
            os.makedirs("static")

        plt.savefig("static/graph.png")
        plt.close()

    return render_template("dashboard.html",
                           name=session.get("name"),
                           result=result,
                           calories_burnt=calories_burnt,
                           predicted_burn=predicted_burn,
                           bmi=bmi,
                           body_fat=body_fat,
                           graph="static/graph.png")


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
