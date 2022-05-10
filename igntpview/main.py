import typer
import re
from pathlib import Path
from bs4 import BeautifulSoup
from appdirs import user_cache_dir
from lxml import etree
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
console = Console()
from rich import box

app = typer.Typer()

def strip_namespace(el):
    if hasattr(el, "tag") and "}" in el.tag:
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


def ga_to_intf(ga):
    if ga.startswith("P"):
        s = 10000
        ga = ga[1:]
    elif ga.startswith("L"):
        s = 40000
        ga = ga[1:]
    elif ga.startswith("0"):
        s = 20000
    else:
        s = 30000

    return int(ga) + s

@app.command()
def main(
    verse:str,
    directory:Path = None,
):
    """
    Looks for correctors in the XML files
    """
    if directory is None:
        directory = Path(user_cache_dir("dcodex-bible"))/"IGNTP/06-Romans"

    xmls = directory.glob('*.xml')

    data = {}
    has_xml = False
    for xml in xmls:
        has_xml = True
        parser = etree.XMLParser(ns_clean=True, recover=True)
        tree = etree.parse(str(xml), parser)
        tree = tree.getroot()
        strip_namespace(tree)

        title = tree.find(".//title[@n]")
        if title is not None and 'n' in title.attrib:
            siglum = title.attrib['n']
        else:
            siglum = xml.name

        verse_element = tree.find(f".//ab[@n='{verse}']")
        if verse_element is not None:
            words = [element_to_text_coloured(word).replace("\n", "") for word in verse_element]
            verse_text = " ".join(words)
            verse_text = re.sub(r"\s+", ' ', verse_text )
            
            data[ ga_to_intf(siglum) ] = [siglum, verse_text]
            # break

    table = Table(show_header=True, box=box.SIMPLE)
    # table.add_column("INTF ID", style="magenta", justify="right")
    table.add_column("GA", style="green", justify="right")
    table.add_column("Text")
    for key, columns in sorted(data.items()):
        table.add_row(*columns)
    console.print( table )

    if not has_xml:
        console.print("No XML files found", style="red")
        return
