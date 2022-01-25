"""
This file consists of base exceptions required around the project.
"""


class SomeThingNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
