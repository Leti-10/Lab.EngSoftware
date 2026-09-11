from abc import ABC, abstractmethod


class BookRepository(ABC):
    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def create(self, entity):
        pass

    @abstractmethod
    def update(self, id, entity):
        pass

    @abstractmethod
    def delete(self, id):
        pass
