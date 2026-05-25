from nicegui import ui
from pandas import DataFrame
from src.shared.exceptions import CalculationError
from src.shared.zeropoint_container import ZeropointContainer


class ZeropointCalculator:
    
    df : DataFrame
    zeros : ZeropointContainer
    
    def __init__(self):
        self.zeros = ZeropointContainer()
        self.df = DataFrame()
    
    def calculate_zeropoints(self, df: DataFrame):
        
        # set dataframe globally to access it in other methods
        self.df = df
        
        # calc and set bulkhead-zeropoint
        self.zeros.set_bulkhead(self.caclulate_bulkhead_zeropoint())
        self.zeros.set_first_injection(self.calculate_first_injection_zeropoint())
        self.zeros.set_above235(self.calculate_above235_zeropoint())
        self.zeros.set_ventilate2(self.calculate_ventilate2_zeropoint())
        
        return self.zeros
    
    
    
    def caclulate_bulkhead_zeropoint(self)->int:
        
        """calculates the offset to ReadTime of the last found row where bulkhead is 1, searching only in the first 300 rows"""
        
        # only the first 300 rows + reset index to directly access the offset of the zeropoint
        dfBefore300 = self.df.iloc[:300].reset_index(drop=True)

        # save rows there bulkhead is 1
        foundRows = dfBefore300[dfBefore300["PrcChbInletBulkheadOpen"] == 1]
        
        # if no rows found, raise error
        if foundRows.empty:
            ui.notify("No Bulkhead-zeropoint was found")
            return 0
        
        # return the offset of the last found row as int
        return int(foundRows.index[len(foundRows)-1])
    
    
    
    def calculate_first_injection_zeropoint(self):
        
        """calculates the offset to ReadTime of the first injection from the 10. row onwards, where St_MediumPump is 1"""
        
        rowOffset = 10
        
        dfSection = self.df.iloc[rowOffset:].reset_index(drop=True)
        foundRows = dfSection[dfSection["St_MediumPump"] == 1]
        
        if foundRows.empty:
            ui.notify("No first injection zeropoint was found")
            return 0
        
        return int(foundRows.index[0]+rowOffset)
    
    
    
    def calculate_above235_zeropoint(self):
        """calculates tho offset to ReadTime of the first row where temperature (CH1) is above 235°C"""
        
        # take all rows + reset index to directly access the offset of the zeropoint
        dfSelection = self.df.reset_index(drop=True)
        foundRows = dfSelection[dfSelection["CH1"] > 235]
        
        
        if foundRows.empty:
            ui.notify("No zeropoint above 235°C was found")
            return 0

        return int(foundRows.index[0])
    
    
    
    def calculate_ventilate2_zeropoint(self):
        """calculates the offset to ReadTime of the last entry where ventilation is done
        (pressure-gradient of the last 5 entries averaged <30) 
        and actual gradient is < 10 while CH1 is over 205°C"""
        
        # copy whole dataframe, access index directly as numeric offset
        dfSelection = self.df.reset_index(drop=True)
        
        # calculate rolling mean for pressure
        rollingMean = dfSelection['VacuumActualV in mBar'].diff().rolling(5).mean()
        
        # append rollingMean to dataframe for filtering
        dfSelection['RollingMean'] = rollingMean
        
        # search for rows 
        foundRows = dfSelection[
            (dfSelection['CH1'] > 205) &
            (dfSelection['VacuumActualV in mBar'] < 50) &
            (dfSelection['RollingMean'] < 30)
        ]
        
        if foundRows.empty:
            ui.notify("No ventilate2 zeropoint was found")
            return 0
        
        #return first found row
        return int(foundRows.index[0])