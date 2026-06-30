from src.shared.channel_names import ChannelNames

class PlotPresets:
    
    # dict with all presets
    
    ####### CREATE A NEW ONE IF NEEDED #######
    PRESETS = {
        
        "All" : None,
        
        
        "Default" : [
            ChannelNames.CH1,
            ChannelNames.CH2,
            ChannelNames.CH3,
            ChannelNames.CH4,
            ChannelNames.VACUUM,
            ChannelNames.COOLING_FAN_SPEED,
            ChannelNames.MEDIUM_PUMP,
            ],
        
        
        "Default with Gradients" : [
            ChannelNames.CH1,
            ChannelNames.CH2,
            ChannelNames.CH3,
            ChannelNames.CH4,
            ChannelNames.CH1_GRADIENT,
            ChannelNames.CH2_GRADIENT,
            ChannelNames.CH3_GRADIENT,
            ChannelNames.CH4_GRADIENT,
            ChannelNames.VACUUM,
            ChannelNames.COOLING_FAN_SPEED,
            ChannelNames.MEDIUM_PUMP,
        ],
        
        
        "Default with Gradients and Rolling Avg" : [
            ChannelNames.CH1,
            ChannelNames.CH2,
            ChannelNames.CH3,
            ChannelNames.CH4,
            ChannelNames.CH1_GRADIENT_ROLLING_AVG,
            ChannelNames.CH2_GRADIENT_ROLLING_AVG,
            ChannelNames.CH3_GRADIENT_ROLLING_AVG,
            ChannelNames.CH4_GRADIENT_ROLLING_AVG,
            ChannelNames.VACUUM,
            ChannelNames.COOLING_FAN_SPEED,
            ChannelNames.MEDIUM_PUMP,
        ],
    }
    
    
    ##### Methods #####
    
    @classmethod
    def get_options(cls):
        """Return a list of available preset names"""
        return list(cls.PRESETS.keys())
    
    @classmethod
    def get_preset(cls, name:str):
        """Return the preset corresponding to the given name, or None if not found"""
        return cls.PRESETS.get(name, None)