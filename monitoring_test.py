import random
import time

import pandas as pd
import requests

API_URL = "http://prod-api-alb-1845921752.us-east-1.elb.amazonaws.com/api/v1/predict"

positive_examples = [
    ("Amazing", "This product is fantastic, I absolutely love it!"),
    ("Great purchase", "Exceeded all my expectations, very happy!"),
    ("Perfect", "Excellent quality and incredible performance."),
    ("Wonderful", "I am extremely satisfied, highly recommended!"),
    ("Five stars", "The best product I’ve bought this year."),
]

negative_examples = [
    ("Terrible", "Worst experience ever, I hate this product."),
    ("Disappointed", "Low quality, not worth the money."),
    ("Awful", "Completely useless, very bad purchase."),
    ("Horrible", "Terrible quality, arrived broken."),
    ("Waste of money", "Absolutely not recommended, awful product."),
]

results = []


def send_request(title, message):
    payload = {"title": title, "message": message}
    start = time.perf_counter()

    response = requests.post(API_URL, json=payload, timeout=10)
    latency_ms = (time.perf_counter() - start) * 1000.0

    print("response", response)
    data = response.json()

    return {
        "title": title,
        "message": message,
        "prediction_label": data.get("prediction_label"),
        "prediction_label_name": data.get("prediction_label_name"),
        "confidence": data.get("confidence"),
        "sentiment": data.get("sentiment"),
        "latency_ms": latency_ms,
    }


print("Sending 100 requests to API...")

for i in range(50):
    title, msg = random.choice(positive_examples)
    results.append(send_request(title, msg))

for i in range(50):
    title, msg = random.choice(negative_examples)
    results.append(send_request(title, msg))

df = pd.DataFrame(results)
df.to_csv("monitoring_current.csv", index=False)

print("Done! File saved as monitoring_current.csv")
