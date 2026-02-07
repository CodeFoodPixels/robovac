from homeassistant.components.vacuum import VacuumEntityFeature
from .base import RoboVacEntityFeature, RobovacCommand


class T2277:
    homeassistant_features = (
        VacuumEntityFeature.BATTERY
#        | VacuumEntityFeature.CLEAN_SPOT
        | VacuumEntityFeature.FAN_SPEED
        | VacuumEntityFeature.LOCATE
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.SEND_COMMAND
        | VacuumEntityFeature.START
        | VacuumEntityFeature.STATE
        | VacuumEntityFeature.STOP
#        | VacuumEntityFeature.MAP
    )
    robovac_features = (
    #    RoboVacEntityFeature.CLEANING_TIME
    #     | RoboVacEntityFeature.CLEANING_AREA
           RoboVacEntityFeature.DO_NOT_DISTURB
    #     | RoboVacEntityFeature.AUTO_RETURN
    #     | RoboVacEntityFeature.ROOM
    #     | RoboVacEntityFeature.ZONE
         | RoboVacEntityFeature.BOOST_IQ
    #     | RoboVacEntityFeature.MAP
    #     | RoboVacEntityFeature.CONSUMABLES
    )
    commands = {
        RobovacCommand.MODE: {  #works   (Start Auto and Return dock commands tested)
            "code": 152,
            "values": ["AggN","AA==","AggG","BBoCCAE=","AggO"],
        },
        RobovacCommand.STATUS: {  #works    (status only)
            "code": 153,
            "values": ["BgoAEAUyAA===","BgoAEAVSAA===","CAoAEAUyAggB","CAoCCAEQBTIA","CAoCCAEQBVIA","CgoCCAEQBTICCAE=","CAoCCAIQBTIA","CAoCCAIQBVIA","CgoCCAIQBTICCAE=","BAoAEAY=","BBAHQgA=","BBADGgA=","BhADGgIIAQ==","AA==","AhAB"],
        },        
        RobovacCommand.DIRECTION: {  #untested
            "code": 155,
            "values": ["Brake", "Forward", "Back", "Left", "Right"],
        },
        RobovacCommand.START_PAUSE: 156,    #   True, False           #works (status only)
        RobovacCommand.DO_NOT_DISTURB: 157, #   DgoAEgoKABICCBYaAggI  #untested
        RobovacCommand.FAN_SPEED: {                                   #works (status and update)
            "code": 158,
            "values": ["Quiet", "Standard", "Turbo", "Max"],
        },
        RobovacCommand.BOOST_IQ: 159,       #   True, False           #works (status and update)
        RobovacCommand.LOCATE: 160,         #   True, False           #works (status)
        # Speaker volume: 161                                         #works, not yet implemented
        RobovacCommand.BATTERY: 163,        #   int                   #works (status)
        RobovacCommand.CONSUMABLES: 168,                              #encrypted, not usable
        RobovacCommand.RETURN_HOME: 173,                              #encrypted, not usable
        #   FgoQMggKAggBEgIQAToECgIIARICCAE=
        #   FgoQMg4KAggBEggIARj/////DxICCAE=
        #   FAoQMggKAggBEgIQAToECgIIARIA
        #   GAoQMggKAggBEgIQAToECgIIARIECAE4AQ==
        #   GgoQMggKAggBEgIQAToECgIIARIGCAEYATgB
        RobovacCommand.ERROR: 177,          #                         #encrypted, few known values
        #   SIDEBRUSH_STUCK: "FAjwudWorOPszgEaAqURUgQSAqUR"
        #   ROBOT_STUCK: "FAj+nMu7zuPszgEaAtg2UgQSAtg2"
        
        
        #   IQofCgIIAhICCAIaAggCKgIIAjoCCBugAe7Pqs6M1+zOAQ==
        #   IQofCgIIAhICCAIaAggCKgIIAjoCCBqgAYPx0a331uzOAQ==
        #   IQofCgIIBBICCAQaAggEKgIIBDoCCCmgAcSfs6Lo5uzOAQ==

        # These commands need codes adding
        # RobovacCommand.CLEANING_AREA: 0,
        # RobovacCommand.CLEANING_TIME: 0,
        # RobovacCommand.AUTO_RETURN: 0,
        # Unknown: 151 (true/false)
        # Unknown: 154
        #    DgoKCgAaAggBIgIIARIA
        #    DAoICgAaAggBIgASAA==
        # Unknown: 164
        #    MBoAIiwKBgi4y/q0BhIECAEQARoMCAESBBgJIB4aAgg+Kg4aDBIKCgIIARIAGgAiAA==
        #    NAgGEAYaACIsCgYIuMv6tAYSBAgBEAEaDAgBEgQYCSAeGgIIPioOGgwSCgoCCAESABoAIgA=
        # Unknown: 167
        #    FAoAEgcIiEoQbhgEGgcI1EgQbBgC
        #    FgoCEAESBwiIShBuGAQaBwjUSBBsGAI=
        #    GAoECDwQARIHCIhKEG4YBBoHCNRIEGwYAg==
        #    GQoFCLQBEAQSBwiIShBuGAQaBwjUSBBsGAI=
        #    GwoFCKApEDgSCAiocxCmARgFGggI9HEQpAEYAw==
        # Unknown: 171
        #    AhAB
        # Unknown: 176 
        #    MQoAGgBSCBoAIgIIASoAWDJiHwodChFBIG5ldHdvcmsgZm9yIHlvdRABGgYQ4/7/tAY=
        #    LwoAGgBSCBoAIgIIASoAWFZiHQobChFBIG5ldHdvcmsgZm9yIHlvdRoGEPvagrUG
        #    LwoAGgBSCBoAIgIIASoAWCJiHQobChFBIG5ldHdvcmsgZm9yIHlvdRoGEK2YgLUG
        #    LwoAGgBSCBoAIgIIASoAWDBiHQobChFBIG5ldHdvcmsgZm9yIHlvdRoGEK2YgLUG
        # Unknown: 178
        #    DQjRidjfv9bszgESAR8=
        #    DQiMrPbd+eLszgESAVU=
        #    DQiW0dXL+uLszgESAR8=
        #    Cgiv6NbWsePszgE=
        #    DQjPuorb6eTszgESAR8=
        #    DQjayd7nsOXszgESASg=
        # Unknown: 179 
        #    EBIOKgwIBRACGAEgwYyAtQY=
        #    FhIUEhIIBRABIFsowYyAtQYw74yAtQY=
        #    DhIMKgoIBhgCIPvagrUG
        #    DhIMKgoIBxgCIJLbgrUG
        #    EBIOKgwIBxADGAIg3eyCtQY=
        #    EBIOKgwIBxAEGAIgrPGCtQY=
        #    DhIMKgoICBgCILHxgrUG
        #    DhIMKgoICBADIIj6grUG
        #    DhIMKgoICBADIOqMg7UG
        #    DhIMKgoICBAEIOuMg7UG
        #    DBIKKggICSCljYO1Bg==
        #    DhIMKgoICRACIJmcg7UG
        #    FhIUEhIICRABIBoomZyDtQYw6pyDtQY=
        #    DhIMIgoICRABGO+cg7UG
        #    DhIMIgoICRABGLedg7UG
        #    IRIfCh0ICRgBMPvagrUGOMmdg7UGQKApSDhQO1gBYAdqAA==
        # Unknown: 169 
        #    cwoSZXVmeSBDbGVhbiBMNjAgU0VTGhFDODpGRTowRjo3Nzo5NDo5QyIGMS4zLjI0KAVCKDM2NGFjOGNkNjQzZjllMDczZjg4NzlmNGFhOTdkZGE5OGUzMjg5NTRiFggBEgQIAhABGgQIAhABIgIIASoCCAE=
        #    s \x12eufy Clean L60 SES\x1a\x11C8:FE:0F:77:94:9C"\x061.3.24(\x05B(364ac8cd643f9e073f8879f4aa97dda98e328954b\x16\x08\x01\x12\x04\x08\x02\x10\x01\x1a\x04\x08\x02\x10\x01"\x02\x08\x01*\x02\x08\x01
    }
