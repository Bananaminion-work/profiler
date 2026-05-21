from dataclasses import dataclass

@dataclass
class UploadContainer():
    fileName: str
    content: bytes

    def __init__(self, fileName: str, content: bytes):
        self.fileName = fileName
        self.content = content