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
                        yaxis=targetAxis
                    )
                )
        #
        fig.update_layout(
            title_text='Standard-Plot',
            showlegend=True,
            xaxis=dict(title='Time', domain=[0.1, 0.9]),
            yaxis=dict(title='Temperature in °C', side='left'),
            yaxis2=dict(title='Vacuum in mBar', side='right', anchor='x'),
            yaxis3=dict(title='Gradients in K/s', side='right', anchor='free', position=1.0),
            yaxis4=dict(title='Other Channels', side='left', anchor='free', position=0.0),
            legend=dict(orientation="h",yanchor="top",y=-0.2,xanchor="center",x=0.5),
            autosize=True,
            # Extra margin at the bottom to make room for the legend
            margin=dict(l=20, r=20, t=50, b=100)
        )
        
        return self.apply_dynamic_axes(fig, usedAxes)


        
class StandardConfig(BasePlotConfig):
    
    configName = "standard"
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame])-> go.Figure:
        
        fig = self.apply_std_layout(dataDict)
        
        fig.update_layout(
            title_text = "Standard Plot for VPS"
        )
        
        return fig
    
    
    
class SampleConfig(BasePlotConfig):
    
    configName = "Sample Config"
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame]) -> go.Figure:
        
        fig = go.Figure()
        
        # define line styles
        dash_styles = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot']
        
        # helpingfunction to find out which y-axis is the right one
        def get_yaxis_for_column(col_name: str) -> str:
            col_lower = col_name.lower()
            if 'gradient' in col_lower or "average" in col_lower:
                return 'y3'
            elif 'vacuum' in col_lower:
                return 'y2'
            elif 'ch' in col_lower:
                return 'y'
            else:
                return 'y4'

        for index, (m_id, df) in enumerate(dataDict.items()):
            current_dash = dash_styles[index % len(dash_styles)]
            
            for column in df.columns:
                target_yaxis = get_yaxis_for_column(column)
                
                # ---> NEU: Mathematische Normierung (Min-Max Scaling auf 0-100%) <---
                min_val = df[column].min()
                max_val = df[column].max()
                
                # Division durch 0 abfangen (falls eine Kurve komplett flach ist)
                if max_val != min_val:
                    # Normierungs-Formel: (Wert - Min) / (Max - Min) * 100
                    normalized_y = (df[column] - min_val) / (max_val - min_val) * 100
                else:
                    # Wenn die Kurve flach ist, setzen wir sie einfach auf 0%
                    normalized_y = (df[column] * 0) 
                
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=normalized_y,               # <--- HIER die normierten Daten plotten!
                        mode='lines',
                        line=dict(dash=current_dash),
                        connectgaps=True,
                        name=f"{m_id[:4]} | {column}",
                        yaxis=target_yaxis
                    )
                )
        
        # Configure the layout
        fig.update_layout(
            title_text='Normierter Prozess-Plot (Geheimhaltung)',
            showlegend=True,
            
            xaxis=dict(
                title='Time',
                domain=[0.1, 0.9],
                # Optional: Versteckt die echten Sekunden/Zeitstempel auf der X-Achse
                # showticklabels=False 
            ),
            
            # Alle Achsen zeigen jetzt 0-100% an, anstatt der echten Einheiten!
            yaxis=dict(
                title='Temperature in %',
                side='left',
                range=[-5, 105] # Ein kleiner Puffer oben und unten sieht besser aus
            ),
            
            yaxis2=dict(
                title='Vacuum in %',
                side='right',
                overlaying='y',
                range=[0, 1100] 
            ),
            
            yaxis3=dict(
                title='Gradient in %',
                side='right',
                overlaying='y',
                anchor='free',
                position=1.0,
                range=[-5, 105]
            ),
            
            yaxis4=dict(
                title='Other Channels in %',
                side='left',
                overlaying='y',
                anchor='free',
                position=0.0,
                range=[-5, 105]
            ),
            
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            
            autosize=True,
            margin=dict(l=20, r=20, t=50, b=100) 
        )
        
        return fig
    
class SampleConfig2(BasePlotConfig):
    
    configName = "Sample Config 2"
    
    def build_figure(self, dataDict: dict[str, pd.DataFrame]) -> go.Figure:
        
        fig = go.Figure()
        
        # define line styles
        dash_styles = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot']
        
        # helpingfunction to find out which y-axis is the right one
        def get_yaxis_for_column(col_name: str) -> str:
            col_lower = col_name.lower()
            if 'gradient' in col_lower or "average" in col_lower:
                return 'y3'
            elif 'vacuum' in col_lower:
                return 'y2'
            elif 'ch' in col_lower:
                return 'y'
            else:
                return 'y4'

        for index, (m_id, df) in enumerate(dataDict.items()):
            current_dash = dash_styles[index % len(dash_styles)]
            
            # ---------------------------------------------------------
            # NEU: Mathematische Normierung der X-ACHSE (Zeit) auf 0-100%
            # ---------------------------------------------------------
            min_x = df.index.min()
            max_x = df.index.max()
            
            if max_x != min_x:
                normalized_x = (df.index - min_x) / (max_x - min_x) * 100
            else:
                # Multiplikation mit 0 behält den Pandas-Datentyp bei (verhindert Fehler!)
                normalized_x = (df.index * 0)
            
            for column in df.columns:
                target_yaxis = get_yaxis_for_column(column)
                
                # ---------------------------------------------------------
                # Mathematische Normierung der Y-ACHSE (Werte) auf 0-100%
                # ---------------------------------------------------------
                min_val = df[column].min()
                max_val = df[column].max()
                
                # Division durch 0 abfangen (falls eine Kurve komplett flach ist)
                if max_val != min_val:
                    # Normierungs-Formel: (Wert - Min) / (Max - Min) * 100
                    normalized_y = (df[column] - min_val) / (max_val - min_val) * 100
                else:
                    # Wenn die Kurve flach ist, setzen wir sie einfach auf 0%
                    normalized_y = (df[column] * 0) 
                
                fig.add_trace(
                    go.Scatter(
                        x=normalized_x,               # <--- HIER das normierte X nutzen!
                        y=normalized_y,               # <--- HIER das normierte Y nutzen!
                        mode='lines',
                        line=dict(dash=current_dash),
                        connectgaps=True,
                        name=f"{m_id[:4]} | {column}",
                        yaxis=target_yaxis
                    )
                )
        
        # Configure the layout
        fig.update_layout(
            title_text='Normierter Prozess-Plot (Geheimhaltung)',
            showlegend=True,
            
            xaxis=dict(
                title='Time in %',            # <--- Achsentitel auf % geändert
                domain=[0.05, 0.95],         # <--- X-Achse etwas komprimiert, damit die Y-Achsen nicht abgeschnitten werden
                range=[-5, 105]              # <--- X-Achse zwingend auf 0 bis 100% (+ 5% Puffer)
            ),
            
            # Alle Y-Achsen zeigen jetzt 0-100% an
            yaxis=dict(
                title='Temperature in %',
                side='left',
                range=[-5, 105] 
            ),
            
            yaxis2=dict(
                title='Vacuum in %',
                side='right',
                overlaying='y',
                range=[-5, 105]
            ),
            
            yaxis3=dict(
                title='Gradient in %',
                side='right',
                overlaying='y',
                anchor='free',
                position=1.0,
                range=[-5, 105]
            ),
            
            yaxis4=dict(
                title='Other Channels in %',
                side='left',
                overlaying='y',
                anchor='free',
                position=0.0,
                range=[-5, 105]
            ),
            
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            
            autosize=True,
            margin=dict(l=20, r=20, t=50, b=100) 
        )
        
        return fig
