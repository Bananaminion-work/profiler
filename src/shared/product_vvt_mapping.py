from src.shared.product_names import ProductNames
from src.shared.vvt_names import VvtNames

class ProductVvtMapping():
    
    @staticmethod
    def asdict():
        """returns a dict with product as key and vvt as value from the database"""
        return {
            ProductNames.DAI_V2             : VvtNames.GEN4_VL,
            ProductNames.DAI_V4             : VvtNames.GEN4_VL,
            ProductNames.VOLVO_EFAD         : VvtNames.GEN4_VL,
            ProductNames.VOLVO_ERAD         : VvtNames.GEN4_VL,
            ProductNames.VW_BASE            : VvtNames.GEN4_VL,
            ProductNames.VW_ECO_PMOC        : VvtNames.PM6_PMOC_ECO,
            ProductNames.OTHER              : VvtNames.VPS_MAIN
        }