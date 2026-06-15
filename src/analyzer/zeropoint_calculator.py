from nicegui import ui
from pandas import DataFrame
from src.shared.channel_names import ChannelNames
from src.shared.zeropoint_container import ZeropointContainer


class ZeropointCalculator:
    
    df : DataFrame
    zeros : ZeropointContainer
    
    def __init__(self):
        self.df = DataFrame()
    
    def calculate_zeropoints(self, df: DataFrame):
        
        # create new zeropointcontainer
        newZeros = ZeropointContainer()
        
        # set dataframe globally to access it in other methods
        self.df = df
        
        # calc and set bulkhead-zeropoint
        newZeros.set_inlet_bulkhead(self.caclulate_inlet_bulkhead_zeropoint())
        newZeros.set_outlet_bulkhead(self.caclulate_outlet_bulkhead_zeropoint())
        newZeros.set_first_injection(self.calculate_first_injection_zeropoint())
        newZeros.set_above235(self.calculate_above235_zeropoint())
        newZeros.set_ventilate2(self.calculate_ventilate2_zeropoint())
        
        self.df = DataFrame() # reset dataframe to release memory
        
        return newZeros
    
    
    
    def caclulate_inlet_bulkhead_zeropoint(self)->int:
        
        """calculates the offset to ReadTime of the last found row where inlet bulkhead is 1, searching only in the first 300 rows"""
        
        # only the first 300 rows + reset index to directly access the offset of the zeropoint
        dfBefore300 = self.df.iloc[:300].reset_index(drop=True).copy()

        # save rows there bulkhead is 1
        foundRows = dfBefore300[dfBefore300[ChannelNames.INLET_BULKHEAD_OPEN] == 1]
        
        # if no rows found, raise error
        if foundRows.empty:
            ui.notify("No inlet-bulkhead-zeropoint was found")
            return 0
        
        # return the offset of the last found row as int
        return int(foundRows.index[len(foundRows)-1])
    
    
    
    def caclulate_outlet_bulkhead_zeropoint(self)->int:
        
        """calculates the offset to ReadTime of the last found row where outlet bulkhead is 1, searching only in the first 300 rows"""
        
        # reset index to directly access the offset of the zeropoint
        df = self.df.reset_index(drop=True).copy()

        # save rows there bulkhead is 1
        foundRows = df[df[ChannelNames.OUTLET_BULKHEAD_OPEN] == 1]
        
        # if no rows found, raise error
        if foundRows.empty:
            ui.notify("No outlet-bulkhead-zeropoint was found")
            return 0
        
        # return the offset of the last found row as int
        return int(foundRows.index[len(foundRows)-1])
    
    
    
    
    def calculate_first_injection_zeropoint(self):
        
        """calculates the offset to ReadTime of the first injection from the 10. row onwards, where St_MediumPump is 1"""
        
        rowOffset = 10
        
        # take all rows from the offset onwards and reset index to directly access the offset of the zeropoint
        dfSection = self.df.iloc[rowOffset:].reset_index(drop=True).copy()
        # save rows where St_MediumPump is 1, this indicates an injection
        foundRows = dfSection[dfSection[ChannelNames.MEDIUM_PUMP] == 1]
        
        if foundRows.empty:
            ui.notify("No first injection zeropoint was found")
            return 0
        
        # take the first occurance and add the offset to get the correct offset to ReadTime
        return int(foundRows.index[0]+rowOffset)
    
    
    
    def calculate_above235_zeropoint(self):
        """calculates tho offset to ReadTime of the first row where temperature (CH1) is above 235°C"""
        
        # take all rows + reset index to directly access the offset of the zeropoint
        dfSelection = self.df.reset_index(drop=True).copy()
        foundRows = dfSelection[dfSelection[ChannelNames.CH1] > 235]
        
        
        if foundRows.empty:
            ui.notify("No zeropoint above 235°C was found")
            return 0

        return int(foundRows.index[0])
    
    
    ###### ALTE VARIANTE AUS EXCEL - PROBLEMATISCH
    def calculate_ventilate2_zeropoint_OLD(self):
        """"""
        
        minVacuum = 100
        edgeShift = 3
        
        # copy whole dataframe, access index directly as numeric offset
        dfSelection = self.df.reset_index(drop=True).copy()
        
        #calculate gradient
        dfSelection["gradient"] = dfSelection[ChannelNames.VACUUM].diff()
        
        # calculate rolling mean for pressure
        dfSelection['RollingMean'] = dfSelection[ChannelNames.VACUUM].diff().rolling(5).mean()        
        
        # check whether vaccum was at minVacuum before
        dfSelection['MinVacuumHistory'] = dfSelection[ChannelNames.VACUUM].cummin()
        
        # check whether the gradient was very high before
        dfSelection['MaxGradient'] = dfSelection['RollingMean'].cummax()
        
        # edge detection for rolling mean dependant on the edgeShift
        vacuumSettled = dfSelection["gradient"].abs() < 3
        
        # connect conditions
        foundRows = dfSelection[
            (dfSelection[ChannelNames.CH1] > 205) &
            (dfSelection["MinVacuumHistory"] < minVacuum) &
            (dfSelection["MaxGradient"] > 100 ) &
            vacuumSettled
        ]
        
        if foundRows.empty:
            ui.notify("No ventilate2 zeropoint was found")
            return 0
        
        #return first found row
        return int(foundRows.index[0])
    
    
    
    def calculate_ventilate2_zeropoint(self):
        """"""
        minVaccum = 100
        
        # copy df
        dfSelection = self.df.reset_index(drop=True).copy()
        
        # calc gradient
        dfSelection["gradient"] = dfSelection[ChannelNames.VACUUM].diff()
        
        # check whether vaccum was at minVacuum before
        dfSelection['MinVacuumHistory'] = dfSelection[ChannelNames.VACUUM].cummin()
        
        # check if vacuum is static
        vacuumSettled = dfSelection["gradient"].abs() < 3
        
        # merge conditions
        foundRows = dfSelection[
            (dfSelection[ChannelNames.CH1] > 205) &
            (dfSelection['MinVacuumHistory'] < minVaccum) &
            (dfSelection[ChannelNames.VACUUM]> 850) &
            vacuumSettled
        ]
        
        if foundRows.empty:
            ui.notify("No ventilate2 zeropoint was found")
            return 0
        
        return int(foundRows.index[0])