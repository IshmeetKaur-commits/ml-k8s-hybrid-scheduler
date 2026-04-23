from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# -------------------------------
# LOAD MODEL
# -------------------------------
model = joblib.load("../models/scheduler_model.pkl")
le = joblib.load("../models/label_encoder.pkl")


# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route('/')
def home():
    return "Kubernetes ML Scheduler API Running"


# -------------------------------
# PREDICT (USED BY ml_scheduler.py)
# -------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    cpu = data.get('cpu')
    memory = data.get('memory')
    hour = data.get('hour')

    if cpu is None or memory is None or hour is None:
        return jsonify({"error": "Missing input"}), 400

    # ML Prediction
    pred = model.predict([[cpu, memory, hour]])
    node = le.inverse_transform(pred)[0]

    return jsonify({
        "cpu": cpu,
        "memory": memory,
        "hour": hour,
        "recommended_node": node
    })


# -------------------------------
# FILTER (K8s Scheduler Extender)
# -------------------------------
@app.route('/filter', methods=['POST'])
def filter_nodes():
    data = request.get_json()

    nodes = data.get("nodes", {}).get("items", [])
    selected_nodes = []

    for node in nodes:
        node_name = node["metadata"]["name"]

        import subprocess

        try:
            output = subprocess.check_output(
                ["kubectl", "top", "node", node_name],
                universal_newlines=True
            )

            parts = output.strip().split("\n")[1].split()

            cpu = float(parts[1].replace("m", "")) / 1000
            memory = float(parts[3].replace("Mi", ""))

        except:
            cpu, memory = 1.0, 1000  # fallback

        # ML Prediction
        hour = 12
        pred = model.predict([[cpu, memory, hour]])
        workload = le.inverse_transform(pred)[0]

        # Filter logic
        if workload != "high":
            selected_nodes.append(node)

    return jsonify({
        "nodes": {
            "items": selected_nodes
        }
    })


# -------------------------------
# PRIORITIZE (SIMPLE FOR NOW)
# -------------------------------
@app.route('/prioritize', methods=['POST'])
def prioritize_nodes():
    data = request.get_json()
    nodes = data.get("nodes", {}).get("items", [])

    scores = []

    for node in nodes:
        scores.append({
            "name": node["metadata"]["name"],
            "score": 10
        })

    return jsonify(scores)


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)