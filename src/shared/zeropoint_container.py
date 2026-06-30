from src.shared.zeropoint_names import ZeropointNames

class ZeropointContainer:
    
    zeropoints:dict[str,int]
    
    def __init__(self):
        self.zeropoints = {
            ZeropointNames.NONE: 0,
            ZeropointNames.INLET_BULKHEAD: 0,
            ZeropointNames.OUTLET_BULKHEAD: 0,
            ZeropointNames.FIRST_INJECTION: 0,
            ZeropointNames.ABOVE_235: 0,
            ZeropointNames.VENTILATE_2: 0
        }
        
    def set_inlet_bulkhead(self, bulkhead: int):
        self.zeropoints[ZeropointNames.INLET_BULKHEAD] = bulkhead
        
    def set_outlet_bulkhead(self, outlet_bulkhead: int):
        self.zeropoints[ZeropointNames.OUTLET_BULKHEAD] = outlet_bulkhead
        
    def set_first_injection(self, first_injection: int):
        self.zeropoints[ZeropointNames.FIRST_INJECTION] = first_injection
        
    def set_above235(self, above235: int):
        self.zeropoints[ZeropointNames.ABOVE_235] = above235
        
    def set_ventilate2(self, ventilate2: int):
        self.zeropoints[ZeropointNames.VENTILATE_2] = ventilate2
        
    def get_inlet_bulkhead(self) -> int:
        return self.zeropoints[ZeropointNames.INLET_BULKHEAD]

    def get_first_injection(self) -> int:
        return self.zeropoints[ZeropointNames.FIRST_INJECTION]
    
    def get_above235(self) -> int:
        return self.zeropoints[ZeropointNames.ABOVE_235]
    
    def get_ventilate2(self) -> int:
        return self.zeropoints[ZeropointNames.VENTILATE_2]
    
    def get_zeropoints(self)-> dict[str,int]:
        return self.zeropoints