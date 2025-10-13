import grpc
from proto.library_pb2_grpc import LibraryServicer
from proto import library_pb2
from controller.library import Library
from mapper import BookMapper


class LibraryHandler(LibraryServicer):
    def __init__(self, library: Library):
        self.library = library

    def _find_book_by_title(self, title: str):
        """Helper method to find a book by title from inventory."""
        books = self.library._book_repository.GetInventorySummary()
        for book in books:
            if book.title == title:
                return book
        return None

    # What books are currently checked out
    # Finds a patron by ID, then returns their books from nosql mongodb
    def GetBooks(self, request, context):
        try:
            patron_id = request.patron_id
            patron_name = self.library._book_repository.GetPatronNameById(patron_id)

            if patron_name is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Patron with ID {patron_id} not found')
                return library_pb2.GetBooksResponse()

            isbns = self.library._book_repository.GetBooksFromPatron(patron_id)
            print(f"{patron_name}'s books -> {isbns}")

            return library_pb2.GetBooksResponse(isbns=isbns)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error retrieving books: {str(e)}')
            return library_pb2.GetBooksResponse()

    # Fetches all available data from sql database pertaining to library
    def GetInventorySummary(self, request, context):
        try:
            books = self.library._book_repository.GetInventorySummary()
            response_books = BookMapper.to_proto_list(books)
            return library_pb2.GetInventorySummaryResponse(books=response_books)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error retrieving inventory: {str(e)}')
            return library_pb2.GetInventorySummaryResponse()

    # How many of a certain book is remaining in the Library
    # Returns copies_remaining in sql db
    def GetBookCount(self, request, context):
        try:
            book_title = request.book
            book = self._find_book_by_title(book_title)

            if book:
                return library_pb2.GetBookCountResponse(
                    copies_remaining=book.copies_remaining
                )

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Book "{book_title}" not found')
            return library_pb2.GetBookCountResponse(copies_remaining=0)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Error retrieving book count: {str(e)}')
            return library_pb2.GetBookCountResponse(copies_remaining=0)

    # Checkout a book from mysql db, put it in the nosql db for each patron, return an error if 0 copies remaining in sql
    def CheckoutBook(self, request, context):
        try:
            patron_name = request.patron
            book_title = request.book

            book = self._find_book_by_title(book_title)

            if not book:
                return library_pb2.CheckoutBookResponse(
                    status=library_pb2.CheckoutBookResponse.NOT_FOUND,
                    message=f'Book "{book_title}" not found',
                    copies_remaining=0
                )
            patron_id = self.library._book_repository.GetPatronIdByName(patron_name)
            if patron_id is None:
                return library_pb2.CheckoutBookResponse(
                    status=library_pb2.CheckoutBookResponse.NOT_FOUND,
                    message=f'Patron "{patron_name}" not found',
                    copies_remaining=book.copies_remaining
                )

            if book.copies_remaining < 1:
                return library_pb2.CheckoutBookResponse(
                    status=library_pb2.CheckoutBookResponse.UNAVAILABLE,
                    message=f'No copies of "{book_title}" available',
                    copies_remaining=0
                )

            patron_books = self.library._book_repository.GetBooksFromPatron(patron_id)
            if book.isbn in patron_books:
                return library_pb2.CheckoutBookResponse(
                    status=library_pb2.CheckoutBookResponse.ALREADY_EXISTS,
                    message=f'Patron already has "{book_title}" checked out',
                    copies_remaining=book.copies_remaining
                )

            self.library._book_repository.DecrementCopies(book.isbn)
            self.library._book_repository.AddBookToPatron(patron_id, book.isbn)

            return library_pb2.CheckoutBookResponse(
                status=library_pb2.CheckoutBookResponse.OK,
                message=f'Successfully checked out "{book_title}"',
                copies_remaining=book.copies_remaining - 1
            )
        except Exception as e:
            return library_pb2.CheckoutBookResponse(
                status=library_pb2.CheckoutBookResponse.ERROR,
                message=f'Error checking out book: {str(e)}',
                copies_remaining=0
            )

    def ReturnBook(self, request, context):
        try:
            patron_name = request.patron
            book_title = request.book

            book = self._find_book_by_title(book_title)

            if not book:
                return library_pb2.ReturnBookResponse(
                    status=library_pb2.ReturnBookResponse.NOT_FOUND,
                    message=f'Book "{book_title}" not found',
                    copies_remaining=0
                )

            patron_id = self.library._book_repository.GetPatronIdByName(patron_name)
            if patron_id is None:
                return library_pb2.ReturnBookResponse(
                    status=library_pb2.ReturnBookResponse.NOT_FOUND,
                    message=f'Patron "{patron_name}" not found',
                    copies_remaining=book.copies_remaining
                )


            patron_books = self.library._book_repository.GetBooksFromPatron(patron_id)

            if book.isbn not in patron_books:
                return library_pb2.ReturnBookResponse(
                    status=library_pb2.ReturnBookResponse.NOT_FOUND,
                    message=f'Patron does not have "{book_title}" checked out',
                    copies_remaining=book.copies_remaining
                )


            self.library._book_repository.IncrementCopies(book.isbn)
            self.library._book_repository.RemoveBookFromPatron(patron_id, book.isbn)

            return library_pb2.ReturnBookResponse(
                status=library_pb2.ReturnBookResponse.OK,
                message=f'Successfully returned "{book_title}"',
                copies_remaining=book.copies_remaining + 1
            )
        except Exception as e:
            return library_pb2.ReturnBookResponse(
                status=library_pb2.ReturnBookResponse.ERROR,
                message=f'Error returning book: {str(e)}',
                copies_remaining=0
            )

    # Registering a new patron
    def RegisterPatron(self, request, context):
        try:
            patron_name = request.patron


            if self.library._book_repository.PatronExists(patron_name):
                return library_pb2.RegisterPatronResponse(
                    status=library_pb2.RegisterPatronResponse.ALREADY_EXISTS,
                    message=f'Patron "{patron_name}" already exists'
                )

            self.library._book_repository.CreatePatron(patron_name)

            return library_pb2.RegisterPatronResponse(
                status=library_pb2.RegisterPatronResponse.OK,
                message=f'Successfully registered patron "{patron_name}"'
            )
        except Exception as e:
            return library_pb2.RegisterPatronResponse(
                status=library_pb2.RegisterPatronResponse.ERROR,
                message=f'Error registering patron: {str(e)}'
            )