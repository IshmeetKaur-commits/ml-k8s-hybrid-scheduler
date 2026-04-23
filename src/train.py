import os
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from preprocess import load_and_preprocess

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_PATH, exist_ok=True)

def train_model():
    df, le = load_and_preprocess("../data/k8s_dataset.csv")

    X = df[['cpu(m)', 'memory(Mi)', 'hour']]
    y = df['node']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100),
        "DecisionTree": DecisionTreeClassifier(),
        "LogisticRegression": LogisticRegression(max_iter=1000)
    }

    results = {}

    # 🔁 Training loop
    for name, model in models.items():
        try:
            print(f"\nTraining {name}...")

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            results[name] = acc

            print(f"{name} Accuracy:", acc)
            print(classification_report(y_test, y_pred))

            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure()
            plt.imshow(cm)
            plt.title(f"{name} Confusion Matrix")
            plt.colorbar()
            labels = ["node1", "node2", "node3"]
            plt.xticks(np.arange(len(labels)), labels)
            plt.yticks(np.arange(len(labels)), labels)
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            # Add numbers inside cells
            for i in range(len(cm)):
                for j in range(len(cm)):
                    plt.text(j, i, cm[i, j],
                             ha="center", va="center")
            plt.savefig(os.path.join(MODEL_PATH, f"{name}_confusion_matrix.png"))

        except Exception as e:
            print(f"{name} failed:", e)

    print("\nFinal Results:", results)

    # 🏆 Select best model
    best_model_name = max(results, key=results.get)
    best_model = models[best_model_name]

    print("Best Model:", best_model_name)

    # Save model
    joblib.dump(best_model, os.path.join(MODEL_PATH, "scheduler_model.pkl"))
    joblib.dump(le, os.path.join(MODEL_PATH, "label_encoder.pkl"))

    # 📊 Model comparison graph
    if len(results) > 0:
        # plt.figure()
        # plt.bar(list(results.keys()), list(results.values()))
        # plt.title("Model Accuracy Comparison")
        # plt.ylabel("Accuracy")
        # plt.savefig(os.path.join(MODEL_PATH, "model_comparison.png"))
        # print("Saved model_comparison.png")
        plt.figure()

        models_names = list(results.keys())
        accuracies = list(results.values())

        plt.bar(models_names, accuracies)

        plt.title("Model Accuracy Comparison")
        plt.ylabel("Accuracy")

# 🔥 ZOOM THE SCALE (IMPORTANT)
        min_acc = min(accuracies)
        max_acc = max(accuracies)

        plt.ylim(min_acc - 0.02, max_acc + 0.02)

# Optional: show exact values on bars
        for i, v in enumerate(accuracies):
            plt.text(i, v, f"{v:.3f}", ha='center')

        plt.savefig(os.path.join(MODEL_PATH, "model_comparison.png"))
        plt.show()

        print("Saved model_comparison.png")
        
    # 📊 Feature Importance (FIXED)
    if best_model_name == "RandomForest":
        importances = best_model.feature_importances_
        features = ['cpu(m)', 'memory(Mi)', 'hour']

        print("Feature importances:", importances)

        plt.figure()
        plt.barh(features, importances)
        plt.title("Feature Importance")
        plt.xlabel("Importance Score")
        plt.savefig(os.path.join(MODEL_PATH, "feature_importance.png"))
        plt.show()

        print("Saved feature_importance.png")

    print("\nModel training complete!")

if __name__ == "__main__":
    train_model()