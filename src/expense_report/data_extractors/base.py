from abc import ABC, abstractmethod


class Extractor(ABC):
    @abstractmethod
    def to_data_frame(self):
        pass
