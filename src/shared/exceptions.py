class StdToolError(Exception):
    pass

class InputFileError(StdToolError):
    pass

class DataError(StdToolError):
    pass

class ConnectionError(StdToolError):
    pass

class DatabaseQueryError(StdToolError):
    pass

class WrongInputError(StdToolError):
    pass