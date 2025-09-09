from proto import library_pb2, library_pb2_grpc
from pymongo import MongoClient, errors
import mysql.connector
import grpc

class LibraryServicer(library_pb2_grpc.LibraryServicer):
    def __init__(self):
      try:
        self.client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        self.client.admin.command("ping")
        print('MongoDB Connected')
        self.mongodb = self.client['library']
        self.collection = self.mongodb['patrons']
    
      except errors.PyMongoError as e:
         print(f'Mongo failed to connect: {e} \n')
         self.client = None
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
         print(f'MySQL failed to connect: {e}\n')
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
      book_list = []
      for b in books:
         if isinstance(b, dict):
            book_list.append(library_pb2.Book(
              author=b.get('author', ''),
              title=b.get('title', ''),
            ))
         elif isinstance(b, str):
            book_list.append(library_pb2.Book(
               author = '',
               title = b,
            ))
         else:
            continue
      return library_pb2.GetBooksResponse(books=book_list)


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
                  copies_remaining= b.get('copies_remaining', 0),
                  total_copies=b.get('total_copies', 0),
             ) 
             for b in books
          ]
       )
      
       

  # How many of a certain book is remaining in the Library
  # Returns copies_remaining in sql db
    def GetBookCount(self, request, context):
        title = request.book
        if not title:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'Book field must not be empty')
        cursor = self.sql.cursor(dictionary = True)
        cursor.execute(f"SELECT copies_remaining FROM Books WHERE title = %s", (title,))
        row = cursor.fetchone()
        if not row:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Book '{title}' not found")
        return library_pb2.GetBookCountResponse(copies_remaining=row["copies_remaining"])

  # Checkout a book from mysql db, put it in the nosql db for each patron, return an error if 0 copies remaining in sql
    def CheckoutBook(self, request, context):
      title = request.book
      patron = request.patron

      patron_doc = self.collection.find_one({"name": patron})
      if not patron_doc:
          context.abort(grpc.StatusCode.NOT_FOUND, f"Patron '{patron}' not found")
      
      current_books = patron_doc.get("books", [])
      for book in current_books:
          book_title = book.get("title", "") if isinstance(book, dict) else str(book)
          if book_title == title:
              context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Patron '{patron}' already has '{title}' checked out")

      cursor = self.sql.cursor(dictionary=True)
      cursor.execute("SELECT * FROM Books WHERE title = %s", (title,))
      row = cursor.fetchone()
      
      if not row:
          context.abort(grpc.StatusCode.NOT_FOUND, f"Book '{title}' not found")
      elif row["copies_remaining"] == 0:
          context.abort(grpc.StatusCode.UNAVAILABLE, f"No more copies remaining of {title}")
      else:
          cursor.execute(
              "UPDATE Books SET copies_remaining = copies_remaining - 1 WHERE title = %s",
              (title,)
          )
          self.sql.commit()
          
          book_data = {
              "title": row["title"],
              "author": row.get("author", ""),
              "isbn": row.get("ISBN", "")
          }
          
          self.collection.update_one(
              {"name": patron},
              {"$push": {"books": book_data}}
          )

          return library_pb2.CheckoutBookResponse(
              status=library_pb2.CheckoutBookResponse.OK,
              message=f"{title} has been checked out to {patron}"
          )
       
  # Opposite of checkout book
    def ReturnBook(self, request, context):
        title = request.book
        patron = request.patron


        patron_doc = self.collection.find_one({"name": patron})
        if not patron_doc:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Patron '{patron}' not found")

        current_books = patron_doc.get("books", [])
        book_found = None
        for book in current_books:
            book_title = book.get("title", "") if isinstance(book, dict) else str(book)
            if book_title == title:
                book_found = book
                break

        if not book_found:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Patron '{patron}' does not have '{title}' checked out")

        self.collection.update_one(
            {"name": patron},
            {"$pull": {"books": book_found}}
        )

        cursor = self.sql.cursor()
        cursor.execute("SELECT * FROM Books WHERE title = %s", (title,))
        row = cursor.fetchone()
        if not row:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Book '{title}' not found in inventory")

        cursor.execute(
            "UPDATE Books SET copies_remaining = copies_remaining + 1 WHERE title = %s",
            (title,)
        )
        self.sql.commit()

        return library_pb2.ReturnBookResponse(
            status=library_pb2.ReturnBookResponse.OK,
            message=f"{title} has been returned by {patron}"
        )

  # Registering a new patron

    def RegisterPatron(self, request, context):
        last = self.collection.find_one(sort=[("ID", -1)])
        new_id = int(last["ID"]) + 1 if last else 1
        
        
        new_patron = {
           "ID": f'{new_id:03d}',
           "name" : request.patron,
           "books": []
        }
        self.collection.insert_one(new_patron)
        return library_pb2.RegisterPatronResponse(
           status=library_pb2.RegisterPatronResponse.OK,
           message= f"Patron {request.patron} added!"
        )
        
    

