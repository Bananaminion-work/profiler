from pandas import DataFrame

from src.shared.data_composition import DataComposition
from src.shared.plot_presets import PlotPresets
from typing import cast

class DataStore:
    
    def __init__(self):
        self.current_import_measurement = DataComposition()
        self.current_gold_data_for_plot: dict[str, DataFrame] = {}
        self.current_gold_zeropoints = {}
        self.measurement_ids: set = set()
        self.measurement_name_mapping: dict[str,str] = {}
        
    ##### Attribute access #####
    
    
    ##### Methods #####
    
    def get_scoped_data_single(self, preset:str) -> DataFrame:
        """Return a DataFrame with the data for the given preset, or an empty DataFrame if no measurement is loaded"""
        
        # check if a measurement is loaded
        if self.current_import_measurement is None:
            return DataFrame()
        
        # get data
        df = self.current_import_measurement.get_gold_data()
        
        # get channels as preset
        channels = PlotPresets.get_preset(preset)
        
        # check if preset is valid
        if channels is None:
            return df
        
        # return only the columns in the preset
        validChannels = [col for col in channels if col in df.columns]
        
        return cast(DataFrame, df[validChannels])
    
    def get_scoped_data_multiple(self, preset:str)->dict[str, DataFrame]:
        
        # check if a measurement is loaded
        if self.current_gold_data_for_plot is None:
            return {}
        
        # get channels as preset
        channels = PlotPresets.get_preset(preset)
        
        # check if preset is valid
        if channels is None:
            return self.current_gold_data_for_plot
        
        scopedDict: dict[str, DataFrame] = {}
        
        # cast the dataframes to only the columns in the preset
        for key, df in self.current_gold_data_for_plot.items():
            validChannels = [col for col in channels if col in df.columns]
            scopedDict[key] = cast(DataFrame, df[validChannels])
            
        # return the dict with the scoped dataframes
        return scopedDict