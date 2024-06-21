from abc import abstractmethod


class Extractor:
    @abstractmethod
    def to_data_frame(self):
        pass
