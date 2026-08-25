from nicegui import ui
from pandas import DataFrame
from src.shared.channel_names import ChannelNames
from src.shared.zeropoint_container import ZeropointContainer
from src.shared.zeropoint_names import ZeropointNames


class ZeropointCalculator:
    
    df : DataFrame
    
    def __init__(self,warnings):
        self._warnings = warnings
        self.df = DataFrame()
    
    def calculate_zeropoints(self, df: DataFrame):
        
        # create new zeropointcontainer
        newZeros = ZeropointContainer()
        
        # set dataframe globally to access it in other methods
        self.df = df
        
        # calc and set bulkhead-zeropoint
        newZeros.set(ZeropointNames.INLET_BULKHEAD,self.caclulate_inlet_bulkhead_zeropoint())
        newZeros.set(ZeropointNames.OUTLET_BULKHEAD,self.caclulate_outlet_bulkhead_zeropoint())
        newZeros.set(ZeropointNames.FIRST_INJECTION,self.calculate_first_injection_zeropoint())
        newZeros.set(ZeropointNames.ABOVE_235,self.calculate_above235_zeropoint())
        newZeros.set(ZeropointNames.VENTILATE_2,self.calculate_vacuum_done_zeropoint())
        
        self.df = DataFrame() # reset dataframe to release memory
        
        return newZeros
    
    
    
    def caclulate_inlet_bulkhead_zeropoint(self)->int:
        
        """calculates the offset to ReadTime of the last found row where inlet bulkhead is 1, searching only in the first 300 rows"""
        
        # check if column is present in the dataframe and has values, else return 0
        if ChannelNames.INLET_BULKHEAD_OPEN not in self.df.columns or not self.df[ChannelNames.INLET_BULKHEAD_OPEN].any():
            self._warnings.warn("No inlet-bulkhead-zeropoint was found")
            return 0
        
        # only the first 300 rows + reset index to directly access the offset of the zeropoint
        dfBefore300 = self.df.iloc[:300].reset_index(drop=True).copy()

        # save rows there bulkhead is 1
        foundRows = dfBefore300[dfBefore300[ChannelNames.INLET_BULKHEAD_OPEN] == 1]
        
        # if no rows found, raise error
        if foundRows.empty:
            self._warnings.warn("No inlet-bulkhead-zeropoint was found")
            return 0
        
        # return the offset of the last found row as int
        return int(foundRows.index[len(foundRows)-1])
    
    
    
    def caclulate_outlet_bulkhead_zeropoint(self)->int:
        
        """calculates the offset to ReadTime of the last found row where outlet bulkhead is 1, searching only in the first 300 rows"""
        # check if column is present in the dataframe
        if ChannelNames.OUTLET_BULKHEAD_OPEN not in self.df.columns or not self.df[ChannelNames.OUTLET_BULKHEAD_OPEN].any():
            self._warnings.warn("No outlet-bulkhead-zeropoint was found")
            return 0
        
        # reset index to directly access the offset of the zeropoint
        df = self.df.reset_index(drop=True).copy()

        # save rows there bulkhead is 1
        foundRows = df[df[ChannelNames.OUTLET_BULKHEAD_OPEN] == 1]
        
        # if no rows found, raise error
        if foundRows.empty:
            self._warnings.warn("No outlet-bulkhead-zeropoint was found")
            return 0
        
        # return the offset of the last found row as int
        return int(foundRows.index[len(foundRows)-1])
    
    
    
    
    def calculate_first_injection_zeropoint(self):
        
        """calculates the offset to ReadTime of the first injection from the 10. row onwards, where St_MediumPump is 1"""
        
        if ChannelNames.MEDIUM_PUMP not in self.df.columns or not self.df[ChannelNames.MEDIUM_PUMP].any():
            self._warnings.warn("No first injection zeropoint was found")
            return 0
        
        rowOffset = 10
        
        # take all rows from the offset onwards and reset index to directly access the offset of the zeropoint
        dfSection = self.df.iloc[rowOffset:].reset_index(drop=True).copy()
        # save rows where St_MediumPump is 1, this indicates an injection
        foundRows = dfSection[dfSection[ChannelNames.MEDIUM_PUMP] == 1]
        
        if foundRows.empty:
            self._warnings.warn("No first injection zeropoint was found")
            return 0
        
        # take the first occurance and add the offset to get the correct offset to ReadTime
        return int(foundRows.index[0]+rowOffset)
    
    
    
    def calculate_above235_zeropoint(self):
        """calculates tho offset to ReadTime of the first row where temperature (CH1) is above 235°C"""
        
        if ChannelNames.CH1 not in self.df.columns or not self.df[ChannelNames.CH1].any():
            self._warnings.warn("No zeropoint above 235°C was found")
            return 0
        
        # take all rows + reset index to directly access the offset of the zeropoint
        dfSelection = self.df.reset_index(drop=True).copy()
        foundRows = dfSelection[dfSelection[ChannelNames.CH1] > 235]
        
        
        if foundRows.empty:
            self._warnings.warn("No zeropoint above 235°C was found")
            return 0

        return int(foundRows.index[0])
    
    
    
    def calculate_vacuum_done_zeropoint(self):
        """calculates the offset to ReadTime of the defined vacuum done - zeropoint"""
        
        
        minVacuum = 100
        tempThreshold = 205
        
        # check if necessary columns are present in the dataframe
        required_columns = [ChannelNames.CH1, ChannelNames.VACUUM]
        if not all(col in self.df.columns for col in required_columns):
            self._warnings.warn(f"Required columns for \"{ZeropointNames.VENTILATE_2}\" zeropoint calculation are missing in the dataframe.")
            return 0
        
        # copy df
        dfSelection = self.df.reset_index(drop=True).copy()
        
        # calc gradient
        dfSelection["gradient"] = dfSelection[ChannelNames.VACUUM].diff()
        
        # check if vacuum was below minimum and safe time index of first occurance
        dfSelection['MinVacuumHistory'] = dfSelection[ChannelNames.VACUUM].cummin()
        
        # scope the dataframe from the first row where CH1 is above 205°C
        dfSelection = dfSelection[dfSelection[ChannelNames.CH1] > tempThreshold]
        
        # create gradient with shift of 30
        dfSelection["gradient_max_30s"] = dfSelection["gradient"].rolling(window=30, min_periods=1).max()
        
        # check if gradient is static
        vacuumSettled = dfSelection["gradient"].abs() < 3
        
        foundRows = dfSelection[
            (dfSelection['MinVacuumHistory'] < minVacuum) &
            (dfSelection[ChannelNames.VACUUM] > 850)&
            (dfSelection["gradient_max_30s"].abs() > 30) &
            vacuumSettled
        ]
        
        if foundRows.empty:
            self._warnings.warn(f'No "{ZeropointNames.VENTILATE_2}" zeropoint was found')
            return 0
        
        return int(foundRows.index[0])