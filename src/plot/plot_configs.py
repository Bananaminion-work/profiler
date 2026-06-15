from abc import ABC, abstractmethod
import nicegui as ui
import plotly.graph_objects as go
import pandas as pd


class BasePlotConfig(ABC):
    
    #@abstractmethod
    #def build_figure(self, df: pd.DataFrame)-> go.Figure:
    #    pass
    
    @abstractmethod
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        pass
    
class StandardConfig(BasePlotConfig):
    
    configName = "standard"
        
    #def build_figure(self, df: pd.DataFrame):
    #    fig = go.Figure()
    #    
    #    for column in df.columns:
    #        fig.add_trace(
    #            go.Scatter(
    #                x=df.index,
    #                y=df[column],
    #                mode='lines',
    #                name=column
    #            )
    #        )
    #    
    #    
    #    fig.update_layout(
    #        title_text='TESTPLOT',
    #        xaxis_title='Time',
    #        yaxis_title='Measurement-values',
    #        autosize=True
    #    )
    #    
    #    return fig
    

    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = go.Figure()
        
        # walk through every measurement in the dict
        for m_id, df in dataDict.items():
            
            # walk through every channel for this measurement
            for column in df.columns:
                
                # add traces for every channel of every measurement
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        # name of the legend
                        name=f"{m_id[:4]} | {column}"
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
        
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        fig = go.Figure()
        
        for m_id, df in dataDict.items():
            for column in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        name=f"{m_id[:4]} | {column}"
                    )
                )
        
        
        fig.update_layout(
            title_text='TESTPLOT NUMMER 2',
            xaxis_title='Time',
            yaxis_title='Measurement-values',
            autosize=True
        )
        
        return fig