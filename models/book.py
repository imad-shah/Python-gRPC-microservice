from dataclasses import dataclass

@dataclass
class Book:
    author: str
    title: str
    isbn: int
    copies_remaining: int
    total_copies: int

    def get_tuple(self):
        return self.author, self.title, self.isbn, self.copies_remaining, self.total_copies 
