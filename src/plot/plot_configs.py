from abc import ABC, abstractmethod
import nicegui as ui
import plotly.graph_objects as go
import pandas as pd


class BasePlotConfig(ABC):
    
    @abstractmethod
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        pass
    
    def get_axis_for_column(self, col_name: str) -> str:
        """returns the appropriate y-axis for a given column name based on predefined rules
        
        used for dynamic axes application"""
        
        # convert column name to lowercase for easier matching
        col_lower = col_name.lower()
        
        if 'gradient' in col_lower or "average" in col_lower:
            return 'y3'  # Axis 3: Gradients
        elif 'vacuum' in col_lower:
            return 'y2'  # Axis 2: Vacuum
        elif 'ch1' in col_lower or 'ch2' in col_lower or 'ch3' in col_lower or 'ch4' in col_lower or 'ch5' in col_lower or 'ch6' in col_lower:
            return 'y1'   # Axis 1: Temperature
        else:
            return 'y4'  # Axis 4: Unknown Channels (Fallback)
        
    
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
    
    # DONT CHANGE THE NAME!
    # if the name is changed, please change it in the "show" pages as well, otherwise the config will not be found
    
    configName = "Standard"
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = self.apply_std_layout(dataDict)
        
        fig.update_layout(
            title_text = "Standard Plot for VPS"
        )
        
        fig = self.apply_bottom_legend(fig)
        
        return fig
    
    
    
class SideLegendConfig(BasePlotConfig):
    
    configName = "Standard with Side Legend"
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = self.apply_std_layout(dataDict)
        
        fig.update_layout(
            title_text = "Standard Plot for VPS"
        )
        
        fig = self.apply_side_legend(fig)
        
        return fig