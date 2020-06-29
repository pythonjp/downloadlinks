import re
import typing
from urllib.parse import urljoin
import datetime
from dataclasses import dataclass

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

        # get release note
        relnote= urljoin(PYTHON_HOST, li.find(class_="release-enhancements").a['href'])
        
        rel = Release(release=rel, pre=m['pre'], date=date, download=download, relnote=relnote)
        rels.append(rel)

    return sorted(rels, key=lambda r:(r.release, r.pre, r.date), reverse=True)

print(get_releases())
