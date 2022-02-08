"""
These submodule consists of decorators required related to tag processing.

Decorators
----------
for_all_tags(tags, soup): loops through tags in the soup and calls the function.s
for_existing_leaf_nodes(root): calls the function for leaf node in the root if the leaf node exists.
"""
from lxml import etree

from .misc import clean_text


def for_all_tags(func):
    """
    For all tags: Use tags and soup for looping inside a tag list and find that tag and
    call the func inside that tag.

    Keyworded Arguments
    -------------------
    tags: list of str
        tag list of names to loop in
    soup: BeautifulSoup
        soup to find each tag and call function in
    """

    def loop(*args, **kwargs):
        tags = kwargs.get("tags")
        soup = kwargs.get("soup")

        deadline_xpaths = []
        for tag_name in tags:
            for tag in soup.findAll(tag_name):
                res = func(*args, tag)
                if res:
                    deadline_xpaths = res
        return deadline_xpaths

    return loop


def for_existing_leaf_nodes(func):
    """
    For every exisiting leaf node or leaf node with value in a tree, loop through all html leaf node tags.

    Keyworded Arguments
    -------------------
    root: lxml.HtmlElement
        root node of the tree to which loop on leaf nodes.
    """

    def loop(*args, **kwargs):
        root = kwargs.get("root")
        some_new_value = None
        for parent in root:
            for node in parent.iter(tag=etree.Element):
                if not node.getchildren():
                    node_text = clean_text(node.text_content())
                    if node_text:
                        res = func(node, *args, node_text=node_text, **kwargs)
                        if type(res) is not str:
                            some_new_value = res
        return some_new_value

    return loop
