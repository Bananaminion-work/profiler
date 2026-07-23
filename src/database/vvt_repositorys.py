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
    
    #def _initialize_vvt_table(self):
    #    
    #    #create query
    #    query = f"""
    #    CREATE TABLE IF NOT EXISTS {self._vvtTable} (
    #        vvt_name STRING,
    #        rule_id STRING,
    #        rule_name STRING,
    #        channel STRING,
    #        condition STRING,
    #        threshold DOUBLE,
    #        param1 DOUBLE,
    #        param2 DOUBLE,
    #        param3 DOUBLE,
    #        scope STRING
    #    )
    #    """        
    #    #execute query
    #    self.client.execute_query(query)
    #    
    #    #check if tables is empty, if yes, insert default vvt
    #    check_query = f"SELECT * FROM {self._vvtTable} LIMIT 1"
    #    checkDf = self.client.get_data(check_query)
    #    
    #    if checkDf.empty:
    #        
    #        # load default vvt from csv
    #        default_vvt_path = PROJECT_ROOT / "tests" / "fixtures" / "vvt_limits.csv"
    #        default_vvt_df = pd.read_csv(default_vvt_path)
    #        default_vvt_tuple = list(default_vvt_df.itertuples(index=False, name=None))
    #        
    #        # fill sql table with default vvt from csv file
    #        self.client.execute_batch_insert(self._vvtTable, default_vvt_tuple)
    #        
    #    #else:
    #    #    print(f"VVT table '{self._vvtTable}' already contains data. Skipping default VVT insertion.")
            
            