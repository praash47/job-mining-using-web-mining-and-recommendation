import re

def clean_text(text):
    """
    Cleans text and returns it.

    Parameters
    ----------
    text
        text to operate cleaning on

    Returns
    -------
    str
        text, cleaned form of the text
    """
    # Reduce multiple spaces into single spaces
    text = re.sub(' +', ' ', text)
    # Replace colon and new line characters
    text = text.lower().replace(':', '').replace('\\n', '').replace('\n', '').strip()
    # Replace \r and \s type of characters
    text = text.replace('\\r', '').replace('\\s', '')
    
    return text