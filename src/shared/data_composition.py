from src.shared.data_models import Data, Metadata, GoldData
from src.shared.exceptions import WrongInputError
from src.shared.zeropoint_container import ZeropointContainer
from src.shared.violation import Violation


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
        self._metadata = metadata
        
    def set_medallion_data(self, medallionData: dict[str,Data]):
        if len(medallionData)!= 3:
            raise WrongInputError(f"Dictionary for the method set_medallion_data hat a length of {len(medallionData)} instead of 3.")
        
        requiredKeys = {'bronze', 'silver', 'gold'}
        if requiredKeys != medallionData.keys():
            raise WrongInputError("The Dictionary has keys than expected")
        
        else:
            self._medallionData = medallionData
          
    def set_zeropoint_container(self, zeropoints: ZeropointContainer):
        self._zeropoints = zeropoints
                
    def get_medallion_data(self) ->dict[str,Data]:
        return self._medallionData
           
    def get_metadata(self) -> Metadata:
        return self._metadata
    
    def get_zeropoint_container(self) -> ZeropointContainer:
        return self._zeropoints
    
    def set_final_gold_object(self, gold: Data):
        pass