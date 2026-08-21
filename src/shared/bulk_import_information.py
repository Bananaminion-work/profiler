class BulkImportInformation():
    """class to hold the information of a single imported measurement from a zip file"""
    
    FILENAME = "Filename"
    DESCRIPTION = "Description"
    CONFIG_NAME = "Configuration name"
    DATE = "Date"
    STARTTIME = "Start time"
    
    _filename: str
    _description: str
    _config_name: str
    _date: str
    _starttime: str
    
    def __init__(self, filename: str ="", description: str="", config_name: str="", date: str="", starttime: str=""):
        """can be initialized with or without params"""
        self._filename = filename
        self._description = description
        self._config_name = config_name
        self._date = date
        self._starttime = starttime
        
    
    def get_info_dict(self) -> dict[str, str]:
        """returns the information as a dictionary with the keys being the column names"""
        return {
            self.FILENAME: self._filename,
            self.DESCRIPTION: self._description,
            self.CONFIG_NAME: self._config_name,
            self.DATE: self._date,
            self.STARTTIME: self._starttime
        }
        
    @property
    def filename(self) -> str:
        return self._filename
    @property
    def description(self) -> str:
        return self._description

    @property
    def config_name(self) -> str:
        return self._config_name

    @property
    def date(self) -> str:
        return self._date

    @property
    def starttime(self) -> str:
        return self._starttime
    
    @filename.setter
    def filename(self, value: str):
        self._filename = value
        
    @description.setter
    def description(self, value: str):
        self._description = value

    @config_name.setter
    def config_name(self, value: str):
        self._config_name = value

    @date.setter
    def date(self, value: str):
        self._date = value

    @starttime.setter
    def starttime(self, value: str):
        self._starttime = value
    
    
    def __repr__(self) -> str:
        return f"BulkImportInformation(filename={self._filename}, date={self._date}, config={self._config_name})"