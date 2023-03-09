import json

from envoy_solar_reader.dataretriever import DataRetriever


class EnvoySolarReader:
    def __init__(self, reader: DataRetriever):
        self._reader = reader

    def get_production_data(self) -> str:
        return json.dumps(self._reader.get_production_data().__dict__)
