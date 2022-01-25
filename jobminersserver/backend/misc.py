"""
This file consists of miscellaneous functions used in the project. The functions may be used either once or twice.

Consists:
* common_start: find the common starting substrings in strings
"""


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
