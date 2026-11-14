"""Verify extracted originals byte-for-byte against each supplied ZIP."""
import hashlib
import json
from pathlib import Path
import zipfile
import argparse

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,help='Optional new audit output outside handover; originals are read-only')
    args=parser.parse_args()
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
    if args.out is not None:
        output=args.out.resolve()
        if output.is_relative_to(ROOT/'handover'):raise ValueError('audit output must be outside handover')
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x') as stream:stream.write(json.dumps(manifest,indent=2,ensure_ascii=False))
    print('Verified',len(records),'original archive members')


if __name__=='__main__':main()
