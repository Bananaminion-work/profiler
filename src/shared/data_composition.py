from src.shared.data_models import Data, Metadata, GoldData
from src.shared.exceptions import WrongInputError
from src.shared.zeropoint_container import ZeropointContainer
from src.shared.violation import Violation


class DataComposition:
    
    _metadata : Metadata
    _medallionData : dict[str,Data]
    _zeropoints : ZeropointContainer
    _violations : dict[str, Violation]
    
    def __init__(self):
        self._metadata = Metadata()
        self._medallionData = dict[str,Data]()
        self._zeropoints = ZeropointContainer()
        self._violations = dict[str, Violation]()
        
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
        
    def set_violations(self, violations: dict[str, Violation]):
        self._violations = violations
          
          
                
    def get_medallion_data(self) ->dict[str,Data]:
        return self._medallionData
           
    def get_metadata(self) -> Metadata:
        return self._metadata
    
    def get_zeropoint_container(self) -> ZeropointContainer:
        return self._zeropoints
    
    def get_violations(self) -> dict[str, Violation]:
        return self._violations
    
    
    
    
    def set_final_gold_object(self, gold: Data):
        pass