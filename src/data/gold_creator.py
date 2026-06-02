from nicegui import ui
from pandas import DataFrame
import pandas as pd
from src.shared.data_models import GoldData, SilverData
from src.shared.exceptions import WrongInputError

class GoldCreator():
    
    goldDf: DataFrame   
    
    def create_gold_object(self, silver: SilverData, source: str)->GoldData:
        
        # raise error if no SilverData is provided
        if not isinstance(silver, SilverData): 
            raise WrongInputError(f"Expected SilverData as input for silver parameter, got {type(silver)} instead.")
        
        else:
            
            self.goldDf = silver.get_dataframe().copy()
            
            self.goldDf.reset_index(inplace=True) # ensure ReadTime is a column for processing
            
            # distiguish between different sources of measurement
            if source == "Rehm-recorder":
                               
                
                # create df for gradient values
                channelDf = self.goldDf[['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6']].copy()
                
                # create df for gradient
                gradientDf = DataFrame()
                
                #create df for rolling average
                rollingDf = DataFrame()
                
                # call function to calc gradient if df is instanciated
                if isinstance(channelDf, DataFrame):
                    gradientDf = self.calc_gradient(channelDf)
                    
                    if isinstance(gradientDf, DataFrame):
                        rollingDf = self.calc_rolling_average(gradientDf, mode="trailing", window_size=10)
                        
                    else:
                        ui.notify(f"Expected a DataFrame, got {type(gradientDf)} instead.")
                
                else:
                    ui.notify(f"Expected a DataFrame, got {type(channelDf)} instead.")
                
                
                self.goldDf = pd.concat([self.goldDf, gradientDf, rollingDf], axis=1)
            
            # set ReadTime as index
            self.goldDf.set_index('ReadTime', inplace=True)
                
            return GoldData(self.goldDf)
        
        
        
    def calc_gradient(self, dataInput: DataFrame):
        """calculates the gradient for each column in the provided DataFrame and returns it as a dict of DataFrames"""
        
        # calculate gradient using diff() method and fill NaN values with 0
        gradientDf = dataInput.diff().fillna(0)
        # rename columns
        gradientDf = gradientDf.add_suffix('_gradient')
        
        # return gradientDf
        return gradientDf
        
        
        
    def calc_rolling_average(self, dataInput: DataFrame, mode: str, window_size: int):
        """calculates the rolling average for each column in the provided DataFrame and returns it as a dict of DataFrames"""
        
        #windowStr = f"{window_size}s"
        rollingDf = None
        
        if mode == "trailing":
        # calculate rolling average using rolling() method and fill NaN values with 0
            rollingDf = dataInput.rolling(window_size).mean().fillna(0)
        
        elif mode == "centered":
            rollingDf = dataInput.rolling(window_size, center=True).mean().fillna(0)
            
        elif mode == "leading":
            rollingDf = dataInput.rolling(window_size).mean().fillna(0).shift(-1, freq=window_size)
        
                
        # rename and return df if it is instanciated
        if isinstance(rollingDf, DataFrame):
            
            # rename columns
            rollingDf = rollingDf.add_suffix(f'_rolling_avg')
            
            # return rollingDf
            return rollingDf
            
        else:
            raise WrongInputError(f"Expected a DataFrame, got {type(rollingDf)} instead.")
        