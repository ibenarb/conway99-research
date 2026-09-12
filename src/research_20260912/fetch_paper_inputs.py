"""Fetch pinned arXiv inputs; refuse a changed version rather than silently audit it."""
from pathlib import Path
from urllib.request import urlopen
from io import BytesIO
import hashlib,tarfile
base=Path(__file__).resolve().parents[2]/'data/research_20260912'
base.mkdir(parents=True,exist_ok=True)
def save(name,data,expected):
    actual=hashlib.sha256(data).hexdigest()
    if actual!=expected:raise ValueError(f'{name}: source changed: {actual}; expected {expected}')
    (base/name).write_bytes(data)
    print('PASS_SOURCE_HASH',name,actual)
html=urlopen('https://arxiv.org/html/2608.19410v1',timeout=60).read()
save('reimbayev.html',html,'09377f0b08646cfd92c847f76ee342805161f2480f8d3bbf49a95b4d52ff33af')
raw=urlopen('https://arxiv.org/src/2608.19410v1',timeout=60).read()
with tarfile.open(fileobj=BytesIO(raw),mode='r:*') as archive:
    member=next(m for m in archive.getmembers() if m.name.split('/')[-1]=='The_Subgraphs_of_Order_Seven.tex')
    tex=archive.extractfile(member).read()
save('reimbayev_source.tex',tex,'d2c0c9d8985a19c6f5418eed38ecff6b9b4d177c6359b4f2df799453cd2530e9')
