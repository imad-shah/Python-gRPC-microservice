from proto import library_pb2, library_pb2_grpc
from pymongo import MongoClient, errors
import mysql.connector
import grpc

class LibraryServicer(library_pb2_grpc.LibraryServicer):
    def __init__(self):
        self.mongoclient = MongoClient("mongodb://localhost:27017/")
        self.mongodb = self.mongoclient['library']
        self.mongotable = self.mongodb['patrons']
        self.mysql = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'password',
            database = 'my_database',
        )



  # What books are currently checked out
  # Finds a patron by name, then returns their books from nosql mongodb
    def GetBooks(self, request, context):
        patron = request.patron 

        query = {'name' : patron}
        doc = self.mongotable.find(query)
        




  # Fetches all available data from sql database pertaining to library
    def GetInventorySummary(self, request, context):
        cursor = self.mysql.cursor()
        cursor.execute('SELECT * FROM Books;')
        db = cursor.fetchall()
        cursor.close()

        books = []
        for row in db:
            book = library_pb2.Book(
                isbn = row[0],
                title = row[1],
                author = row[3],
                copies_remaining = row[3],
                total_copies = row[4],
            )
            books.append(book)
        
        return library_pb2.GetInventorySummaryResponse(
            books = books
        )

  # How many of a certain book is remaining in the Library
  # Returns copies_remaining in sql db
    def GetBookCount(self, request, context):
        pass


  # Checkout a book from mysql db, put it in the nosql db for each patron, return an error if 0 copies remaining in sql
    def CheckoutBook(self, request, context):
        pass

       
  # Opposite of checkout book
    def ReturnBook(self, request, context):
        pass

  # Registering a new patron
    def RegisterPatron(self, request, context):
        pass

        
    

