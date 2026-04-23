import subprocess
import time
import csv
from datetime import datetime

with open("k8s_dataset.csv", "a") as f:
    writer = csv.writer(f)

    while True:
        pods = subprocess.getoutput("kubectl get pods -o wide").split("\n")[1:]
        metrics = subprocess.getoutput("kubectl top pods").split("\n")[1:]

        for p, m in zip(pods, metrics):
            p_parts = p.split()
            m_parts = m.split()

            if len(p_parts) > 6 and len(m_parts) > 2:
                writer.writerow([
                    datetime.now(),
                    p_parts[0],
                    m_parts[1],
                    m_parts[2],
                    p_parts[6]
                ])

        time.sleep(5)
        