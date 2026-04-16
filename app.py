from flask import Flask, render_template, request, redirect, session, url_for
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
        session['age'] = int(request.form.get('age'))
        session['gender'] = request.form.get('gender')
        return redirect('/dashboard')
    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'name' not in session:
        return redirect('/')

    result = None
    glucose = None
    calories_burnt = None
    predicted_burn = None
    bmi = None
    body_fat = None
    graph = None

    if request.method == 'POST':
        try:
            # -------- GET INPUT --------
            food = request.form.get('food')
            steps = request.form.get('steps')
            sleep = request.form.get('sleep')
            weight = request.form.get('weight')
            height = request.form.get('height')

            # -------- CHECK EMPTY --------
            if not all([food, steps, sleep, weight, height]):
                return render_template("dashboard.html",
                    name=session.get("name"),
                    result="Please fill all fields",
                    graph=None
                )

            # -------- CONVERT --------
            food = float(food)
            steps = float(steps)
            sleep = float(sleep)
            weight = float(weight)
            height = float(height)

            age = int(session.get('age'))
            gender = session.get('gender')

            # -------- VALIDATION --------
            if height <= 0 or weight <= 0:
                return render_template("dashboard.html",
                    name=session.get("name"),
                    result="Invalid height or weight",
                    graph=None
                )

            # -------- CALCULATIONS --------

            # Health Score
            result = round(80 + (food * 0.1) - (steps * 0.02) + (sleep * 2), 2)

            # Glucose estimate (mg/dL) — simplified heuristic model
            # Base fasting glucose ~90, rises with food intake, lowers with activity
            glucose = round(90 + (food * 0.05) - (steps * 0.003) - (sleep * 0.5), 2)
            glucose = max(60, min(glucose, 300))  # clamp to realistic range

            # Calories
            calories_burnt = round(steps * 0.04, 2)
            predicted_burn = round((steps + 1000) * 0.04, 2)

            # BMI
            bmi = round(weight / (height * height), 2)

            # Body Fat %
            if gender == "male":
                body_fat = round((1.20 * bmi) + (0.23 * age) - 16.2, 2)
            else:
                body_fat = round((1.20 * bmi) + (0.23 * age) - 5.4, 2)

            # -------- SAVE DATA --------
            new_data = pd.DataFrame({
                "Steps": [steps],
                "Calories": [calories_burnt]
            })

            if os.path.exists("data.csv"):
                new_data.to_csv("data.csv", mode='a', header=False, index=False)
            else:
                new_data.to_csv("data.csv", index=False)

            # -------- READ DATA (safe) --------
            try:
                if os.path.exists("data.csv") and os.path.getsize("data.csv") > 0:
                    df = pd.read_csv("data.csv")
                    # Reset if columns are wrong / corrupted
                    if not {"Steps", "Calories"}.issubset(df.columns):
                        df = new_data
                        df.to_csv("data.csv", index=False)
                else:
                    df = new_data
            except Exception:
                # CSV is corrupt — reset it
                df = new_data
                df.to_csv("data.csv", index=False)

            # -------- GRAPH --------
            plt.figure(figsize=(6, 4))
            plt.plot(df["Steps"].values, df["Calories"].values,
                     marker='o', color='#4CAF50', linewidth=2, markersize=6)
            plt.xlabel("Steps")
            plt.ylabel("Calories Burnt")
            plt.title("Calories Burnt vs Steps Trend")
            plt.tight_layout()
            plt.savefig("static/graph.png")
            plt.close()

            graph = "graph.png"

        except Exception as e:
            print("ERROR:", e)
            result = f"Error: {str(e)}"

    return render_template("dashboard.html",
        name=session.get("name"),
        result=result,
        glucose=glucose,
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
    app.run(debug=True)
