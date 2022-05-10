from itertools import count
import typer
import re
from pathlib import Path
from lxml import etree
from rich.console import Console
from rich.table import Table
from rich import box
from .xml import *
from .download import get_cache_dir, download_latin, download_greek
from rich.progress import track

console = Console()
app = typer.Typer()


def walk_xml(path): 
    for p in Path(path).iterdir(): 
        if p.is_dir(): 
            yield from walk_xml(p)
        elif p.suffix == ".xml":
            yield p.resolve()

def ga_to_intf(ga):
    ga=str(ga)
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
    greek:bool = True,
    latin:bool = True,
):
    """
    Looks for correctors in the XML files
    """
    if directory is None:
        directory = get_cache_dir()

    xmls = [x for x in walk_xml(directory)]


    data = {}
    has_xml = False
    for index, xml in track(enumerate(xmls), description="Processing...", total=len(xmls)):
        has_xml = True

        with open(xml, 'r') as f:
            filetext = f.read()
            if verse not in filetext:
                continue

        parser = etree.XMLParser(ns_clean=True, recover=True)
        tree = etree.parse(str(xml), parser)
        tree = tree.getroot()
        strip_namespace(tree)

        language = ""
        for text in tree.findall(".//text"):
            for attrib in text.attrib:
                if "lang" in attrib:
                    language = text.attrib[attrib]

        if language:
            if not greek and language == "grc":
                continue
            if not latin and language == "lat":
                continue

        title = tree.find(".//title[@n]")
        number = 0
        if title is not None and 'n' in title.attrib:
            siglum = title.attrib['n'] 
            if language == "lat" and greek:
                siglum += " (Lat)"
            if language == "grc":
                number = ga_to_intf(title.attrib['n'])
            else:
                m = re.search("\d+", title.attrib['n'])
                if m:
                    number = 100_000 + int(m.group(0))
                else:
                    number = 1_000_000 + index
        else:
            siglum = xml.name

        verse_element = tree.find(f".//ab[@n='{verse}']")
        if verse_element is not None:
            words = [element_to_text_coloured(word).replace("\n", "") for word in verse_element]
            verse_text = " ".join(words)
            verse_text = re.sub(r"\s+", ' ', verse_text )
            
            data[ number ] = [siglum, verse_text]
            # break

    table = Table(show_header=True, box=box.SIMPLE)
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
    greek:bool = True,
    latin:bool = False,
):
    if greek:
        download_greek()

    if latin:
        download_latin()