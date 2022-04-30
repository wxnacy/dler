from pydantic import BaseModel

class DownloadTaskModel(BaseModel):
    url: str
    path: str
