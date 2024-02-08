VERSION = (0, 1, 0, "final", 0)


def get_version():
    """Get package version."""
    string_version: str = ""
    if VERSION[3] == "final":
        string_version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"
    elif VERSION[3] == "dev":
        if VERSION[2] == 0:
            string_version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[3]}{VERSION[4]}"
        string_version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}.{VERSION[3]}{VERSION[4]}"
    else:
        string_version = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}{VERSION[3]}"
    return string_version


__version__ = get_version()
