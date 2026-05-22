# MUSS NOCH GELÖSCHT WERDEN; IST NUR FÜR TESTING DABEI !!!!!
from nicegui import ui

from pandas import DataFrame
import pandas as pd
from src.shared.data_models import GoldData, SilverData, Data
from src.shared.exceptions import WrongInputError

class GoldCreator():
    
    goldDf: DataFrame   
    
    def create_gold_object_multiple(self, silver: SilverData, source: str)->GoldData:
        
        # raise error if no SilverData is provided
        if not isinstance(silver, SilverData): 
            raise WrongInputError("Expected SilverData as input for silver parameter")
        
        else:
            
            self.goldDf = silver.get_dataframe().copy()
            
            # distiguish between different sources of measurement
            if source == "Rehm-recorder":
                
                # create df for gradient values
                gradientDf = self.goldDf[['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6']].copy()
                
                # call function to calc gradient if df is instanciated
                if isinstance(gradientDf, DataFrame):
                    self.calc_gradient(gradientDf)
                
                else:
                    raise WrongInputError(f"Expected a DataFrame, got {type(gradientDf)} instead.")
                
            ui.notify("call of function create_gold_object_multiple successful")
            return GoldData(DataFrame())
    
    
    def create_gold_data_final(self, gold: Data, chosenZeropoints: dict[str,DataFrame])->GoldData:
        
        # raise error if no GoldData is provided
        if not isinstance(gold, GoldData):
            raise WrongInputError("Expected GoldData as input for gold parameter")
        
        else:
            ui.notify("call of function create_gold_data_final successful")
            return GoldData(DataFrame())
        
    def calc_gradient(self, dataInput: DataFrame):
        """calculates the gradient for each column in the provided DataFrame and returns it as a dict of DataFrames"""
        
        # calculate gradient using diff() method and fill NaN values with 0
        gradientDf = dataInput.diff().fillna(0)
        # rename columns
        gradientDf = gradientDf.add_suffix('_gradient')
        
        # append values to goldDf
        self.goldDf = pd.concat([self.goldDf, gradientDf], axis=1)
        
    def calc_rolling_average(self, dataInput: DataFrame, mode: str, window_size: int):
        """calculates the rolling average for each column in the provided DataFrame and returns it as a dict of DataFrames"""
        
        windowStr = f"{window_size}s"
        rollingDf = None
        
        if mode == "trailing":
        # calculate rolling average using rolling() method and fill NaN values with 0
            rollingDf = dataInput.rolling(windowStr).mean().fillna(0)
        
        elif mode == "centered":
            rollingDf = dataInput.rolling(windowStr, center=True).mean().fillna(0)
            
        elif mode == "leading":
            rollingDf = dataInput.rolling(windowStr).mean().fillna(0).shift(-1, freq=windowStr)
        
                
        # append values to goldDf if type matches
        if isinstance(rollingDf, DataFrame):
            # rename columns
            rollingDf = rollingDf.add_suffix(f'_rolling_avg_{window_size}')
            # append to goldDf
            self.goldDf = pd.concat([self.goldDf, rollingDf], axis=1)
            
        else:
            raise WrongInputError(f"Expected a DataFrame, got {type(rollingDf)} instead.")
        