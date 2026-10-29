from pathlib import Path
import tarfile,json,difflib,hashlib
root=Path(__file__).resolve().parent
archive=root/'gz-rendering-8.2.3.tar.gz'
if hashlib.sha256(archive.read_bytes()).hexdigest() != '5bfe18d164414e098b2ba6ef81bf9391f7ff8f2c39b8a4fa9f8543f778e921c8': raise SystemExit('Source hash mismatch')
with tarfile.open(archive) as t:
 def read(name):return t.extractfile(next(m for m in t.getmembers() if m.name.endswith('/ogre/src/'+name))).read().decode()
 base=read('OgreGpuRays.cc');light=read('OgreLight.cc')
(root/'OgreLight.original.cc').write_text(light)
def center(s):
 return s.replace('double startX = dx;','double startX = dx / 2.0;').replace('double startY = this->dataPtr->h2nd/10.0;','double startY = (this->dataPtr->h2nd - 0.5) / 10.0;').replace('startX = 0;','startX = -dx / 2.0;')
def uv(s):return s.replace('double v = 0.5 - (tan(gamma) * cos(theta)) /\n          (2.0 * tan(phiCamera) * cos(delta));','double v = 0.5;\n      if (this->VerticalRangeCount() > 1u)\n        v -= (tan(gamma) * cos(theta)) /\n          (2.0 * tan(phiCamera) * cos(delta));')
def orientation(s):
 s=s.replace('cameraYaws[4]','cameraYaws[3]')
 s=s.replace('this->dataPtr->cameraYaws[1] = +this->HFOV().Radian();\n    this->dataPtr->cameraYaws[2] = 0;\n    this->dataPtr->cameraYaws[3] = -this->HFOV().Radian() / 2.0;','this->dataPtr->cameraYaws[1] = +this->HFOV().Radian() / 2.0;')
 s=s.replace('this->dataPtr->cameraYaws[1] = +this->HFOV().Radian();\n    this->dataPtr->cameraYaws[2] = +this->HFOV().Radian();\n    this->dataPtr->cameraYaws[3] = -this->HFOV().Radian();','this->dataPtr->cameraYaws[1] = 0;\n    this->dataPtr->cameraYaws[2] = +this->HFOV().Radian();')
 s=s.replace('  for (unsigned int i = 0; i < this->dataPtr->textureCount; ++i)\n  {\n    if (this->dataPtr->textureCount > 1)','  Ogre::Quaternion initialOrientation;\n  if (this->dataPtr->textureCount > 1) initialOrientation = this->Node()->getOrientation();\n  for (unsigned int i = 0; i < this->dataPtr->textureCount; ++i)\n  {\n    if (this->dataPtr->textureCount > 1)')
 s=s.replace('      this->Node()->roll(Ogre::Radian(this->dataPtr->cameraYaws[i]));','      this->Node()->setOrientation(initialOrientation);\n      this->Node()->roll(Ogre::Radian(this->dataPtr->cameraYaws[i]));')
 s=s.replace('this->Node()->roll(Ogre::Radian(this->dataPtr->cameraYaws[3]));','this->Node()->setOrientation(initialOrientation);')
 return s
def pad(s,n):
 s=s.replace('this->SetRayCountRatio(horzRangeCountPerCamera);',f'this->SetRayCountRatio(horzRangeCountPerCamera / (vertRangeCountPerCamera == 1u ? {n}.0 : 1.0));')
 s=s.replace('this->dataPtr->h1st = _h;',f'this->dataPtr->h1st = (_h == 1u ? {n}u : _h);').replace('this->dataPtr->h2nd = _h;',f'this->dataPtr->h2nd = (_h == 1u ? {n}u : _h);')
 a=s.index('void OgreGpuRays::PostRender()');b=s.index('const float* OgreGpuRays::Data()',a);part=s[a:b]
 part=part.replace('unsigned int height = secondPassViewport->getActualHeight();','unsigned int physicalHeight = secondPassViewport->getActualHeight();\n  unsigned int height = this->VerticalRangeCount();').replace('int len = width * height * this->Channels();','int len = width * physicalHeight * this->Channels();').replace('Ogre::PixelBox dstBox(width, height,','Ogre::PixelBox dstBox(width, physicalHeight,').replace('memcpy(this->dataPtr->gpuRaysScan, this->dataPtr->gpuRaysBuffer, size);','auto source = this->dataPtr->gpuRaysBuffer;\n  if (height == 1u && physicalHeight > 1u) source += (physicalHeight / 2u) * width * this->Channels();\n  memcpy(this->dataPtr->gpuRaysScan, source, size);')
 s=s[:a]+part+s[b:];a=s.index('void OgreGpuRays::Copy(');b=s.index('void OgreGpuRays::CreateOrthoCam()',a);part=s[a:b].replace('unsigned int height = secondPassViewport->getActualHeight();','unsigned int height = this->VerticalRangeCount();');s=s[:a]+part+s[b:]
 return s
variants={'stock':base,'center':center(base),'uv':uv(base),'center_uv':uv(center(base)), 'pad2':pad(uv(center(base)),2),'pad3':pad(uv(center(base)),3),'upstream':orientation(center(base)),'upstream_uv':uv(orientation(center(base)))}
for name,s in variants.items():
 p=root/'variants'/name;p.mkdir(parents=True,exist_ok=True);(p/'OgreGpuRays.cc').write_text(s)
 (p/'changes.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile='a/ogre/src/OgreGpuRays.cc',tofile='b/ogre/src/OgreGpuRays.cc')))
print('Prepared variants:',','.join(variants))
