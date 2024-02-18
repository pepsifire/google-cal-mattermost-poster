from dataclasses import dataclass
import json

@dataclass
class Config:
    google_api_key: str
    calendar_id: str
    mm_api_key: str
    mm_team_name: str
    mm_url: str

    @staticmethod
    def from_file(filename):
        try:
            with open(filename, "r") as configFile:
                data = json.load(configFile)
            return Config(**data)
        except FileNotFoundError:
            print("Failed to load config! Wrong filename?")
            return None