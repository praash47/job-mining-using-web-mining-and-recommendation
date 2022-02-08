"""
This file consists of miscellaneous checkers required in various steps of our
processing.

Methods
-------
is_interested_website(home_page_url)
Returns False for websites present in the misccheckers.ini's interested_websites
non_interested variable.
"""
from backend.misc import read_config, log


def is_interested_website(home_page_url):
    """
    Checks if given home page url is in interested list i.e. not in non_interested
    list of misccheckers.ini. This is in order to ignore websites to reduce processing
    time.

    Parameters
    ----------
    home_page_url: str
        home page url to check, without a trailing slash '/'.
        for eg.: https://www.youtube.com
        and NOT https://www.facebook.com/

    Returns
    -------
    Boolean
        Is interested website or not? True, if interested
        False, if present in non_interested section of
        interested_websites section of misccheckers.ini.
    """
    config = read_config("checkers/misccheckers.ini")
    non_interested = config.get("interested_websites", "non_interested").split(", ")
    # Removing www. and https://

    try:
        home_page_url = home_page_url.replace("https://", "")
    except:
        home_page_url = home_page_url.replace("http://", "")

    try:
        home_page_url = home_page_url.replace("www.", "")
    except:
        pass
    if home_page_url in non_interested:
        return False

    log("checkjobs", "info", f"{home_page_url} is not an interested website.")
    return True


def main():
    print(is_interested_website("https://play.google.com"))
    print(is_interested_website("https://youtube.com"))
    print(is_interested_website("https://www.youtube.com"))
    print(is_interested_website("https://www.facebook.com"))


if __name__ == "__main__":
    main()
