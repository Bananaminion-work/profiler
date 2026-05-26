class ZeropointContainer:
    
    zeropoints:dict[str,int]
    
    def __init__(self):
        self.zeropoints = {
            'none':0,
            'bulkhead':0,
            'first injection':0,
            'above 235':0,
            'ventilate 2':0
        }
        
    def set_bulkhead(self, bulkhead: int):
        self.zeropoints['bulkhead'] = bulkhead
        
    def set_first_injection(self, first_injection: int):
        self.zeropoints['first injection'] = first_injection
        
    def set_above235(self, above235: int):
        self.zeropoints['above 235'] = above235
        
    def set_ventilate2(self, ventilate2: int):
        self.zeropoints['ventilate 2'] = ventilate2
        
    def get_bulkheads(self) -> int:
        return self.zeropoints['bulkhead']

    def get_first_injection(self) -> int:
        return self.zeropoints['first injection']
    
    def get_above235(self) -> int:
        return self.zeropoints['above 235']
    
    def get_ventilate2(self) -> int:
        return self.zeropoints['ventilate 2']
    
    def get_zeropoints(self)-> dict[str,int]:
        return self.zeropoints