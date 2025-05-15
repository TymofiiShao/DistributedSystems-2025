import requests
import random
import json
from flask import Flask, request
from consul import Consul
import threading

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from consul_register import register_service

consul_client = Consul(host="localhost", port=8500)

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

def get_service_address(service_name):
    """Повертає (ip, port) випадкового екземпляру сервісу з Consul"""
    services = consul_client.health.service(service_name, passing=True)[1]
    if not services:
        raise Exception(f"No available service instances for {service_name}")
    service = random.choice(services)["Service"]
    return service["Address"], service["Port"]

def get_kv_config(key):
    """Зчитує значення з Consul KV"""
    index, data = consul_client.kv.get(key)
    if data is None:
        raise Exception(f"KV key '{key}' not found")
    return data["Value"].decode()

@app.route("/send", methods=["POST"])
def send():
    # Дані, які будемо надсилати
    payload = request.get_json()

    logging_ip, logging_port = get_service_address("logging-service")
    messages_ip, messages_port = get_service_address("messages-service")

    queue_name = get_kv_config("message_queue/queue_name")

    print(f"[FACADE] Queue config: {queue_name}")

    # Надсилаємо в logging
  ##  logging_url = f"http://{logging_ip}:{logging_port}/log"
  ##  requests.post(logging_url, json=payload)

    #Надсилаємо в messages
    messages_url = f"http://{messages_ip}:{messages_port}/send"
    requests.post(messages_url, json=payload)

    return {"status": "sent"}, 200

def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    #Health чек окремо
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5050), daemon=True).start()

    # Реєстрація фасаду в Consul
    register_service("facade-service", "facade-5000", port=5000, check_path="/health")

    run_flask()




