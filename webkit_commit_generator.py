from abc import ABC, abstractmethod


class WebKitCommitGenerator(ABC):
    def __init__(self, max_date: str):
        self._max_date = max_date

    @abstractmethod
    def __iter__(self):
        pass

