from fastapi import FastAPI, Request
import uuid
import requests
import grpc
import time

import logging_service.logging_pb2 as logging_pb2
import logging_service.logging_pb2_grpc as logging_pb2_grpc

app = FastAPI()

# gRPC порт логінгу
LOGGING_GRPC_HOST = "localhost:50051"
# HTTP для messages-service
MESSAGES_SERVICE_URL = "http://localhost:12002/"

MAX_RETRIES = 3
RETRY_DELAY = 1  # секунд

def send_to_logging_service_grpc(msg_id, msg):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with grpc.insecure_channel(LOGGING_GRPC_HOST) as channel:
                stub = logging_pb2_grpc.LoggingServiceStub(channel)
                request = logging_pb2.LogRequest(uuid=msg_id, msg=msg)
                response = stub.LogMessage(request)
                return response.status, attempt - 1
        except grpc.RpcError as e:
            print(f"[RETRY {attempt}] gRPC call failed: {e}")
            time.sleep(RETRY_DELAY)
    return "failed", MAX_RETRIES

@app.post("/")
async def post_message(request: Request):
    data = await request.json()
    msg = data.get("msg")
    if not msg:
        return {"error": "Message is required"}

    msg_id = str(uuid.uuid4())
    status, retries = send_to_logging_service_grpc(msg_id, msg)

    return {"uuid": msg_id, "status": status, "retries": retries}

@app.get("/")
def get_all_data():
    try:
        log_response = requests.get("http://localhost:12001/").json()
        msg_response = requests.get(MESSAGES_SERVICE_URL).json()
        return {
            "logs": log_response.get("messages", []),
            "msg": msg_response.get("message")
        }
    except Exception as e:
        return {"error": str(e)}


