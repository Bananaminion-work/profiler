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
            ChannelNames.CH5,
            ChannelNames.CH6,
            ChannelNames.VACUUM,
            ChannelNames.COOLING_FAN_SPEED,
            ChannelNames.MEDIUM_PUMP,
            ],
        
        
        "Default with Gradients and Rolling Avg" : [
            ChannelNames.CH1,
            ChannelNames.CH2,
            ChannelNames.CH3,
            ChannelNames.CH4,
            ChannelNames.CH5,
            ChannelNames.CH6,
            ChannelNames.CH1_GRADIENT_ROLLING_AVG,
            ChannelNames.CH2_GRADIENT_ROLLING_AVG,
            ChannelNames.CH3_GRADIENT_ROLLING_AVG,
            ChannelNames.CH4_GRADIENT_ROLLING_AVG,
            ChannelNames.CH5_GRADIENT_ROLLING_AVG,
            ChannelNames.CH6_GRADIENT_ROLLING_AVG,
            ChannelNames.VACUUM,
            ChannelNames.COOLING_FAN_SPEED,
            ChannelNames.MEDIUM_PUMP,
        ],
        
        "Bottom Heaters" : [
            ChannelNames.HEATER_BOTTOM1_ACTUAL,
            ChannelNames.HEATER_BOTTOM2_ACTUAL,
            ChannelNames.HEATER_BOTTOM3_ACTUAL,
            ChannelNames.HEATER_BOTTOM4_ACTUAL,
            ChannelNames.HEATER_BOTTOM1_Y,
            ChannelNames.HEATER_BOTTOM2_Y,
            ChannelNames.HEATER_BOTTOM3_Y,
            ChannelNames.HEATER_BOTTOM4_Y,
            ChannelNames.OUTLET_BULKHEAD_OPEN,
            ChannelNames.INLET_BULKHEAD_OPEN,
            ChannelNames.MON_PRC_CHA
            
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