from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class VvtRepository(ABC):
    @abstractmethod
    def load_vvt(self)-> DataFrame:
        pass

    @abstractmethod
    def add_vvt(self, df: DataFrame) -> None:
        pass
    
    @abstractmethod
    def delete_vvt(self,name:str) -> None:
        pass



class CsvRepository(VvtRepository):
    
    def __init__(self):
        """initializes the repository with the path to the csv file"""
        self._pathToCsv = PROJECT_ROOT / "tests" / "fixtures" / "vvt_limits.csv"
    
    def load_vvt(self) -> DataFrame:
        return pd.read_csv(self._pathToCsv)
    
    def add_vvt(self,df: DataFrame) -> None:
        pass
    
    def delete_vvt(self,name:str) -> None:
        pass
    
    
class DatabricksRepository(VvtRepository):
    
    def __init__(self):
        pass
    
    def load_vvt(self) -> DataFrame:
        return pd.DataFrame()
    
    def add_vvt(self,df: DataFrame) -> None:
        pass
    
    def delete_vvt(self,name:str) -> None:
        pass