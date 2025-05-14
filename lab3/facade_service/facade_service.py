import grpc
import random
import time
import requests
from flask import Flask, request, jsonify
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logging_service")))
import logging_pb2
import logging_pb2_grpc

app = Flask(__name__)

CONFIG_SERVER_URL = "http://127.0.0.1:8000/services/logging-service"

def get_logging_service_addresses():
    try:
        res = requests.get(CONFIG_SERVER_URL)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"[ConfigServer] ❌ Failed to get services: {e}")
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
                    return response.messages
        except Exception as e:
            print(f"[{host}:{port}] ❌ Failed attempt {attempt+1}: {e}")
    return None

@app.route("/log", methods=["POST"])
def post_message():
    data = request.get_json()
    msg = data.get("msg")

    addresses = get_logging_service_addresses()
    if not addresses:
        return {"error": "No available logging services"}, 500

    random.shuffle(addresses)
    for address in addresses:
        host, port = address.split(":")
        status = send_grpc_request(host, int(port), msg=msg, method="post")
        if status:
            return {"status": status, "uuid": str(time.time())}, 200

    return {"error": "All logging services unavailable"}, 500

@app.route("/log", methods=["GET"])
def get_messages():
    addresses = get_logging_service_addresses()
    if not addresses:
        return {"error": "No available logging services"}, 500

    random.shuffle(addresses)
    for address in addresses:
        host, port = address.split(":")
        messages = send_grpc_request(host, int(port), method="get")
        if messages is not None:
            return {"messages": list(messages)}, 200

    return {"error": "All logging services unavailable"}, 500

if __name__ == "__main__":
    app.run(port=7000)


