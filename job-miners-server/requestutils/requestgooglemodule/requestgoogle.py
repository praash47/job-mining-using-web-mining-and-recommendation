class RequestGoogle (Requests):
    def __init__(self):
        super.__init__('www.google.com')
        self._100urls = []

    def get_100_urls(self):
        self._100.urls = []