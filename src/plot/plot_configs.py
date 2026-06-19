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
        
        # define line styles
        dash_styles = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot']
        
        # 2. helpingfunction to find out which y-axis is the right one for a channel
        def get_yaxis_for_column(col_name: str) -> str:
            
            # convert column name to lowercase for easier matching
            col_lower = col_name.lower()
            
            if 'gradient' in col_lower or "average" in col_lower:
                return 'y3'  # Axis 3: Gradients
            elif 'vacuum' in col_lower:
                return 'y2'  # Axis 2: Vacuum
            elif 'ch1' in col_lower or 'ch2' in col_lower or 'ch3' in col_lower or 'ch4' in col_lower or 'ch5' in col_lower or 'ch6' in col_lower:
                return 'y1'  # Axis 1: Temperature
            else:
                return 'y4'  # Axis 4: Unknown Channels (Fallback)

        # walk through every measurement in the dict
        for index, (m_id, df) in enumerate(dataDict.items()):
            
            # Choose the line style for this measurement (repeats if more than 6 measurements)
            current_dash = dash_styles[index % len(dash_styles)]
            
            # walk through every channel for this measurement
            for column in df.columns:
                
                # Find out which Y-axis this channel belongs to
                target_yaxis = get_yaxis_for_column(column)
                
                # add traces for every channel of every measurement
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        line=dict(dash=current_dash), # different line styles for each measurement!
                        name=f"{m_id[:4]} | {column}",
                        yaxis=target_yaxis            # assignment to the correct Y-axis!
                    )
                )
        
        # 3. Configure the layout with the 4 axes and the legend at the bottom
        fig.update_layout(
            title_text='Standard-Plot',
            
            # Compress the X-axis 
            xaxis=dict(
                title='Time',
                domain=[0.1, 0.9] 
            ),
            
            # Y-Axis 1: Temperature (Left, directly on the graph)
            yaxis=dict(
                title='Temperature [°C]',
                side='left'
            ),
            
            # Y-Axis 2: Vacuum (Right, directly on the graph)
            yaxis2=dict(
                title='Vacuum [mBar]',
                side='right',
                overlaying='y' # overlaying='y' forces it into the same plot
            ),
            
            # Y-Axis 3: Gradient (Right, outermost)
            yaxis3=dict(
                title='Gradient [K/s]',
                side='right',
                overlaying='y',
                anchor='free',
                position=1.0 # Moves the axis to the far right (100%)
            ),
            
            # Y-Axis 4: Unknown Channels (Left, outermost)
            yaxis4=dict(
                title='Other Channels',
                side='left',
                overlaying='y',
                anchor='free',
                position=0.0 # Moves the axis to the far left (0%)
            ),
            
            # Move the legend below the plot
            legend=dict(
                orientation="h",      # Arrange horizontally
                yanchor="top",
                y=-0.2,               # Negative value moves it down
                xanchor="center",
                x=0.5
            ),
            
            autosize=True,
            # Extra margin at the bottom to make room for the legend
            margin=dict(l=20, r=20, t=50, b=100) 
        )
        
        return fig