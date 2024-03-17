from homeassistant.components.vacuum import VacuumEntityFeature
from .base import RoboVacEntityFeature, RobovacCommand


class T2267:
    homeassistant_features = (
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
        | VacuumEntityFeature.MAP
    )
    robovac_features = (
        RoboVacEntityFeature.CLEANING_TIME
        | RoboVacEntityFeature.CLEANING_AREA
        | RoboVacEntityFeature.DO_NOT_DISTURB
        | RoboVacEntityFeature.AUTO_RETURN
        | RoboVacEntityFeature.ROOM
        | RoboVacEntityFeature.ZONE
        | RoboVacEntityFeature.BOOST_IQ
        | RoboVacEntityFeature.MAP
        | RoboVacEntityFeature.CONSUMABLES
    )
    commands = {
        RobovacCommand.START_PAUSE: 156,
        RobovacCommand.DIRECTION: {
            "code": 155,
            "values": ["Brake", "Forward", "Back", "Left", "Right"],
        },
        RobovacCommand.MODE: {
            "code": 152,
            # "values": ["auto", "SmallRoom", "Spot", "Edge", "Nosweep"],
        },
        RobovacCommand.STATUS: 153,
        RobovacCommand.RETURN_HOME: 173,
        RobovacCommand.FAN_SPEED: {
            "code": 158,
            "values": ["Quiet", "Standard", "Turbo", "Max"],
        },
        RobovacCommand.LOCATE: 160,
        RobovacCommand.BATTERY: 163,
        RobovacCommand.ERROR: 177,
        # These commands need codes adding
        # RobovacCommand.CLEANING_AREA: 0,
        # RobovacCommand.CLEANING_TIME: 0,
        # RobovacCommand.AUTO_RETURN: 0,
        # RobovacCommand.DO_NOT_DISTURB: 157,
        # RobovacCommand.BOOST_IQ: 159,
        # RobovacCommand.CONSUMABLES: 168,
    }
