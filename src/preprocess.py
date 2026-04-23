import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import random

def load_and_preprocess(file_path):
    df = pd.read_csv(file_path)

    print("Loaded data:", df.shape)

    # Remove missing values
    df = df.dropna()

    # Convert CPU and Memory to numeric
    df['cpu(m)'] = df['cpu(m)'].str.replace('m', '', regex=False).astype(float)
    df['memory(Mi)'] = df['memory(Mi)'].str.replace('Mi', '', regex=False).astype(float)

    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour

    # 🔥 IMPORTANT FIX: Create MULTI-NODE labels
    # def assign_node(cpu):
    #     if cpu < 200:
    #         return "node1"
    #     else:
    #         return "node2"

    # df['node'] = df['cpu(m)'].apply(assign_node)

    # def assign_node(cpu, memory, hour):
    #     if cpu > 700 or memory > 400:
    #         return "node3"
    #     elif hour > 18:
    #         return "node2"
    #     else:
    #         return "node1"

    # df['node'] = df.apply(lambda x: assign_node(
    # x['cpu(m)'], x['memory(Mi)'], x['hour']), axis=1)

    def assign_node(cpu, memory, hour):
        if cpu > 700 or memory > 400:
            node = "node2"
        elif cpu > 300:
            node = "node1"
        else:
            node = "node2"

    # 🔥 ADD NOISE (5–10%)
        if random.random() < 0.1:
            node = random.choice(["node1", "node2"])

        return node

    df['node'] = df.apply(lambda x: assign_node(
        x['cpu(m)'], x['memory(Mi)'], x['hour']), axis=1)

    # Encode node labels
    le = LabelEncoder()
    df['node'] = le.fit_transform(df['node'])

    print("Processed data:", df.shape)

    return df, le