"""
Book mapper module for converting between domain models and protobuf messages.
"""
from proto import library_pb2
from models.book import Book


class BookMapper:

    @staticmethod
    def to_proto(book: Book) -> library_pb2.Book:
        return library_pb2.Book(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            copies_remaining=book.copies_remaining,
            total_copies=book.total_copies
        )

    @staticmethod
    def to_proto_list(books: list[Book]) -> list[library_pb2.Book]:
        return [BookMapper.to_proto(book) for book in books]