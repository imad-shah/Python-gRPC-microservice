from proto.library_pb2_grpc import LibraryServicer

class LibraryServicer(LibraryServicer):
    # Fetch name, return books
    def GetBooks(name:str):
        ...


    def GetInventorySummary():
        ...
    def GetBookCount():
        ...