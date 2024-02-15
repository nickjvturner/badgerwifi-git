# required_tags.py


# Project A
# required_tagKeys = ("ap-bracket", "antenna-bracket", "rf-group")


# Project B
requiredTagKeys = ("ap-bracket", "UNIT", "EX", "ind/out", "power", "backhaul", "building-group")


# Project C
# required_tagKeys = ("ap-bracket", "antenna-bracket", "rf-group")


def offender_constructor():
    offenders = {
        'color': [],
        'antennaHeight': [],
        'missing_tags': {}
    }

    for tagKey in requiredTagKeys:
        offenders['missing_tags'][tagKey] = []

    return offenders