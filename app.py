from flask import Flask, render_template, request, redirect, session
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form.get('name')
        session['age'] = int(request.form.get('age', 0))
        session['gender'] = request.form.get('gender')
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
    graph = None

    if request.method == 'POST':
        try:
            # INPUTS
            food = float(request.form.get('food', 0))
            steps = float(request.form.get('steps', 0))
            sleep = float(request.form.get('sleep', 0))
            weight = float(request.form.get('weight', 0))
            height = float(request.form.get('height', 0))

            age = int(session.get('age', 0))
            gender = session.get('gender', 'male')

            # VALIDATION
            if height <= 0 or weight <= 0:
                return render_template("dashboard.html",
                    name=session.get("name"),
                    result="Invalid height/weight",
                    calories_burnt=0,
                    predicted_burn=0,
                    bmi=0,
                    body_fat=0,
                    graph=None
                )

            # CALCULATIONS
            result = round(80 + (food * 0.1) - (steps * 0.02) + (sleep * 2), 2)
            calories_burnt = round(steps * 0.04, 2)
            predicted_burn = round((steps + 1000) * 0.04, 2)

            bmi = round(weight / (height * height), 2)

            if gender == "male":
                body_fat = round((1.20 * bmi) + (0.23 * age) - 16.2, 2)
            else:
                body_fat = round((1.20 * bmi) + (0.23 * age) - 5.4, 2)

            # SAVE DATA
            new_data = pd.DataFrame({
                "Steps": [steps],
                "Calories": [calories_burnt]
            })

            if os.path.exists("data.csv"):
                new_data.to_csv("data.csv", mode='a', header=False, index=False)
            else:
                new_data.to_csv("data.csv", index=False)

            # GRAPH
            if os.path.exists("data.csv") and os.path.getsize("data.csv") > 0:
                df = pd.read_csv("data.csv")
            else:
                df = new_data

            plt.figure()
            plt.plot(df["Steps"], df["Calories"], marker='o')
            plt.xlabel("Steps")
            plt.ylabel("Calories Burnt")
            plt.title("Calories vs Steps")

            plt.savefig("static/graph.png")
            plt.close()

            graph = "graph.png"

        except Exception as e:
            print("REAL ERROR:", e)
            result = str(e)

    return render_template("dashboard.html",
        name=session.get("name"),
        result=result,
        calories_burnt=calories_burnt,
        predicted_burn=predicted_burn,
        bmi=bmi,
        body_fat=body_fat,
        graph=graph
    )


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
