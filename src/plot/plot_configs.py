from abc import ABC, abstractmethod
import nicegui as ui
import plotly.graph_objects as go
import pandas as pd


class BasePlotConfig(ABC):
    
    @abstractmethod
    def build_figure(self, df: pd.DataFrame)-> go.Figure:
        pass
    
class StandardConfig(BasePlotConfig):
    
    configName = "standard"
        
    def build_figure(self, df: pd.DataFrame):
        fig = go.Figure()
        
        for column in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[column],
                    mode='lines',
                    name=column
                )
            )
        
        
        fig.update_layout(
            title_text='TESTPLOT',
            xaxis_title='Time',
            yaxis_title='Measurement-values',
            autosize=True
        )
        
        return fig
        
class StandardConfig2(BasePlotConfig):
    
    configName = "standard2"
        
    def build_figure(self, df: pd.DataFrame):
        fig = go.Figure()
        
        for column in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[column],
                    mode='lines',
                    name=column
                )
            )
        
        
        fig.update_layout(
            title_text='TESTPLOT NUMMER 2',
            xaxis_title='Time',
            yaxis_title='Measurement-values',
            autosize=True
        )
        
        return fig