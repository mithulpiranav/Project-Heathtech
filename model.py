import pandas as pd
from sklearn.linear_model import LinearRegression

# Load dataset
data = pd.read_csv("data.csv")

# Features and output
X = data[["food", "steps", "sleep"]]
y = data["glucose"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Prediction function
def predict(food, steps, sleep):
    prediction = model.predict([[food, steps, sleep]])
    return prediction[0]