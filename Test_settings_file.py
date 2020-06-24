import json

# factory settings for reference comparison (double quotes used rather than single quote convention due to desire to allow copy-paste between this dictionary and the .json file)
factory_settings = {
    "Number of recent workflows displayed": 3,
    "Default freeze method": "Click or Ctrl",
    "Default record pause": "No pauses",
    "Default record pause over duration": 0.2,
    "Default record method": "Overwrite",
    "Default execute pause between commands": 0.2,
    "Default execute pause between commands checked": "True",
    "Default execute mouse command duration": 0.5,
    "Default execute mouse command duration checked": "True",
    "Interval between text character outputs": 0.05,
    "Interval between text character outputs checked": "True"
}

# settings validation lambda functions
settings_validation = {
    'Number of recent workflows displayed': lambda x: x in list(range(0, 6)),
    'Default freeze method': lambda x: x.lower() in [y.lower() for y in ['None', 'Click', 'Ctrl', 'Click or ctrl']],
    'Default record pause': lambda x: x.lower() in [y.lower() for y in ['No pauses', 'All pauses', 'Pauses over...']],
    'Default record pause over duration': lambda x: x > 0,
    'Default record method': lambda x: x.lower() in [y.lower() for y in ['Overwrite', 'Append']],
    'Default execute pause between commands': lambda x: x > 0,
    'Default execute pause between commands checked': lambda x: x in [True, False],
    'Default execute mouse command duration': lambda x: x > 0,
    'Default execute mouse command duration checked': lambda x: x in [True, False],
    'Interval between text character outputs': lambda x: x > 0,
    'Interval between text character outputs checked': lambda x: x in [True, False]
}

# open data/settings.json file to import settings, otherwise create empty dictionary to use factory settings
try:
    with open('data/settings.json', 'r') as file:
        imported_settings = json.load(file)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    imported_settings = dict()
    # TODO implement warning that settings.json file could not be parsed correctly

settings = dict()
for key in factory_settings:  # loop through the factory settings and attempt to parse imported setting if available
    if factory_settings[key] in ['True', 'False']:
        cast_type = bool
    else:
        cast_type = type(factory_settings[key])

    try:
        # TODO implement more parsing and verification of imported settings later
        if settings_validation[key](cast_type(imported_settings[key])):
            settings[key] = cast_type(imported_settings[key])

            if isinstance(settings[key], str):
                settings[key] = settings[key].capitalize()
        else:
            raise ValueError
    except (KeyError, ValueError):
        settings[key] = cast_type(factory_settings[key])

with open('data/settings.json', 'w') as json_file:
  json.dump(settings, json_file, indent=4)
