import hashlib,sys
from pathlib import Path
expected='5bfe18d164414e098b2ba6ef81bf9391f7ff8f2c39b8a4fa9f8543f778e921c8'
actual=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()
if actual!=expected:raise SystemExit("STOP: SHA256 dei sorgenti non corrispondente")
print("SHA256 sorgenti verificato:",actual)
