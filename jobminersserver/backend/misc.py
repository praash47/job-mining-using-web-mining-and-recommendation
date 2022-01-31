"""
This file consists of miscellaneous functions used in the project. The functions may be used either once or many times.

Consists:
* common_start(sa, sb): find the common starting substrings in strings
* read_config(config_path): reads and returns the ConfigParser file
* (decorator) try_and_pass: tries and passes if exception arises.
"""
# for settings

def read_config(config_path):
    """
    Returns the config parser object from where the sections of config can be read.

    Parameters
    ----------
    config_path
        relative path to config file respect to the root folder of the server

    Returns
    -------
    ConfigParser
        ConfigParser object of the config file
    """
    from configparser import ConfigParser
    # Read from config
    parser = ConfigParser()
    parser.read(config_path)

    return parser


def common_start(sa, sb):
    """
    Returns the longest common substring from the beginning of sa and sb

    Parameters
    ----------
    sa: string
        string 'a' to compare
    sb: string
        string 'b' to compare
    # ref: https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings

    Returns
    -------
    string
        common part between sa and sb.
    """
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())

def try_and_pass(func):
    """
    Tries and something and passes if the function raises exception
    """
    def exec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except: pass
    return exec
