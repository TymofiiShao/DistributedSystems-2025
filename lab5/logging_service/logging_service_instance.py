from concurrent import futures
import grpc
from flask import Flask
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from consul_register import register_service
from logging_service import logging_pb2, logging_pb2_grpc

storage = {}

class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        if request.uuid in storage:
            print(f"[DUPLICATE] UUID {request.uuid} already exists. Skipping.")
            return logging_pb2.LogResponse(status="duplicate")
        storage[request.uuid] = request.msg
        print(f"[LOG] {request.uuid}: {request.msg}")
        return logging_pb2.LogResponse(status="ok")

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

def run_health_check_server():
    app.run(host="0.0.0.0", port=5051)

# gRPC сервер
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    print("[LOGGING SERVICE] gRPC server started on port 5001")
    server.wait_for_termination()

# Запуск
if __name__ == "__main__":
    threading.Thread(target=run_health_check_server, daemon=True).start()
    register_service("logging-service", "logging-5001", port=5001, check_path="/health", health_port=5051)
    serve()




