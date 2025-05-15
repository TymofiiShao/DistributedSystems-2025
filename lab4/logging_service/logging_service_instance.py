import grpc
from concurrent import futures
import sys

import logging_pb2
import logging_pb2_grpc

from hazelcast_queue_lib import log_queue
  # окремо створений файл

PORT = sys.argv[1] if len(sys.argv) > 1 else "50051"

stored_messages = []

class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        entry = f"{request.uuid}: {request.msg}"
        log_queue.offer(entry)
        stored_messages.append(entry)  # ✅ Додаємо в локальний список
        print(f"[LOGGED] {entry}")
        return logging_pb2.LogResponse(status="success")

    def GetMessages(self, request, context):
        print(f"[GET] Returning {len(stored_messages)} messages")
        return logging_pb2.MessagesResponse(messages=stored_messages)  # ✅ Повертаємо з локального списку

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"[STARTED] Logging-service is running on port {PORT}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()




