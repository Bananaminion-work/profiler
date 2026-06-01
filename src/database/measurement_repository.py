from pandas import DataFrame
from src.shared.data_models import Data
from pathlib import Path

from src.shared.exceptions import WrongInputError

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class MeasurementRepository:
    """
    Repository for storing and managing measurements.
    """
    def __init__(self):
        self._measurements = []
    
    def add_measurement(self,measurement_id: str, measurement: dict[str,Data]):
        pass
    
    def get_measurements(self):
        return self._measurements
    
    
    
class MeasurementRepoCsv(MeasurementRepository):
    def __init__(self):
        super().__init__()
        self._bronzePath = PROJECT_ROOT / "tests" / "fixtures" / "vps_bronze_data.csv"
        self._silverPath = PROJECT_ROOT / "tests" / "fixtures" / "vps_silver_data.csv"
        self._goldPath = PROJECT_ROOT / "tests" / "fixtures" / "vps_gold_data.csv"
    
    def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
        """adds a measurement to the database (csv-files)"""
        
        
        # get medallion-data-objects
        bronze = measurement.get("bronze")
        silver = measurement.get("silver")
        gold = measurement.get("gold")
        
        if isinstance(bronze, Data) and isinstance(silver, Data) and isinstance(gold, Data):
            # get Dataframes from medallion-data-objects
            bronzeDf = bronze.get_dataframe()
            silverDf = silver.get_dataframe()
            goldDf = gold.get_dataframe()
        
            # set measurement_id as index for all dataframes
            bronzeDf['measurement_id'] = measurement_id
            silverDf['measurement_id'] = measurement_id
            goldDf['measurement_id'] = measurement_id
            
            # cretae long format Df for meallion data
            longBronzeDf = bronzeDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="variable", value_name="value")
            longSilverDf = silverDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="variable", value_name="value")
            longGoldDf = goldDf.reset_index().melt(id_vars=['measurement_id','ReadTime'], var_name="variable", value_name="value")
            
            # save longs to csv
            if self._bronzePath.exists() and self._silverPath.exists() and self._goldPath.exists():
                longBronzeDf.to_csv(self._bronzePath, mode='a', header=False, index=False)
                longSilverDf.to_csv(self._silverPath, mode='a', header=False, index=False)
                longGoldDf.to_csv(self._goldPath, mode='a', header=False, index=False)
                
            else:
                raise FileNotFoundError("One or more of the csv files for storing measurements do not exist.")
            
        else:
            raise WrongInputError("Measurement Data are none of type Data. Cannot add measurement to database.")
        
        

class MeasurementRepoDatabricks(MeasurementRepository):
    def __init__(self):
        super().__init__()
    
    def add_measurement(self, measurement_id: str, measurement: dict[str,Data]):
        pass