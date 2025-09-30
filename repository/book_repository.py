from abc import ABC, abstractmethod
import collections

from models import Book

INSERT_QUERY = 'insert into books (isbn,title,author,copies_remaining,total_copies) values (%s,%s,%s,%s,%s)'
UPDATE_QUERY = 'update books set isbn=%s,title=%s,author=%s,copies_remaining=%s,total_copies=%s where isbn=%s'
GET_QUERY = 'select isbn, title, author, copies_remaining, total_copies from books where isbn=%s'
DELETE_QUERY = 'delete from books where isbn=%s'

class IBookRepository(ABC):


    @abstractmethod
    def GetBook(self, isbn: int) -> Book | None:
        pass

    @abstractmethod
    def GetBooksFromPatron(self, id : int) -> list[int]:
        pass

    @abstractmethod
    def GetInventorySummary(self) -> list[Book]:
        pass

    @abstractmethod
    def GetBookCount(self, isbn: int) -> int:
        pass
    
    @abstractmethod
    def GetTotalCopies(self, isbn: int) -> int:
        pass

    @abstractmethod
    def IncrementCopies(self, isbn : int) -> None:
        pass

    @abstractmethod
    def DecrementCopies(self, isbn : int) -> None:
        pass
    
    @abstractmethod
    def AddBookToPatron(self, patron : int, isbn : int) -> None:
        pass

    @abstractmethod
    def RemoveBookFromPatron(self, patron : int, isbn: int) -> None:
        pass

    @abstractmethod
    def CreatePatron(self, patron: str):
        pass

    @abstractmethod
    def GetBookById(self, isbn : int) -> Book:
        pass
   
    @abstractmethod
    def DeleteBookByIsbn(self, isbn : int) -> bool:
        pass

class BookRepository(IBookRepository):
    def __init__(self, sqldb, mongodb):
        self._sqldb = sqldb
        self._mongodb = mongodb


    def GetBook(self, isbn: int) -> Book | None:
        cursor = self._sqldb.cursor()
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetch_one()
        if not row:
            return None
        return Book(*row)

    def GetBooksFromPatron(self, id: int) -> list[int]:
        doc = self._mongodb.find({'id' : id})
        if doc:
            books = doc['books']
            if books:
                return books
            else:
                print('No books checked out')
        else:
            print('Patron not found')
        return []

    def GetInventorySummary(self) -> list[Book]:
        cursor = self._sqldb.cursor()
        cursor.execute(GET_QUERY)
        rows = cursor.fetchall()
        return [Book(isbn, title, author, copies_remaining, total_copies) for isbn, title, author, copies_remaining, total_copies in rows]

    def GetBookCount(self, isbn: int) -> int:
        cursor = self._sqldb.cursor(dictionary = True)
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetch_one()
        return row['copies_remaining']

    def GetTotalCopies(self, isbn: int) -> int:
        cursor = self._sqldb.cursor(dictionary = True)
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetch_one()
        return row['total_copies']

    def IncrementCopies(self, isbn : int) -> None:
        cursor = self._sqldb.cursor()
        cursor.execute('UPDATE Books SET copies_remaining = copies_remaining + 1 WHERE isbn = %s', (isbn,))
        self._sqldb.commit()
        return None

    def DecrementCopies(self, isbn : int) -> None:
        cursor = self._sqldb.cursor()
        cursor.execute('UPDATE Books SET copies_remaining = copies_remaining - 1 WHERE isbn = %s', (isbn,))
        self._sqldb.commit()
        return None
    
    def AddBookToPatron(self, patron: int, isbn: int) -> None:
        self._mongodb.update_one(
                {"id": patron},
                {"$push": {"books": isbn}}
                )
    
    def RemoveBookFromPatron(self, patron: int, isbn: int) -> None:
        self._mongodb.update_one(
                {"id": patron},
                {"$pull": {"books": isbn}}
                )

    def CreatePatron(self, patron: str):
        last_id = self._mongodb.find_one().sort({"ID"}, -1)
        insert = {'id' : last_id + 1, 'name' : patron, 'books' : []}
        self._mongodb.insert_one(insert)
    
    def GetBookById(self, isbn: int) -> Book:
        cursor = self._sqldb.cursor()
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetch_one()
        return Book(*row)

    def DeleteBookByIsbn(self, isbn: int) -> bool:
        cursor = self._sqldb.cursor()
        cursor.execute(DELETE_QUERY, (isbn,))
        self._sqldb.commit()
        return True

