from dataclasses import dataclass

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    copies_remaining: int
    total_copies: int

    def get_tuple(self):
        return self.isbn, self.title, self.author, self.copies_remaining, self.total_copies 
