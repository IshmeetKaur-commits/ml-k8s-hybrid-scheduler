import joblib

model = joblib.load("../models/scheduler_model.pkl")
le = joblib.load("../models/label_encoder.pkl")

def predict_node(cpu, memory, hour):
    pred = model.predict([[cpu, memory, hour]])
    node = le.inverse_transform(pred)[0]
    return node

if __name__ == "__main__":
    print("Predicted Node:", predict_node(600, 300, 10))