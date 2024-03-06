from .vacuums.base import RobovacCommand
from .tuyalocalapi import TuyaDevice
from .vacuums import ROBOVAC_MODELS


class ModelNotSupportedException(Exception):
    """This model is not supported"""


class RoboVac(TuyaDevice):
    """"""

    def __init__(self, model_code, *args, **kwargs):
        if model_code not in ROBOVAC_MODELS:
            raise ModelNotSupportedException(
                "Model {} is not supported".format(model_code)
            )

        self.model_details = ROBOVAC_MODELS[model_code]
        super().__init__(self.model_details, *args, **kwargs)

    def getHomeAssistantFeatures(self):
        return self.model_details.homeassistant_features

    def getRoboVacFeatures(self):
        return self.model_details.robovac_features

    def getFanSpeeds(self):
        return self.model_details.commands[RobovacCommand.FAN_SPEED]["values"]

    def getModes(self):
        return self.model_details.commands[RobovacCommand.MODE]["values"]

    def getSupportedCommands(self):
        return list(self.model_details.commands.keys())

    def getCommandCodes(self):
        command_codes = {}
        for key, value in self.model_details.commands.items():
            if isinstance(value, dict):
                command_codes[key] = str(value["code"])
            else:
                command_codes[key] = str(value)

        return command_codes
