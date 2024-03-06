const fs = require("fs/promises");
const path = require("path");

const ROBOVAC_SERIES = {
    C: [
        "T2103",
        "T2117",
        "T2118",
        "T2119",
        "T2120",
        "T2123",
        "T2128",
        "T2130",
        "T2132",
    ],
    G: [
        "T1250",
        "T2250",
        "T2251",
        "T2252",
        "T2253",
        "T2254",
        "T2150",
        "T2255",
        "T2256",
        "T2257",
        "T2258",
        "T2259",
        "T2270",
        "T2272",
        "T2273",
    ],
    L: ["T2181", "T2182", "T2190", "T2192", "T2193", "T2194"],
    X: ["T2261", "T2262", "T2320"],
};

const HAS_MAP_FEATURE = [
    "T2253",
    ...ROBOVAC_SERIES["L"],
    ...ROBOVAC_SERIES["X"],
];

const HAS_CONSUMABLES = [
    "T1250",
    "T2181",
    "T2182",
    "T2190",
    "T2193",
    "T2194",
    "T2253",
    "T2256",
    "T2258",
    "T2261",
    "T2273",
    "T2320",
];

const ROBOVAC_SERIES_FEATURES = {
    C: ["RoboVacEntityFeature.EDGE", "RoboVacEntityFeature.SMALL_ROOM"],
    G: [
        "RoboVacEntityFeature.CLEANING_TIME",
        "RoboVacEntityFeature.CLEANING_AREA",
        "RoboVacEntityFeature.DO_NOT_DISTURB",
        "RoboVacEntityFeature.AUTO_RETURN",
    ],
    L: [
        "RoboVacEntityFeature.CLEANING_TIME",
        "RoboVacEntityFeature.CLEANING_AREA",
        "RoboVacEntityFeature.DO_NOT_DISTURB",
        "RoboVacEntityFeature.AUTO_RETURN",
        "RoboVacEntityFeature.ROOM",
        "RoboVacEntityFeature.ZONE",
        "RoboVacEntityFeature.BOOST_IQ",
    ],
    X: [
        "RoboVacEntityFeature.CLEANING_TIME",
        "RoboVacEntityFeature.CLEANING_AREA",
        "RoboVacEntityFeature.DO_NOT_DISTURB",
        "RoboVacEntityFeature.AUTO_RETURN",
        "RoboVacEntityFeature.ROOM",
        "RoboVacEntityFeature.ZONE",
        "RoboVacEntityFeature.BOOST_IQ",
    ],
};

const ROBOVAC_SERIES_FAN_SPEEDS = {
    C: ["No_Suction", "Standard", "Boost_IQ", "Max"],
    G: ["Standard", "Turbo", "Max", "Boost_IQ"],
    L: ["Quiet", "Standard", "Turbo", "Max"],
    X: ["Pure", "Standard", "Turbo", "Max"],
};

const commands = [
    "CLEANING_AREA",
    "CLEANING_TIME",
    "AUTO_RETURN",
    "DO_NOT_DISTURB",
    "BOOST_IQ",
    "CONSUMABLES",
];

const allModels = [];

Object.entries(ROBOVAC_SERIES).forEach(([series, models]) => {
    models.forEach((model) => {
        allModels.push(model);

        const robovac_features = [...ROBOVAC_SERIES_FEATURES[series]];
        const homeassistant_features = [
            "VacuumEntityFeature.BATTERY",
            "VacuumEntityFeature.CLEAN_SPOT",
            "VacuumEntityFeature.FAN_SPEED",
            "VacuumEntityFeature.LOCATE",
            "VacuumEntityFeature.PAUSE",
            "VacuumEntityFeature.RETURN_HOME",
            "VacuumEntityFeature.SEND_COMMAND",
            "VacuumEntityFeature.START",
            "VacuumEntityFeature.STATE",
            "VacuumEntityFeature.STOP",
        ];

        if (HAS_MAP_FEATURE.includes(model)) {
            homeassistant_features.push("VacuumEntityFeature.MAP");
            robovac_features.push("RoboVacEntityFeature.MAP");
        }

        if (HAS_CONSUMABLES.includes(model)) {
            robovac_features.push("RoboVacEntityFeature.CONSUMABLES");
        }

        const extra_commands = commands
            .filter((command) =>
                robovac_features.includes(`RoboVacEntityFeature.${command}`)
            )
            .map((command) => `# RobovacCommand.${command}: 0,`);

        if (extra_commands.length > 0) {
            extra_commands.unshift("# These commands need codes adding");
        }

        const file = `from homeassistant.components.vacuum import VacuumEntityFeature
from .base import RoboVacEntityFeature, RobovacCommand


class ${model}:
    homeassistant_features = (
        ${homeassistant_features.join("\n        | ")}
    )
    robovac_features = ${robovac_features.join(" | ")}
    commands = {
        RobovacCommand.PAUSE: 2,
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
            "values": ${JSON.stringify(ROBOVAC_SERIES_FAN_SPEEDS[series])},
        },
        RobovacCommand.LOCATE: 103,
        RobovacCommand.BATTERY: 104,
        RobovacCommand.ERROR: 106,${
            extra_commands.length > 0
                ? `\n        ${extra_commands.join("\n        ")}`
                : ""
        }
    }
`;
        fs.writeFile(
            path.join(
                __dirname,
                "custom_components",
                "robovac",
                "vacuums",
                `${model}.py`
            ),
            file
        );
    });
});

const initFile = `${allModels
    .map((model) => `from .${model} import ${model}`)
    .join("\n")}


ROBOVAC_MODELS = {
${allModels.map((model) => `    "${model}": ${model}`).join(",\n")}
}`;

fs.writeFile(
    path.join(
        __dirname,
        "custom_components",
        "robovac",
        "vacuums",
        `__init__.py`
    ),
    initFile
);
