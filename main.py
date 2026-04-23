import os

print("Training model...")
os.system("python src/train.py")

print("\nTesting prediction...")
os.system("python src/predict.py")

print("\nDone!")