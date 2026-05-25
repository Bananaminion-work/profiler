#from __future__ import annotations

from abc import ABC, abstractmethod
from src.shared.metadata import Metadata
from src.shared.exceptions import WrongInputError
from pandas import DataFrame

class Data(ABC):
    """
    abstract base class for medallion objects
    """
    
    @abstractmethod
    def set_dataframe(self, df: DataFrame):
        pass
    
    @abstractmethod
    def get_dataframe(self) -> DataFrame:
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        pass



class BronzeData(Data):
    
    typeString = "BronzeData"
    
    def __init__(self, bronzeValues: DataFrame):
        self.set_dataframe(bronzeValues)
        
      
    def set_dataframe(self, df: DataFrame):
        self.bronzeValues = df
        
    def get_dataframe(self) -> DataFrame:
        return self.bronzeValues
    
    def get_type(self) -> str:
        return self.typeString
                    
                    
                    
class SilverData(Data):
    
    typeString = "SilverData"
    
    def __init__(self, silverValues: DataFrame):
        self.set_dataframe(silverValues)
        
      
    def set_dataframe(self, df: DataFrame):
        self.silverValues = df
        
    def get_dataframe(self) -> DataFrame:
        return self.silverValues
    
    def get_type(self) -> str:
        return self.typeString



class GoldData(Data):
       
    typeString = "GoldData"
    
    def __init__(self, goldValues: DataFrame):
        self.set_dataframe(goldValues)
        
      
    def set_dataframe(self, df: DataFrame):
        self.goldValues = df
        
    def get_dataframe(self) -> DataFrame:
        return self.goldValues
    
    def get_type(self) -> str:
        return self.typeString


