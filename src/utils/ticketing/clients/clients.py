from abc import ABC, abstractmethod


class BaseClient(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_ticket(self, external_id: str) -> dict:
        ...

    @abstractmethod
    def delete_ticket(self, external_id: str):
        ...
