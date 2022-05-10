import re
from pathlib import Path
from appdirs import user_cache_dir
import urllib.request
from lxml import etree

from .xml import strip_namespace

def get_cache_dir():
    return Path(user_cache_dir("igntpview"))

def get_cached_path(filename, directory:Path=None):
    if directory is None:
        directory = get_cache_dir()

    path = directory / filename
    path.parent.mkdir(exist_ok=True, parents=True)
    return path

class DownloadError(Exception):
    pass

def cached_download(url: str, filename: str, directory:Path=None, force=False) -> Path:
    local_path = get_cached_path(filename, directory=directory)
    cached_download_path(url, local_path, force=force)
    return local_path


def cached_download_path(url: str, local_path: Path, force=False) -> None:
    """
    Downloads a file if a local file does not already exist.

    Args:
        url: The url of the file to download.
        local_path: The local path of where the file should be. If this file isn't there or the file size is zero then this function downloads it to this location.

    Raises:
        Exception: Raises an exception if it cannot download the file.

    """
    local_path = Path(local_path)
    needs_download = force or (not local_path.exists() or local_path.stat().st_size == 0)
    if needs_download:
        try:
            print(f"Downloading {url} to {local_path}")
            urllib.request.urlretrieve(url, local_path)
        except Exception:
            raise DownloadError(f"Error downloading {url}")

    if not local_path.exists() or local_path.stat().st_size == 0:
        raise IOError(f"Error reading {local_path}")


def read_cached_download(url: str, filename: str, directory:Path=None, force=False) -> str:
    local_path = cached_download(url, filename, force=force, directory=directory)
    with open(local_path, 'r') as f:
        contents = f.read()
    print(f"File read at {local_path}")
    return contents

def read_cached_xml(url: str, filename: str, directory:Path=None, force:bool = False):
    local_path = cached_download(url, filename, force=force, directory=directory)
    parser = etree.XMLParser(ns_clean=True, recover=True)
    tree = etree.parse(str(local_path), parser)
    tree = tree.getroot()
    strip_namespace(tree)
    return tree

def download_compaul():
    
    url = "https://itseeweb.cal.bham.ac.uk/epistulae/XML/NTstart.xsl"
    # print(read_cached_download(url, "NTstart.xml"))

    tree = read_cached_xml("https://itseeweb.cal.bham.ac.uk/epistulae/XML/compaul-start.xsl", "compaul-start.xsl")
    for option in tree.findall(".//option[@value]"):
        value = option.attrib['value']
        m = re.match(r".*\.xml$", value)
        if m:
            print(m.group(0))
            url = f"https://itseeweb.cal.bham.ac.uk/epistulae/XML/{m.group(0)}"

            try:
                cached_download( url, m.group(0))
            except Exception as err:
                print(f"Cannot download {url}: {err}")