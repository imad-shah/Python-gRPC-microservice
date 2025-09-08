from proto import library_pb2, library_pb2_grpc
from pymongo import MongoClient
import mysql.connector
import grpc

class LibraryServicer(library_pb2_grpc.LibraryServicer):
    def __init__(self):
      self.client = MongoClient('mongodb://localhost:27017/')
      self.mongodb = self.client['library']
      self.collection = self.mongodb['patrons']
      try:
         self.sql = mysql.connector.connect(
            host = '127.0.0.1',
            port = 3306,
            user = 'root',
            password = 'password',
            database = 'my_database',
         )
         if self.sql.is_connected():
            print('MySQL Connected')
      except mysql.connector.Error as e:
         print(f'MySQL failed to connect: {e}')
         self.sql = None

  # What books are currently checked out
  # Finds a patron by name, then returns their books from nosql mongodb
    def GetBooks(self, request, context):
      patron = request.patron
      if not patron:
          context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'Patron field must not be empty')
      doc = self.collection.find_one({"name": patron})
      if not doc:
          context.abort(grpc.StatusCode.NOT_FOUND, f"Patron '{patron}' not found")
      books = doc.get("books", [])
      return library_pb2.GetBooksResponse(
          books = [
              library_pb2.Book(
                  author=b.get('author', ''),
                  title=b.get('title', ''),
              ) 
              for b in books
          ]
      )


  # Fetches all available data from sql database pertaining to library
    def GetInventorySummary(self, request, context):
       cursor = self.sql.cursor(dictionary=True)
       cursor.execute("SELECT * FROM Books;")
       books = cursor.fetchall()
       return library_pb2.GetInventorySummaryResponse(
          books = [
             library_pb2.Book(
                  isbn=b.get('ISBN', ''),
                  title=b.get('title', ''),
                  author=b.get('author', ''),
                  copies_remaining=b.get('copies_remaining', 0),
                  total_copies=b.get('total_copies', 0),
             ) 
             for b in books
          ]
       )
      
       

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
    
