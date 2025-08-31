from proto import library_pb2, library_pb2_grpc
from pymongo import MongoClient

class LibraryServicer(library_pb2_grpc.LibraryServicer):
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['mongo-db']
        self.collection = self.db['patrons']
  # What books are currently checked out
  # Finds a patron by name, then returns their books from nosql mongodb
    def GetBooks(self, request, context):
        patron = request.patron
        doc = self.collection.find_one({"name": patron})
        if not doc:
            return library_pb2.GetBooksResponse(books=[])
        books = doc.get("books", [])
        return library_pb2.GetBooksResponse(
            books = [
                library_pb2.Book(
                    author=b.get('author', ''),
                    title=b.get('title', ''),
                    isbn=b.get('isbn', ''),
                ) for b in books
            ]
        )


  # Fetches all available data from sql database pertaining to library
    def GetInventorySummary():
        ...

  # How many of a certain book is remaining in the Library
  # Returns copies_remaining in sql db
    def GetBookCount():
        ...

  # Checkout a book from mysql db, put it in the nosql db for each patron, return an error if 0 copies remaining in sql
    def CheckoutBook():
        ...

  # Opposite of checkout book
    def ReturnBook():
        ...

  # Registering a new patron

    def RegisterPatron():
        ...
    
