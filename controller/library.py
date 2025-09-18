from abc import ABC, abstractmethod
from types import MethodType

from models import Book
from repository import BookRepository

class ILibrary(ABC):
    
    @abstractmethod
    def GetBook(self, isbn: int) -> Book | None:
        pass

    @abstractmethod
    def ListBooks(self, limit: int) -> list[Book]:
        pass

    @abstractmethod
    def CheckoutBook(self, id : int, isbn : int) -> str:
        pass

    @abstractmethod
    def ReturnBook(self, id: int, isbn: int) -> Book | None:
        pass

    @abstractmethod
    def DeleteBook(self, isbn: int) -> Book | None:
        pass