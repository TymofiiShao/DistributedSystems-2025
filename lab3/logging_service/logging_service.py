import grpc
from concurrent import futures
import logging_pb2
import logging_pb2_grpc
from hazelcast_client_lib import log_map
import sys

# Клас сервісу
class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        if log_map.contains_key(request.uuid):
            print(f"[DUPLICATE] UUID {request.uuid} already exists.")
            return logging_pb2.LogResponse(status="duplicate")

        log_map.put(request.uuid, request.msg)
        print(f"[LOGGED] {request.uuid}: {request.msg}")
        return logging_pb2.LogResponse(status="success")

    def GetMessages(self, request, context):
        messages = log_map.values()
        print(f"[GET] Returning {len(messages)} messages")
        return logging_pb2.MessagesList(messages=messages)


# Запуск gRPC-сервера
def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[STARTED] Logging-service is running on port {port}")
    server.wait_for_termination()

# Головна точка входу
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide a port number: python logging_service.py 50051")
        sys.exit(1)

    port = sys.argv[1]
    serve(port)


