from .misccheckers import is_interested_website

class MiscCheckers:
    def test_is_interested_website(self):
        assert is_interested_website('https://play.google.com') == \
            False