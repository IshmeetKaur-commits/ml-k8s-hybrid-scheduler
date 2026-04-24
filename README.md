# ML-Based Kubernetes Scheduler

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-green)
![ML](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)

## 📋 Overview
This project optimizes Kubernetes pod scheduling by replacing static rules with **Machine Learning** predictions. It analyzes real-time CPU and memory metrics to decide the best node for deployment.

---

## 🏗 System Architecture
1. **Metrics Collection:** Fetches node data via K8s Metrics Server.
2. **ML Inference:** A Flask API serves a Random Forest model to score nodes.
3. **Deployment:** The scheduler triggers `kubectl` to place the pod.
4. **Visualization:** A Streamlit dashboard tracks live performance.

---

## 📁 Project Structure
```text
ml-k8s-project/
├── api/
│   └── app.py                # Flask API (Model Server)
├── src/
│   └── train.py              # Model Training
├── models/                   # Saved .pkl files & plots
├── ml_scheduler.py           # Main Scheduler Logic
├── app_ui.py                 # Streamlit Dashboard
└── deployments/              # YAML Manifests


🛠 Setup & Running
1. Prerequisites
Python 3.12

Minikube (with 2+ nodes)

2. Installation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install flask streamlit pandas scikit-learn matplotlib joblib


3. Execution Steps
Step	Action	Command
1	Train Model	python src/train.py
2	Start API	python api/app.py
3	Run Dashboard	streamlit run app_ui.py
4	Run Scheduler	python ml_scheduler.py


📊 Sample Output

Node: minikube-m02 | CPU: 2.1% | Mem: 400Mi
Selected Node: minikube-m02
Reason: Lowest CPU usage predicted by ML model.
Status: Deployment Successful.


👥 Authors
Ishmeet Kaur

Anshika Goyal

📜 License
Academic Use Only.


---

### Why it might have looked bad before:
1.  **Indentation:** Markdown code blocks (the ` ``` ` parts) must start at the very beginning of the line.
2.  **Empty Lines:** Tables and lists need an empty line above them to "trigger" the formatting.
3.  **File Extension:** Ensure your file is named exactly `README.md`. If you name it `README.txt`, the preview will just show plain text.

**Pro-tip for VS Code:** If you are using VS Code, press `Ctrl + Shift + V` (Windows) to see a live "formatted" preview of the file while you edit!
