from proto.library_pb2_grpc import LibraryServicer

class LibraryServicer(LibraryServicer):
    # Fetch name, return books
    def GetBooks():
        ...

    def GetInventorySummary():
        ...

    def GetBookCount():
        ...


    def CheckoutBook():
        ...


    def ReturnBook():
        ...
