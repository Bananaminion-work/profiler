from abc import ABC, abstractmethod
import nicegui as ui
import plotly
import plotly.graph_objects as go
import pandas as pd

from src.shared.channel_names import ChannelNames
from src.shared.config_names import ConfigNames

class BasePlotConfig(ABC):
    
    @abstractmethod
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        pass
    
    def get_axis_for_column(self, col_name: str) -> str:
        """returns the appropriate y-axis for a given column name based on predefined rules
        
        used for dynamic axes application"""
        
        # convert column name to lowercase for easier matching
        
        
        ## define the right axis based on the column name
        
        # gradients
        if col_name in{
            
            ChannelNames.CH1_GRADIENT,
            ChannelNames.CH2_GRADIENT,
            ChannelNames.CH3_GRADIENT,
            ChannelNames.CH4_GRADIENT,
            ChannelNames.CH5_GRADIENT,
            ChannelNames.CH6_GRADIENT,
            
            ChannelNames.CH1_GRADIENT_ROLLING_AVG,
            ChannelNames.CH2_GRADIENT_ROLLING_AVG,
            ChannelNames.CH3_GRADIENT_ROLLING_AVG,
            ChannelNames.CH4_GRADIENT_ROLLING_AVG,
            ChannelNames.CH5_GRADIENT_ROLLING_AVG,
            ChannelNames.CH6_GRADIENT_ROLLING_AVG,
            
            }:
            return 'y3'  # Gradients in K/s
        
        # pressure
        elif col_name == ChannelNames.VACUUM:
            return 'y2'  # Vacuum in mBar
        
        
        # temperature
        elif col_name in {
            ChannelNames.CH1,
            ChannelNames.CH2,
            ChannelNames.CH3,
            ChannelNames.CH4,
            ChannelNames.CH5,
            ChannelNames.CH6,
            
            ChannelNames.HEATER_BOTTOM1_ACTUAL,
            ChannelNames.HEATER_BOTTOM2_ACTUAL,
            ChannelNames.HEATER_BOTTOM3_ACTUAL,
            ChannelNames.HEATER_BOTTOM4_ACTUAL,
            
            ChannelNames.HEATER_SIDEBACK_ACTUAL,
            ChannelNames.HEATER_SIDEFRONT_ACTUAL,
            ChannelNames.HEATER_SIDELEFT_ACTUAL,
            ChannelNames.HEATER_SIDERIGHT_ACTUAL,
            
            ChannelNames.MON_PRC_CHA
        }:
            return 'y1'  # Temperature in °C
        
        # fallback
        else:
            return 'y4'  # Other channels
        
        
        
        
    
    def apply_dynamic_axes(self, fig: go.Figure, usedAxes: list[str]) -> go.Figure:
        """solves scaling-problem for plot
        
        uses the first axis as reference and scales all others accordingly and as overlays."""
        
        # set the first axis as reference
        refAxis = usedAxes[0] if usedAxes else 'y1'
        # create a layout update dictionary to hold the axis configurations
        layoutUpdate = {}
        
        # loop through all axes and set them to overlay the reference axis
        for id in ['y1', 'y2', 'y3', 'y4']:
            # determine the layout key based on the axis id
            layoutKey = 'yaxis' if id == 'y1' else f'yaxis{id[1]}'
            
            # if the current axis is not the reference axis, set it to overlay the reference axis
            if id != refAxis:
                layoutUpdate[layoutKey] = dict(
                    overlaying=refAxis
                )
            else:
                layoutUpdate[layoutKey] = dict(
                    overlaying=None
                )
                
        # update the figure layout with the new axis configurations
        fig.update_layout(**layoutUpdate)
        return fig
    
    def apply_std_layout(self, dataDict: dict[str, pd.DataFrame]) -> go.Figure:
        """Applies a standard layout to the figure based on the provided data dictionary.
        
        creates multiple y-axes for different channels and applies different line styles for each measurement_id."""
        
        fig = go.Figure()
        dashStyles = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot']
        usedAxes = []
        
        # 
        for index, (m_id, df) in enumerate(dataDict.items()):
            currentDash = dashStyles[index % len(dashStyles)]
            for column in df.columns:
                targetAxis = self.get_axis_for_column(column)
                if targetAxis not in usedAxes:
                    usedAxes.append(targetAxis)
                
                fig.add_trace(
                    go.Scatter(
                        x=df.index,                 y=df[column],
                        mode='lines',               line=dict(dash=currentDash),
                        name=f"{m_id} | {column}",  connectgaps=True,
                        yaxis=targetAxis,           hovertemplate=f"(%{{x}}, %{{y}}) : {m_id} : {column}<extra></extra>"
                    )
                )
        #
        fig.update_layout(
            title_text='Standard-Plot',
            showlegend=True,
            xaxis=dict(title='Time', domain=[0.05, 0.95]),
            yaxis=dict(title='Temperature in °C', side='left'),
            yaxis2=dict(title='Pressure in mBar', side='right', anchor='x'),
            yaxis3=dict(title='Gradients in K/s', side='right', anchor='free', position=1.0),
            yaxis4=dict(title='Other Channels', side='left', anchor='free', position=0.0),
            legend=dict(orientation="h",yanchor="top",y=-0.2,xanchor="center",x=0.5),
            autosize=True,
            # Extra margin at the bottom to make room for the legend
            margin=dict(l=20, r=20, t=50, b=100)
        )
        
        return self.apply_dynamic_axes(fig, usedAxes)
    
    
    
    def apply_bottom_legend(self, fig: go.Figure) -> go.Figure:
        """applies a bottom legend to the figure
        """
        
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y= -0.1,
                xanchor="center",
                x=0.5,
                maxheight=0.1
            ),
            autosize=True
        )
        
        
        return fig
    
    
    def apply_side_legend(self, fig: go.Figure, legend_width: int = 250) -> go.Figure:
        """Puts the Legend to the right
        
        legend_width: width of the legend in pixels
        """
        
        fig.update_layout(
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1.0,
                xanchor="left",
                x=1.05,
                yref="paper"           # forces the legend to be scaled according to the plot 
            ),
            
            margin=dict(l=20, r=legend_width, t=50, b=20),
            autosize=True
        )
        
        return fig









        
