from homeassistant.components.vacuum import VacuumEntityFeature
from .base import RoboVacEntityFeature, RobovacCommand


class T2117:
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
    )
    robovac_features = RoboVacEntityFeature.EDGE | RoboVacEntityFeature.SMALL_ROOM
    commands = {
        RobovacCommand.START_PAUSE: 2,
        RobovacCommand.DIRECTION: {
            "code": 3,
            "values": ["forward", "back", "left", "right"],
        },
        RobovacCommand.MODE: {
            "code": 5,
            "values": ["auto", "SmallRoom", "Spot", "Edge", "Nosweep"],
        },
        RobovacCommand.STATUS: 15,
        RobovacCommand.RETURN_HOME: 101,
        RobovacCommand.FAN_SPEED: {
            "code": 102,
            "values": ["No_suction","Standard","Boost_IQ","Max"],
        },
        RobovacCommand.LOCATE: 103,
        RobovacCommand.BATTERY: 104,
        RobovacCommand.ERROR: 106,
    }
