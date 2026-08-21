from src.shared.data_models import Data, Metadata
from src.shared.exceptions import WrongInputError
from src.shared.zeropoint_container import ZeropointContainer
from pandas import DataFrame


class DataComposition:
    """this class contains a Metadata-objet, the medallion-data-objects and the zeropoints (either calculated or loaded from the database)"""
    _metadata : Metadata
    _medallionData : dict[str,Data]
    _zeropoints : ZeropointContainer
    
    def __init__(self):
        self._metadata = Metadata()
        self._medallionData = dict[str,Data]()
        self._zeropoints = ZeropointContainer()
        
    def set_metadata(self, metadata: Metadata):
        """sets the metadata object of the DataComposition"""
        self._metadata = metadata
        
    def set_medallion_data(self, medallionData: dict[str,Data]):
        """sets the medallion data dictionary of the DataComposition"""
        if len(medallionData)!= 3:
            raise WrongInputError(f"Dictionary for the method set_medallion_data hat a length of {len(medallionData)} instead of 3.")
        
        requiredKeys = {'bronze', 'silver', 'gold'}
        if requiredKeys != medallionData.keys():
            raise WrongInputError(f"Expected keys {requiredKeys} for the method set_medallion_data but got {medallionData.keys()}.")
        
        else:
            self._medallionData = medallionData
          
    def set_zeropoint_container(self, zeropoints: ZeropointContainer):
        """sets the zeropoint container of the DataComposition"""
        self._zeropoints = zeropoints
                
    def get_medallion_data(self) ->dict[str,Data]:
        """returns the medallion data dictionary of the DataComposition"""
        return self._medallionData
           
    def get_metadata(self) -> Metadata:
        """returns the metadata object of the DataComposition"""
        return self._metadata
    
    def get_zeropoint_container(self) -> ZeropointContainer:
        """returns the zeropoint container of the DataComposition"""
        return self._zeropoints
    
    def get_gold_data(self) -> DataFrame:
        """returns the gold data as a DataFrame"""
        return self._medallionData["gold"].get_dataframe()