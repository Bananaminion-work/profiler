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
                return 'y1'
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
                        name=f"{m_id[:4]} | {column}",
                        yaxis=target_yaxis
                    )
                )
        
        # Configure the layout
        fig.update_layout(
            title_text='Normierter Prozess-Plot (Geheimhaltung)',
            
            xaxis=dict(
                title='Time',
                domain=[0.1, 0.9],
                # Optional: Versteckt die echten Sekunden/Zeitstempel auf der X-Achse
                # showticklabels=False 
            ),
            
            # Alle Achsen zeigen jetzt 0-100% an, anstatt der echten Einheiten!
            yaxis=dict(
                title='Temperature [%]',
                side='left',
                range=[-5, 105] # Ein kleiner Puffer oben und unten sieht besser aus
            ),
            
            yaxis2=dict(
                title='Vacuum [%]',
                side='right',
                overlaying='y',
                range=[-5, 105]
            ),
            
            yaxis3=dict(
                title='Gradient [%]',
                side='right',
                overlaying='y',
                anchor='free',
                position=1.0,
                range=[-5, 105]
            ),
            
            yaxis4=dict(
                title='Other Channels [%]',
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
                return 'y1'
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
                        name=f"{m_id[:4]} | {column}",
                        yaxis=target_yaxis
                    )
                )
        
        # Configure the layout
        fig.update_layout(
            title_text='Normierter Prozess-Plot (Geheimhaltung)',
            
            xaxis=dict(
                title='Time [%]',            # <--- Achsentitel auf % geändert
                domain=[0.05, 0.95],         # <--- X-Achse etwas komprimiert, damit die Y-Achsen nicht abgeschnitten werden
                range=[-5, 105]              # <--- X-Achse zwingend auf 0 bis 100% (+ 5% Puffer)
            ),
            
            # Alle Y-Achsen zeigen jetzt 0-100% an
            yaxis=dict(
                title='Temperature [%]',
                side='left',
                range=[-5, 105] 
            ),
            
            yaxis2=dict(
                title='Vacuum [%]',
                side='right',
                overlaying='y',
                range=[-5, 105]
            ),
            
            yaxis3=dict(
                title='Gradient [%]',
                side='right',
                overlaying='y',
                anchor='free',
                position=1.0,
                range=[-5, 105]
            ),
            
            yaxis4=dict(
                title='Other Channels [%]',
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
