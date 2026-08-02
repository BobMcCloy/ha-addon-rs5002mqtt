from typing import Sequence, Optional, Dict
from dataclasses import dataclass

@dataclass
class TempHum:
    temperature: float
    humidity: int

    @staticmethod
    def from_protocol(temp: Sequence[int], hum: int) -> "TempHum":
        return TempHum(float(int.from_bytes(temp, byteorder="big", signed=True)) / 10.0, hum)

class Response:
    def __init__(self):
        self.__data: Dict[int, Optional[TempHum]] = {i: None for i in range(1, 9)}

    def get_channel_data(self, channel: int) -> Optional[TempHum]:
        return self.__data.get(channel)

    def set_channel_data(self, channel: int, data: TempHum):
        self.__data[channel] = data

    @property
    def all(self) -> dict:
        return self.__data
