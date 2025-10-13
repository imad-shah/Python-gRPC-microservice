from handler import LibraryHandler
from controller import Library
from repository import BookRepository, connect_sqldb, connect_mongodb

from proto import library_pb2, library_pb2_grpc
import grpc
from concurrent import futures
import time
from grpc_reflection.v1alpha import reflection

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sql_connection = connect_sqldb()
    mongo_connection = connect_mongodb()
    book_repository = BookRepository(sql_connection, mongo_connection)
    library = Library(book_repository)
    library_pb2_grpc.add_LibraryServicer_to_server(LibraryHandler(library), server)
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