import grpc
from concurrent import futures
import logging_pb2
import logging_pb2_grpc

storage = {}

class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        if request.uuid in storage:
            print(f"[DUPLICATE] UUID {request.uuid} already exists. Skipping.")
            return logging_pb2.LogResponse(status="duplicate")
        storage[request.uuid] = request.msg
        print(f"[LOGGING SERVICE] Logged: {request.uuid} -> {request.msg}")
        return logging_pb2.LogResponse(status="ok")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

