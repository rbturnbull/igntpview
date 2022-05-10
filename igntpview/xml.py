from lxml import etree
from bs4 import BeautifulSoup
import re

def strip_namespace(el):
    if hasattr(el, "tag") and isinstance(el.tag, str) and "}" in el.tag:
        el.tag = el.tag.split("}", 1)[1]  # strip all namespaces
    for x in el:
        strip_namespace(x)

def element_to_text(element):
    text = etree.tostring(
        element, encoding="UTF-8", method="xml"
    ).decode("utf-8")
    text = re.sub(r'\s*<lb break="no"/>\s*', "", text) # big hack
    text = re.sub(r'\s*<unclear>(.*)</unclear>\s*', r"\1", text)
    text = BeautifulSoup(
        text, "lxml"
    ).text  # This is a bit of a hack
    return text


def element_to_text_coloured(element):
    text = element_to_text(element)
    if element.tag == "app":
        text = ""
        for subelement in element:
            colour = "blue"
            if subelement.attrib['type'] == "corr":
                colour = "red"
            
            text += f" [{colour}]{element_to_text(subelement)}[/{colour}]"
    else:
        text = element_to_text(element)

    if "ntranscribed" in text:
        return ""
    return text
