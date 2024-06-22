from abc import ABC, abstractmethod


class Extractor(ABC):
    """
    This is the data file extractor base class. An extractor is responsible to extract
    the data from one file of a certain type of account
    """

    @abstractmethod
    def to_data_frame(self):
        pass
