import grpc
import random
import time
import requests
from flask import Flask, request, jsonify
import sys
import os
import hazelcast

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logging_service")))
from logging_service import logging_pb2, logging_pb2_grpc

app = Flask(__name__)

# config-server endpoint
CONFIG_SERVER_URL = "http://127.0.0.1:8000/services/logging-service"
MESSAGES_SERVICE_URL = "http://127.0.0.1:8000/services/messages-service"

# Hazelcast Queue для логування

client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        "127.0.0.1:5701",
        "127.0.0.1:5702",
        "127.0.0.1:5703"
    ]
)

log_queue = client.get_queue("log_queue").blocking()

def get_service_addresses(service_name):
    try:
        res = requests.get(f"http://127.0.0.1:8000/services/{service_name}")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"[ConfigServer] ❌ Failed to get {service_name}: {e}")
    return []


def send_grpc_request(host, port, msg=None, method="post"):
    for attempt in range(3):
        try:
            with grpc.insecure_channel(f"{host}:{port}") as channel:
                stub = logging_pb2_grpc.LoggingServiceStub(channel)

                if method == "post":
                    response = stub.LogMessage(logging_pb2.LogRequest(msg=msg, uuid=str(time.time())))
                    return response.status
                elif method == "get":
                    response = stub.GetMessages(logging_pb2.Empty())
                    return list(response.messages)
        except Exception as e:
            print(f"[{host}:{port}] ❌ Failed attempt {attempt+1}: {e}")
    return None


@app.route("/log", methods=["POST"])
def post_message():
    data = request.get_json()
    msg = data.get("msg")

    # 1. GRPC → logging_service
    addresses = get_service_addresses("logging-service")
    if not addresses:
        return {"error": "No logging services available"}, 500

    random.shuffle(addresses)
    grpc_success = False
    for address in addresses:
        host, port = address.split(":")
        status = send_grpc_request(host, int(port), msg=msg, method="post")
        if status:
            grpc_success = True
            break

    if not grpc_success:
        return {"error": "All logging services failed"}, 500

    # 2. Hazelcast Queue → для messages_service
    log_queue.offer(msg)

    return {"status": "success", "msg": msg}, 200


@app.route("/log", methods=["GET"])
def get_messages():
    # Отримуємо GRPC-повідомлення
    logging_messages = []
    addresses = get_service_addresses("logging-service")
    random.shuffle(addresses)
    for address in addresses:
        host, port = address.split(":")
        messages = send_grpc_request(host, int(port), method="get")
        if messages is not None:
            logging_messages = messages
            break

    # Отримуємо REST-повідомлення від messages-service
    msg_addresses = get_service_addresses("messages-service")
    messages_messages = []
    random.shuffle(msg_addresses)
    for address in msg_addresses:
        try:
            res = requests.get(f"http://{address}/messages")
            if res.status_code == 200:
                messages_messages = res.json().get("messages", [])
                break
        except Exception as e:
            print(f"[{address}] ❌ Failed to fetch messages-service: {e}")

    return jsonify({
        "from_logging": logging_messages,
        "from_messages_service": messages_messages
    })

if __name__ == "__main__":
    app.run(port=7000)


