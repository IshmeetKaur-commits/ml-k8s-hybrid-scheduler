import subprocess
import requests
import time
import csv
from datetime import datetime

API_URL = "http://127.0.0.1:5000/predict"


# -------------------------------
# FETCH NODE METRICS
# -------------------------------
def get_node_metrics():
    try:
        output = subprocess.check_output(
            ["kubectl", "top", "nodes"],
            universal_newlines=True
        )

        lines = output.strip().split("\n")[1:]
        nodes = []

        for line in lines:
            parts = line.split()

            nodes.append({
                "node": parts[0],
                "cpu": float(parts[1].replace("m", "")) / 1000,
                "memory": float(parts[3].replace("Mi", ""))
            })

        return nodes

    except Exception as e:
        print("❌ Error getting metrics:", e)
        return []


# -------------------------------
# ML PREDICTION
# -------------------------------
def predict_ml(node):
    data = {
        "cpu": node["cpu"],
        "memory": node["memory"],
        "hour": datetime.now().hour
    }

    try:
        response = requests.post(API_URL, json=data, timeout=2)
        return response.json().get("recommended_node", "fallback")
    except:
        return "fallback"


# -------------------------------
# COMPUTE SCORE
# -------------------------------
def compute_score(node, ml_pred):
    score = 0

    # ML contribution
    if ml_pred == node["node"]:
        score += 2

    # CPU (lower is better)
    score += max(0, 5 - node["cpu"])

    # Memory (lower is better)
    score += max(0, 1500 - node["memory"]) / 500

    return round(score, 2)


# -------------------------------
# GENERATE REASON
# -------------------------------
def generate_reason(node, ml_pred, all_nodes):
    reasons = []

    if ml_pred == node["node"]:
        reasons.append("ML recommended this node")

    min_cpu = min(n["cpu"] for n in all_nodes)
    if node["cpu"] == min_cpu:
        reasons.append("Lowest CPU usage")

    if node["memory"] < 1000:
        reasons.append("Memory within safe limit")

    if ml_pred == "fallback":
        reasons.append("ML unavailable, fallback used")

    return ", ".join(reasons)


# -------------------------------
# SELECT BEST NODE (SCORING)
# -------------------------------
def select_best_node(nodes):
    best_node = None
    best_score = -1
    ml_predictions = {}
    scores = {}

    print("\n📊 NODE ANALYSIS")
    print("========================")

    for node in nodes:
        ml_pred = predict_ml(node)
        ml_predictions[node["node"]] = ml_pred

        score = compute_score(node, ml_pred)
        scores[node["node"]] = score

        print(f"\nNode: {node['node']}")
        print(f"CPU: {node['cpu']}, Memory: {node['memory']}")
        print(f"ML Prediction: {ml_pred}")
        print(f"Score: {score}")

        if score > best_score:
            best_score = score
            best_node = node

    reason = generate_reason(best_node, ml_predictions[best_node["node"]], nodes)

    print("\n🎯 SELECTED NODE:", best_node["node"])
    print("🏆 Score:", best_score)
    print("🧠 Reason:", reason)

    return best_node, reason, scores


# -------------------------------
# DEPLOY POD
# -------------------------------
def deploy_pod_to_node(node_name):
    pod_name = f"ml-pod-{int(time.time())}"

    yaml_content = f"""
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
spec:
  nodeSelector:
    kubernetes.io/hostname: {node_name}
  containers:
  - name: cpu-loader
    image: busybox
    command: ["/bin/sh", "-c"]
    args:
      - |
        while true; do
          yes > /dev/null &
          sleep 2
          killall yes
          sleep 2
        done
    resources:
      requests:
        cpu: "200m"
      limits:
        cpu: "500m"
"""

    file_name = f"/tmp/{pod_name}.yaml"

    with open(file_name, "w") as f:
        f.write(yaml_content)

    subprocess.run(["kubectl", "apply", "-f", file_name])

    print(f"🚀 Deployed pod {pod_name} on {node_name}")


# -------------------------------
# AUTO SCALE
# -------------------------------
def auto_scale(avg_cpu):
    try:
        replicas = int(subprocess.getoutput(
            "kubectl get deployment cpu-loader-2-deployment -o=jsonpath='{.spec.replicas}'"
        ).replace("'", ""))

        if avg_cpu > 1.5 and replicas < 5:
            subprocess.run([
                "kubectl", "scale", "deployment",
                "cpu-loader-2-deployment",
                f"--replicas={replicas + 1}"
            ])
            print("📈 Scaling UP")

        elif avg_cpu < 0.5 and replicas > 1:
            subprocess.run([
                "kubectl", "scale", "deployment",
                "cpu-loader-2-deployment",
                f"--replicas={replicas - 1}"
            ])
            print("📉 Scaling DOWN")

    except Exception as e:
        print("Scaling error:", e)


# -------------------------------
# POD DISTRIBUTION (FIXED)
# -------------------------------
def get_pod_distribution():
    output = subprocess.getoutput("kubectl get pods -o wide")
    lines = output.split("\n")[1:]

    node_count = {}

    for line in lines:
        parts = line.split()
        if len(parts) > 6:
            node = parts[-3]   # FIXED index
            node_count[node] = node_count.get(node, 0) + 1

    return node_count


# -------------------------------
# LOG METRICS
# -------------------------------
def log_metrics(selected_node, nodes, sched_time, pod_dist, reason, scores):
    with open("metrics_log.csv", "a") as f:
        writer = csv.writer(f)

        for node in nodes:
            writer.writerow([
                datetime.now(),
                selected_node["node"],
                node["node"],
                node["cpu"],
                node["memory"],
                sched_time,
                pod_dist,
                reason,
                scores[node["node"]]
            ])


# -------------------------------
# MAIN
# -------------------------------
def main():
    start_time = time.time()

    nodes = get_node_metrics()

    if not nodes:
        print("❌ No nodes found")
        return

    avg_cpu = sum(n["cpu"] for n in nodes) / len(nodes)

    best_node, reason, scores = select_best_node(nodes)

    deploy_pod_to_node(best_node["node"])

    auto_scale(avg_cpu)

    pod_dist = get_pod_distribution()
    sched_time = round(time.time() - start_time, 4)

    print("\n📈 METRICS")
    print("Pod Distribution:", pod_dist)
    print("Scheduling Time:", sched_time)

    log_metrics(best_node, nodes, sched_time, pod_dist, reason, scores)

    print("\n✅ ML Scheduling Completed")


if __name__ == "__main__":
    main()