from abc import ABC, abstractmethod

from models import Book
from repository import BookRepository

class ILibrary(ABC):
    
    @abstractmethod
    def ListBooks(self, limit: int) -> list[Book]:
        pass

    @abstractmethod
    def CheckoutBook(self, id : int, isbn : int) -> str:
        pass

    @abstractmethod
    def ReturnBook(self, id: int, isbn: int) -> str:
        pass

    @abstractmethod
    def DeleteBook(self, isbn: int) -> str:
        pass

class Library(ILibrary):

    def __init__(self, book_repository: BookRepository):
        self._book_repository = book_repository
 
    def ListBooks(self, limit : int) -> list[Book]:
        catalog = self._book_repository.GetInventorySummary()
        return catalog[:limit]

    def CheckoutBook(self, id : int, isbn : int) -> str:
        patrons_books = self._book_repository.GetBooksFromPatron(id)
        if isbn in patrons_books:
            return f'Error: Book({isbn}) already currently checked out'

        book_count = self._book_repository.GetBookCount(isbn)
        if book_count < 1:
            return 'Error: Book out of stock'

        self._book_repository.DecrementCopies(isbn)
        self._book_repository.AddBookToPatron(id, isbn)
        
        return f'Book {isbn} successfully removed to patron {id}'
    
    def ReturnBook(self, id : int, isbn : int) -> str:
        patrons_books = self._book_repository.GetBooksFromPatron(id)
        if isbn not in patrons_books:
            return f'Error: Book({isbn}) not currently checked out'

        book_count = self._book_repository.GetBookCount(isbn)
        if book_count >= self._book_repository.GetTotalCopies(isbn):
            return 'Error: Book Overflow'

        self._book_repository.IncrementCopies(isbn)
        self._book_repository.RemoveBookFromPatron(id, isbn)

        return f'Book {isbn} successfully removed to patron {id}'

    def DeleteBook(self, isbn: int) -> str:
        book = self._book_repository.GetBook(isbn)
        if not book:
            return f'Error: Book({isbn}) not found'
        self._book_repository.DeleteBookByIsbn(isbn)
        return f'Book({isbn}) deleted'



        


        

