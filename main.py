from handler import LibraryServicer

from proto import library_pb2, library_pb2_grpc
import grpc
from concurrent import futures
import time
from grpc_reflection.v1alpha import reflection

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_LibraryServicer_to_server(LibraryServicer(), server)
    SERVICE_NAMES = (
        library_pb2.DESCRIPTOR.services_by_name['Library'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:50051')  
    server.start()
    print("gRPC server running on port 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()