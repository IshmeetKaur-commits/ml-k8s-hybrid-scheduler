import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/k8s_dataset.csv")

# CPU distribution
plt.figure()
sns.histplot(df['cpu(m)'], kde=True)
plt.title("CPU Usage Distribution")
plt.savefig("../models/cpu_distribution.png")

# Memory vs CPU
plt.figure()
sns.scatterplot(x=df['cpu(m)'], y=df['memory(Mi)'])
plt.title("CPU vs Memory")
plt.savefig("../models/cpu_memory.png")

print("Graphs saved!")