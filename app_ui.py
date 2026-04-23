import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="ML Kubernetes Scheduler", layout="wide")

st.title("🚀 ML-Based Kubernetes Scheduler Dashboard")

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("⚙️ Controls")

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

st.sidebar.info("ML Scheduler Dashboard\nBuilt with Streamlit")

# -------------------------------
# FETCH NODE METRICS
# -------------------------------
def get_node_metrics():
    try:
        output = subprocess.getoutput("kubectl top nodes")
        lines = output.split("\n")[1:]

        data = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                data.append({
                    "Node": parts[0],
                    "CPU (cores)": float(parts[1].replace("m", "")) / 1000,
                    "Memory (Mi)": float(parts[3].replace("Mi", ""))
                })

        return pd.DataFrame(data)

    except:
        return pd.DataFrame()


# -------------------------------
# POD DISTRIBUTION
# -------------------------------
def get_pod_distribution():
    output = subprocess.getoutput("kubectl get pods -o wide")
    lines = output.split("\n")[1:]

    node_count = {}

    for line in lines:
        parts = line.split()
        if len(parts) > 6:
            node = parts[-3]   # safer than fixed index
            node_count[node] = node_count.get(node, 0) + 1

    return node_count


# -------------------------------
# LOAD METRICS LOG
# -------------------------------
def load_metrics():
    try:
        df = pd.read_csv("metrics_log.csv", header=None)
        df.columns = [
            "Timestamp",
            "Selected Node",
            "Node",
            "CPU",
            "Memory",
            "Scheduling Time",
            "Pod Distribution",
            "Reason",
            "Score"
        ]
        return df
    except:
        return pd.DataFrame()


# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Live Cluster",
    "📦 Pod Distribution",
    "📈 Historical Analytics",
    "🤖 ML Analysis"
])

# -------------------------------
# TAB 1: LIVE CLUSTER
# -------------------------------
with tab1:
    node_df = get_node_metrics()
    df = load_metrics()

    if not node_df.empty:
        st.subheader("📊 Current Node Metrics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Nodes", len(node_df))
        col2.metric("Avg CPU", f"{node_df['CPU (cores)'].mean():.2f}")
        col3.metric("Avg Memory", f"{node_df['Memory (Mi)'].mean():.0f} Mi")

        # LAST DECISION
        if not df.empty:
            last = df.iloc[-1]

            st.subheader("🎯 Last Scheduling Decision")

            c1, c2, c3 = st.columns(3)
            c1.metric("Selected Node", last["Selected Node"])
            c2.metric("CPU", f"{float(last['CPU']):.2f}")
            c3.metric("Memory", f"{float(last['Memory']):.0f}")

            st.subheader("🧠 Explanation")

            reasons = str(last["Reason"]).split(", ")
            for r in reasons:
                st.write(f"- {r}")

            st.subheader("🏆 Node Scores")

            score_df = df[["Node", "Score"]].drop_duplicates()
            st.bar_chart(score_df.set_index("Node"))

        # LIVE METRICS
        st.subheader("📉 CPU Usage")
        st.bar_chart(node_df.set_index("Node")["CPU (cores)"])

        st.subheader("📉 Memory Usage")
        st.bar_chart(node_df.set_index("Node")["Memory (Mi)"])

    else:
        st.warning("Metrics not available")


# -------------------------------
# TAB 2: POD DISTRIBUTION
# -------------------------------
with tab2:
    st.subheader("📦 Pod Distribution")

    pod_dist = get_pod_distribution()

    if pod_dist:
        df_pods = pd.DataFrame(
            list(pod_dist.items()),
            columns=["Node", "Pods"]
        ).set_index("Node")

        st.dataframe(df_pods)
        st.bar_chart(df_pods)
    else:
        st.write("No pod data available")


# -------------------------------
# TAB 3: HISTORICAL ANALYTICS
# -------------------------------
with tab3:
    st.subheader("📈 Historical Data")

    df = load_metrics()

    if not df.empty:
        st.dataframe(df.tail(10))

        st.subheader("📊 CPU Trend")
        st.line_chart(pd.to_numeric(df["CPU"], errors="coerce"))

        st.subheader("📊 Scheduling Time")
        st.line_chart(pd.to_numeric(df["Scheduling Time"], errors="coerce"))

        st.subheader("📊 Node Selection Frequency")
        st.bar_chart(df["Selected Node"].value_counts())

    else:
        st.warning("No metrics yet")


# -------------------------------
# TAB 4: ML ANALYSIS
# -------------------------------
with tab4:
    st.subheader("🤖 Machine Learning Model Analysis")

    model_path = "models"

    # Accuracy comparison
    comp_path = os.path.join(model_path, "model_comparison.png")
    if os.path.exists(comp_path):
        st.image(comp_path, caption="Model Accuracy Comparison")
    else:
        st.warning("Model comparison not found. Run train.py.")

    # Feature importance
    feat_path = os.path.join(model_path, "feature_importance.png")
    if os.path.exists(feat_path):
        st.image(feat_path, caption="Feature Importance")

    # Confusion matrices
    st.subheader("Confusion Matrices")

    for model_name in ["RandomForest", "DecisionTree"]:
        cm_path = os.path.join(model_path, f"{model_name}_confusion_matrix.png")
        if os.path.exists(cm_path):
            st.image(cm_path, caption=f"{model_name} Confusion Matrix")