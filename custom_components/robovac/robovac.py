from enum import IntEnum
from homeassistant.components.vacuum import VacuumEntityFeature
from .tuyalocalapi import TuyaDevice


class RoboVacEntityFeature(IntEnum):
    """Supported features of the RoboVac entity."""

    EDGE = 1
    SMALL_ROOM = 2
    CLEANING_TIME = 4
    CLEANING_AREA = 8
    DO_NOT_DISTURB = 16
    AUTO_RETURN = 32
    CONSUMABLES = 64
    ROOM = 128
    ZONE = 256
    MAP = 512
    BOOST_IQ = 1024


HAS_MAP_FEATURE = ["T2261", "T2262"]

ROBOVAC_SERIES = {
    "C": [
        "T2103",
        "T2117",
        "T2118",
        "T2119",
        "T2120",
        "T2123",
        "T2128",
        "T2130",
    ],
    "G": [
        "T1250",
        "T2250",
        "T2251",
        "T2252",
        "T2253",
        "T2150",
        "T2255",
    ],
    "X": ["T2261", "T2262"],
}

ROBOVAC_SERIES_FEATURES = {
    "C": RoboVacEntityFeature.EDGE | RoboVacEntityFeature.SMALL_ROOM,
    "G": RoboVacEntityFeature.CLEANING_TIME
    | RoboVacEntityFeature.CLEANING_AREA
    | RoboVacEntityFeature.DO_NOT_DISTURB
    | RoboVacEntityFeature.AUTO_RETURN
    | RoboVacEntityFeature.CONSUMABLES,
    "X": RoboVacEntityFeature.CLEANING_TIME
    | RoboVacEntityFeature.CLEANING_AREA
    | RoboVacEntityFeature.DO_NOT_DISTURB
    | RoboVacEntityFeature.AUTO_RETURN
    | RoboVacEntityFeature.CONSUMABLES
    | RoboVacEntityFeature.ROOM
    | RoboVacEntityFeature.ZONE
    | RoboVacEntityFeature.MAP
    | RoboVacEntityFeature.BOOST_IQ,
}

ROBOVAC_SERIES_FAN_SPEEDS = {
"C": ["No Suction", "Standard", "Boost IQ", "Max"],
"G": ["Standard", "Turbo", "Max", "Boost IQ"],
"X": ["Pure", "Standard", "Turbo", "Max"],
}


SUPPORTED_ROBOVAC_MODELS = list(
    set([item for sublist in ROBOVAC_SERIES.values() for item in sublist])
)

class ModelNotSupportedException(Exception):
    """This model is not supported"""


class RoboVac(TuyaDevice):
    """"""

    def __init__(self, model_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_code = model_code

        if self.model_code not in SUPPORTED_ROBOVAC_MODELS:
            raise ModelNotSupportedException(
                "Model {} is not supported".format(self.model_code)
            )

    def getHomeAssistantFeatures(self):
        supportedFeatures = (
            VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.CLEAN_SPOT
            | VacuumEntityFeature.FAN_SPEED
            | VacuumEntityFeature.LOCATE
            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.RETURN_HOME
            | VacuumEntityFeature.SEND_COMMAND
            | VacuumEntityFeature.START
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.STOP
        )

        if self.model_code in HAS_MAP_FEATURE:
            supportedFeatures |= VacuumEntityFeature.MAP

        return supportedFeatures

    def getRoboVacFeatures(self):
        return ROBOVAC_SERIES_FEATURES[self.getRoboVacSeries()]

    def getRoboVacSeries(self):
        for series in ROBOVAC_SERIES:
            if self.model_code in series.value:
                return series.name


    def getFanSpeeds(self):
        return ROBOVAC_SERIES_FAN_SPEEDS[self.getRoboVacSeries()]
