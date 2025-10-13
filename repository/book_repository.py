from abc import ABC, abstractmethod
import collections

from models import Book

INSERT_QUERY = 'insert into Books (isbn,title,author,copies_remaining,total_copies) values (%s,%s,%s,%s,%s)'
UPDATE_QUERY = 'update Books set isbn=%s,title=%s,author=%s,copies_remaining=%s,total_copies=%s where isbn=%s'
GET_QUERY = 'select isbn, title, author, copies_remaining, total_copies from Books where isbn=%s'
DELETE_QUERY = 'delete from Books where isbn=%s'

class IBookRepository(ABC):


    @abstractmethod
    def GetBooks(self, isbn: str) -> Book | None:
        pass

    @abstractmethod
    def GetBooksFromPatron(self, id : int) -> list[str]:
        pass

    @abstractmethod
    def GetInventorySummary(self) -> list[Book]:
        pass

    @abstractmethod
    def GetBookCount(self, isbn: str) -> int:
        pass

    @abstractmethod
    def GetTotalCopies(self, isbn: str) -> int:
        pass

    @abstractmethod
    def IncrementCopies(self, isbn : str) -> None:
        pass

    @abstractmethod
    def DecrementCopies(self, isbn : str) -> None:
        pass

    @abstractmethod
    def AddBookToPatron(self, patron : int, isbn : str) -> None:
        pass

    @abstractmethod
    def RemoveBookFromPatron(self, patron : int, isbn: str) -> None:
        pass

    @abstractmethod
    def CreatePatron(self, patron: str):
        pass

    @abstractmethod
    def PatronExists(self, patron_name: str) -> bool:
        pass

    @abstractmethod
    def GetPatronIdByName(self, patron_name: str) -> int | None:
        pass

    @abstractmethod
    def GetPatronNameById(self, patron_id: int) -> str | None:
        pass

    @abstractmethod
    def GetBookById(self, isbn : str) -> Book:
        pass

    @abstractmethod
    def DeleteBookByIsbn(self, isbn : str) -> bool:
        pass

class BookRepository(IBookRepository):
    def __init__(self, sqldb, mongodb):
        self._sqldb = sqldb
        self._mongodb = mongodb


    def GetBooks(self, isbn: str) -> Book | None:
        cursor = self._sqldb.cursor()
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetchone()
        if not row:
            return None
        return Book(*row)

    def GetBooksFromPatron(self, id: int) -> list[str]:
        doc = self._mongodb.find_one({'id' : id})
        if doc:
            books = doc.get('books', [])
            if books:
                return books
            else:
                print('No books checked out')
        else:
            print('Patron not found')
        return []

    def GetInventorySummary(self) -> list[Book]:
        cursor = self._sqldb.cursor()
        cursor.execute('SELECT isbn, title, author, copies_remaining, total_copies FROM Books')
        rows = cursor.fetchall()
        return [Book(isbn, title, author, copies_remaining, total_copies) for isbn, title, author, copies_remaining, total_copies in rows]

    def GetBookCount(self, isbn: str) -> int:
        cursor = self._sqldb.cursor(dictionary = True)
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetchone()
        return row['copies_remaining']

    def GetTotalCopies(self, isbn: str) -> int:
        cursor = self._sqldb.cursor(dictionary = True)
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetchone()
        return row['total_copies']

    def IncrementCopies(self, isbn : str) -> None:
        cursor = self._sqldb.cursor()
        cursor.execute('UPDATE Books SET copies_remaining = copies_remaining + 1 WHERE isbn = %s', (isbn,))
        self._sqldb.commit()
        return None

    def DecrementCopies(self, isbn : str) -> None:
        cursor = self._sqldb.cursor()
        cursor.execute('UPDATE Books SET copies_remaining = copies_remaining - 1 WHERE isbn = %s', (isbn,))
        self._sqldb.commit()
        return None

    def AddBookToPatron(self, patron: int, isbn: str) -> None:
        self._mongodb.update_one(
                {"id": patron},
                {"$push": {"books": isbn}}
                )

    def RemoveBookFromPatron(self, patron: int, isbn: str) -> None:
        self._mongodb.update_one(
                {"id": patron},
                {"$pull": {"books": isbn}}
                )

    def CreatePatron(self, patron: str):
        last_patron = self._mongodb.find_one(sort=[("id", -1)])
        last_id = last_patron['id'] if last_patron else 0
        insert = {'id' : last_id + 1, 'name' : patron, 'books' : []}
        self._mongodb.insert_one(insert)

    def PatronExists(self, patron_name: str) -> bool:
        doc = self._mongodb.find_one({'name': patron_name})
        return doc is not None

    def GetPatronIdByName(self, patron_name: str) -> int | None:
        doc = self._mongodb.find_one({'name': patron_name})
        return doc['id'] if doc else None

    def GetPatronNameById(self, patron_id: int) -> str | None:
        doc = self._mongodb.find_one({'id': patron_id})
        return doc['name'] if doc else None

    def GetBookById(self, isbn: str) -> Book:
        cursor = self._sqldb.cursor()
        cursor.execute(GET_QUERY, (isbn,))
        row = cursor.fetchone()
        return Book(*row)

    def DeleteBookByIsbn(self, isbn: str) -> bool:
        cursor = self._sqldb.cursor()
        cursor.execute(DELETE_QUERY, (isbn,))
        self._sqldb.commit()
        return True

