import typer
import re
from pathlib import Path
from lxml import etree
from rich.console import Console
from rich.table import Table
from rich import box
from .xml import *
from .download import get_cache_dir, download_compaul

console = Console()
app = typer.Typer()


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

    try:
        return int(ga) + s
    except Exception:
        pass

    return 0

@app.command()
def list(
    verse:str,
    directory:Path = None,
):
    """
    Looks for correctors in the XML files
    """
    if directory is None:
        directory = get_cache_dir()

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
    table.add_column("Siglum", style="magenta", justify="right")
    table.add_column("Text")
    for key, columns in sorted(data.items()):
        table.add_row(*columns)
    console.print( table )

    if not has_xml:
        console.print("No XML files found", style="red")
        return

@app.command()
def download(
):
    download_compaul()