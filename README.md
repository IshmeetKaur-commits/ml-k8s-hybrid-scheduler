# ML-Based Kubernetes Scheduler

## 📌 Overview
This project predicts optimal node placement for Kubernetes pods using Machine Learning.

## 🚀 Features
- Data preprocessing pipeline
- Random Forest ML model
- REST API for prediction
- Visualization of resource usage

## 🛠 Tech Stack
- Python
- Scikit-learn
- Flask
- Pandas

## 📂 Structure
- src/ → ML logic
- api/ → API server
- models/ → saved models
- data/ → dataset

## ▶️ Run Project
pip install -r requirements.txt
cd src
python train.py

cd ../api
python app.py

## 📊 Results
- Accuracy: XX%