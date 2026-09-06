import os
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import requests

MANIFEST = "https://mirror.guweh.com/images.json"
OUT = "downloads"
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif")

def walk(node):
    """recursively rip every string out of whatever cursed shape the json is"""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from walk(v)

s = requests.Session()
s.headers["User-Agent"] = "lamp/1.0"
out_root = os.path.abspath(OUT)

def grab(path):
    url = urljoin(MANIFEST, path)
    rel = urlparse(url).path.lstrip("/")
    dest = os.path.abspath(os.path.join(OUT, rel))
    if not dest.startswith(out_root + os.sep):
        return  # someone put ../../etc/passwd in the json, nice try
    if os.path.exists(dest):
        return  # already got it, skip
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with s.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(65536):
                f.write(chunk)
    os.replace(tmp, dest)

seen = set()
queue = [MANIFEST]
images = []

while queue:
    m = queue.pop()
    if m in seen:
        continue
    seen.add(m)
    data = s.get(m, timeout=30).json()
    for p in walk(data):
        u = urljoin(m, p)
        if u.lower().endswith(".json"):
            queue.append(u)
        elif u.lower().endswith(EXTS):
            images.append(u)

with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(grab, images))