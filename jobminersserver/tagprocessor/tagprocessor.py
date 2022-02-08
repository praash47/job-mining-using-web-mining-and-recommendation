"""
Tag Processor:
--------------
This file is used to process related to tag.

Processing includes
* extraction of contents from
* attributes
* innerContent

Classes
-------
TagProcessor
    Used to perform minor processing in the tags.
"""
from bs4 import BeautifulSoup


class TagProcessor:
    """
    Class used in processing tags. It is used to get content from the
    tag attributes. The attribute may be a name or may be any property that
    includes both og and non og properties.
    ...

    Attributes
    ----------
    html: str
        Raw HTML being processed
    tag:
        tag to process on

    Methods
    -------
    get_content()
        Returns inner content of tag.
        * For title: list of all words with
        , . | stripped and lower cased.
    get_content_from_name(name_to_get_from)
        Returns content from name="<name_to_get_from>"
    get_content_from_property(property_name, og=False)
        Returns content from property="<property_name>"
        If og is true, returns from property="og:<property_name>"
    """

    def __init__(self, html, tag=None):
        """
        Parameters
        ----------
        html: str
            Raw HTML to create the object of.
        tag: str, optional
            tag without <>.
            Eg: for <section> tag, pass 'section'.
        """
        self._tag_to_process = tag
        self._soup = BeautifulSoup(html, "html.parser")

    def get_content(self):
        """
        Get inner content from inside a tag.

        * For title: a list is returned with , | . split and lower
        cased.
        """
        if self._tag_to_process == "title":
            title = self._soup.title
            if title:
                try:
                    title = title.string.split(" ")
                    title = [
                        word.strip(",").strip("|").strip(".").lower() for word in title
                    ]
                    # remove empty strings
                    title = [word for word in title if word]
                    return title
                except:
                    return [""]

    def get_content_from_name(self, name_to_get_from):
        """
        Returns content from the name attribute of the
        tag in the object.

        Usage
        -----
        To extract <tag name="<name_to_get_from>".

        Parameters
        ----------
        name_to_get_from: str
            the name from which to get content.

        Returns
        -------
        str
            a string present in name="<name_to_get_from>" of the
            tag of the object.

        Raises
        ------
        No exception. If error is encountered, empty string is returned.
        """
        try:
            tag = self._soup.find(self._tag_to_process, {"name": name_to_get_from})
            return tag["content"]
        except:
            return ""

    def get_content_from_property(self, property_name, og=False):
        """
        Returns content from the property attribute of the
        tag in the object.

        Usage
        -----
        To extract <tag property="<property_name>".
        if og then, it extracts from <tag property="og:<property_name>".

        Parameters
        ----------
        property_name: str
            the property name from which to get content.
        og: boolean
            specifies if the property is og.

        Returns
        -------
        str
            a string present in
            * property="<name_to_get_from>"
            * property="og:<name_to_get_from>"
            of the tag of the object.

        Raises
        ------
        No exception. If error is encountered, empty string is returned.
        """
        try:
            if og:
                property_name = "og:" + property_name
            tag = self._soup.find(self._tag_to_process, {"property": property_name})
            return tag["content"]
        except:
            return ""
