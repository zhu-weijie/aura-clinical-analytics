import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

print("--- Starting Model Training ---")


data = pd.read_csv("notebooks/sample_data.csv")
X = data[["heart_rate", "spo2"]]
y = data["risk_level"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Training with {len(X_train)} samples.")


model = LogisticRegression()
model.fit(X_train, y_train)


accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")


model_filename = "aura_risk_model.joblib"
joblib.dump(model, model_filename)
print(f"Model saved as '{model_filename}'")
print("--- Model Training Complete ---")
