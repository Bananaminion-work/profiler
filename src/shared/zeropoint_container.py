class ZeropointContainer:
    
    zeropoints:dict[str,int]
    
    def __init__(self):
        self.zeropoints = {
            'bulkhead':0,
            'first_injection':0,
            'above235':0,
            'ventilate2':0
        }
        
    def set_bulkhead(self, bulkhead: int):
        self.zeropoints['bulkhead'] = bulkhead
        
    def set_first_injection(self, first_injection: int):
        self.zeropoints['first_injection'] = first_injection
        
    def set_above235(self, above235: int):
        self.zeropoints['above235'] = above235
        
    def set_ventilate2(self, ventilate2: int):
        self.zeropoints['ventilate2'] = ventilate2
        
    def get_bulkheads(self) -> int:
        return self.zeropoints['bulkhead']

    def get_first_injection(self) -> int:
        return self.zeropoints['first_injection']
    
    def get_above235(self) -> int:
        return self.zeropoints['above235']
    
    def get_ventilate2(self) -> int:
        return self.zeropoints['ventilate2']
    
    def get_zeropoints(self)-> dict[str,int]:
        return self.zeropoints