#!/usr/bin/env python3
"""Prepare pinned, verified rendering sources in this package's overlay."""
from pathlib import Path
import hashlib, tarfile, urllib.request, subprocess, sys
kit=Path(__file__).resolve().parents[1]
cache=kit/'overlay/downloads';cache.mkdir(parents=True,exist_ok=True)
archive=cache/'gz-rendering-8.2.3.tar.gz'
url='https://codeload.github.com/gazebosim/gz-rendering/tar.gz/refs/tags/gz-rendering8_8.2.3'
expected='5bfe18d164414e098b2ba6ef81bf9391f7ff8f2c39b8a4fa9f8543f778e921c8'
if not archive.exists():urllib.request.urlretrieve(url,archive)
if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:sys.exit('Source SHA256 mismatch; stop.')
source=kit/'overlay/source/gz-rendering'
if source.exists():sys.exit('Source directory already exists. Use a new copy of the archive to rebuild.')
source.mkdir(parents=True);(source.parent/'COLCON_IGNORE').touch()
with tarfile.open(archive) as t:
 for member in t.getmembers():
  parts=Path(member.name).parts[1:]
  if not parts:continue
  member.name=str(Path(*parts));t.extract(member,source,filter='data')
patches=[kit/'overlay/src/gz_rendering_vendor/patches/0001-Add-OgreNext-vendor-package.patch',*sorted(p for p in (kit/'patches').glob('*.patch') if not p.name.startswith('.'))]
for patch in patches:subprocess.run(['git','apply','--check',str(patch)],cwd=source,check=True);subprocess.run(['git','apply',str(patch)],cwd=source,check=True)
print(source)