class StandardConfig(BasePlotConfig):
    
    configName = ConfigNames.STANDARD_BOTTOM
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = self.apply_std_layout(dataDict)
        
        fig.update_layout(
            title_text = "One window Plot for VPS"
        )
        
        fig = self.apply_bottom_legend(fig)
        
        return fig
    
    
    
class SideLegendConfig(BasePlotConfig):
    
    configName = ConfigNames.STANDARD_SIDE
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = self.apply_std_layout(dataDict)
        
        fig.update_layout(
            title_text = "One window Plot for VPS"
        )
        
        fig = self.apply_side_legend(fig)
        
        return fig
    
    
#########-------- [INFO] ---------#########
# If you want to add a new config, please create it here

#you can use this blueprint as a template:

                        #class NewConfig(BasePlotConfig):
                        #    
                        #    configName = ConfigNames.YOUR_NEW_CONFIG_NAME
                        #    
                        #    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
                        #        
                        #        fig = self.apply_std_layout(dataDict)
                        #        
                        #        fig.update_layout(
                        #            title_text = "New Config Plot for VPS"
                        #        )
                        #        
                        #        # choose either bottom or side legend
                        #        fig = self.apply_bottom_legend(fig)
                        #        # fig = self.apply_side_legend(fig)
                        #        
                        #        return fig
                        
# please make sure to use a unique name for the config and add it to the ConfigNames class in src/shared/confi_names.py

# this ensures that the APP will run smoothly and you can change the Name as you like