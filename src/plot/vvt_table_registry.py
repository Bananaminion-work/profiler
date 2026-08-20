from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.shared.channel_names import ChannelNames
from src.shared.condition_names import ConditionNames
from src.shared.vvt_names import VvtNames
from src.shared.vvt_scopes import VvtScopes
@dataclass
class VvtTableRegistry:
    label: str
    editable: bool = True
    widget: str = "text"
    option_source: Optional[type] = None
    
    
    
    
    
COLUMN_REGISTRY: dict[str, "VvtTableRegistry"] = {
    "vvt_name":   VvtTableRegistry(label="VVT Name",    widget="dropdown",  option_source=VvtNames),
    "rule_id":    VvtTableRegistry(label="Rule ID",     widget="text"),
    "rule_name":  VvtTableRegistry(label="Rule Name",   widget="text"),
    "channel":    VvtTableRegistry(label="Channel",     widget="dropdown",  option_source=ChannelNames),
    "condition":  VvtTableRegistry(label="Condition",   widget="dropdown",  option_source=ConditionNames),
    "threshold":  VvtTableRegistry(label="Threshold",   widget="text"),
    "param1":     VvtTableRegistry(label="Param 1",     widget="text"),
    "param2":     VvtTableRegistry(label="Param 2",     widget="text"),
    "param3":     VvtTableRegistry(label="Param 3",     widget="text"),
    "scope":      VvtTableRegistry(label="Scope",       widget="dropdown",  option_source=VvtScopes)
}