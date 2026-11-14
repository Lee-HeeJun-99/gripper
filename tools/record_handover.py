"""Verify extracted originals byte-for-byte against each supplied ZIP."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    outer=list(ROOT.parent.glob('ReGrip_*.zip'))
    if len(outer)!=1:raise RuntimeError('expected exactly one incoming ReGrip ZIP')
    originals=ROOT/'handover/20261114'
    records=[]
    for archive in [outer[0]]+sorted(originals.glob('*.zip')):
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():continue
                path=originals/info.filename
                expected=z.read(info)
                actual=path.read_bytes()
                if expected!=actual:raise RuntimeError('original changed: '+str(path))
                records.append(dict(archive=archive.name,path=str(path.relative_to(ROOT)),
                                    sha256=hashlib.sha256(actual).hexdigest(),size=len(actual)))
    manifest=dict(outer_archive=outer[0].name,outer_sha256=hashlib.sha256(outer[0].read_bytes()).hexdigest(),
                  originals_match_archives=True,files=records)
    (originals/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
    print('Verified',len(records),'original archive members')


if __name__=='__main__':main()
