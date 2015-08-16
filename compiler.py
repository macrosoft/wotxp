import py_compile, zipfile, os

WOTVersion = "0.9.10 Common Test"

if os.path.exists("wotxp.zip"):
    os.remove("wotxp.zip")

py_compile.compile("src/__init__.py")
py_compile.compile("src/CameraNode.py")
py_compile.compile("src/wotxp.py")

fZip = zipfile.ZipFile("wotxp.zip", "w")
fZip.write("src/__init__.pyc", WOTVersion+"/scripts/client/mods/__init__.pyc")
fZip.write("src/wotxp.pyc", WOTVersion+"/scripts/client/mods/wotxp.pyc")
fZip.write("src/CameraNode.pyc", WOTVersion+"/scripts/client/CameraNode.pyc")
fZip.write("data/wotxp.json", WOTVersion+"/scripts/client/mods/wotxp.json")
fZip.close()
