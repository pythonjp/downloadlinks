import re
import typing
from urllib.parse import urljoin
import datetime
from dataclasses import dataclass
from collections import defaultdict
import re

import yaml

import requests
from bs4 import BeautifulSoup
import dateutil.parser

PYTHON_HOST = 'https://www.python.org'
DOWNLOADS = f'{PYTHON_HOST}/downloads/'

# from https://www.python.org/dev/peps/pep-0440/

VERSION_PATTERN = r"""(python)*\s*
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""

RE_VERSION = re.compile(
    r"^\s*" + VERSION_PATTERN + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)


@dataclass
class Release:
    release: typing.Tuple[int, int, int]
    pre: typing.Optional[str]
    date: datetime.date
    download: str
    relnote: str
    files: typing.List[typing.Dict[str, str]]

def get_files(url):
    html = requests.get(url).text
    links = BeautifulSoup(html, features="html.parser").select("td a")

    ret = []
    for link in links:
        text = ""
        if re.search(r"(Windows x86-64 executable installer)|(Windows x86-64 MSI installer)", link.text):
            text = "windows64"
        elif re.search(r"(Windows x86 executable installer)|(Windows x86 MSI installer)", link.text):
            text = "windows32"
        elif re.search(r"XZ compressed source tarball", link.text):
            text = "source"
        elif re.search(r"Gzipped source tarball", link.text):
            if not text:
                text = "source"
        elif re.search(r"(macOS 64-bit installer)|(Mac OS X 64-bit/32-bit installer)", link.text):
            text = "macos"



        if text:
            ret.append({text: link["href"]})

    return ret


def get_releases():
    html = requests.get(DOWNLOADS).text
    lis = BeautifulSoup(html, features="html.parser").select(".download-list-widget li")

    rels = []
    for li in lis:
        # get version number
        rel = li.find(class_='release-number')
        m = RE_VERSION.search(rel.text.strip())
        rel = tuple(int(v) for v in m['release'].split('.'))

        # get release date
        text_date = li.find(class_="release-date").text.strip()
        date = dateutil.parser.parse(text_date).date()

        # get download link
        download = urljoin(PYTHON_HOST, li.find(class_="release-download").a['href'])

        files = get_files(download)
        
        # get release note
        relnote= urljoin(PYTHON_HOST, li.find(class_="release-enhancements").a['href'])
        
        rel = Release(release=rel, pre=m['pre'], date=date, download=download, relnote=relnote, files=files)
        rels.append(rel)

    return sorted(rels, key=lambda r:(r.release, r.pre, r.date), reverse=True)

def save(rels):
    all = defaultdict(list)
    for rel in rels:
        d = {
            'version': ".".join(str(r) for r in rel.release),
            'date': str(rel.date),
            'info': rel.download,
        }
        for file in rel.files:
            d.update(file)

        all[".".join(str(r) for r in rel.release[:2])].append(d)


    rels = [{'majorversion': k, 'releases': v} for k, v in all.items()]
    return rels

rels = get_releases()
ret = save(rels)

print(yaml.dump({'python_versions': ret}, Dumper=yaml.Dumper))

