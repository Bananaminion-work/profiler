from src.shared.zeropoint_names import ZeropointNames

class ZeropointContainer:
    """class that works as a container for the zeropoints
    
    add a name here in self.zeropoints as well as in zeropoint_names.py to add a new zeropoint"""
    
    zeropoints:dict[str,int]
    
    def __init__(self):
        
        self.zeropoints = {
            ZeropointNames.NONE: 0,
            ZeropointNames.INLET_BULKHEAD: 0,
            ZeropointNames.OUTLET_BULKHEAD: 0,
            ZeropointNames.FIRST_INJECTION: 0,
            ZeropointNames.ABOVE_235: 0,
            ZeropointNames.VENTILATE_2: 0,
        }
        
    def set(self, name:str, offset:int):
        """use Names defined in ZeropointNames to set the offset for a zeropoint"""
        self.zeropoints[name] = offset
        
    def get(self, name:str) -> int:
        """use Names defined in ZeropointNames to get the offset for a zeropoint"""
        return self.zeropoints.get(name, 0)
    
    def get_zeropoints(self) -> dict[str,int]:
        """returns a dict of all zeropoints and their offsets"""
        return self.zeropoints