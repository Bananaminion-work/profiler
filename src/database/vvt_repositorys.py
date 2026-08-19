from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame

from src.shared.table_names import TableNames

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



class VvtRepoCsv(VvtRepository):
    
    def __init__(self):
        """initializes the repository with the path to the csv file"""
        self._pathToCsv = PROJECT_ROOT / "tests" / "fixtures" / "vvt_limits.csv"
    
    def load_vvt(self) -> DataFrame:
        return pd.read_csv(self._pathToCsv)
    
    def add_vvt(self,df: DataFrame) -> None:
        pass
    
    def delete_vvt(self,name:str) -> None:
        pass
    
    
class VvtRepoDatabricks(VvtRepository):
    
    def __init__(self,databaseClient):
        self.client = databaseClient
        self._vvtTable = TableNames.VVT
    
    def load_vvt(self) -> DataFrame:
        query = f"SELECT * FROM {self._vvtTable}"
        return self.client.get_data(query)
        
    
    def add_vvt(self,df: DataFrame) -> None:
        pass
    
    def delete_vvt(self,name:str) -> None:
        pass
    
    
            
            