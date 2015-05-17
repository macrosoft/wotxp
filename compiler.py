import py_compile, zipfile, os

WOTVersion = "0.9.8 Common Test"

if os.path.exists("wotcrew.zip"):
    os.remove("wotcrew.zip")

py_compile.compile("src/__init__.py")
py_compile.compile("src/CameraNode.py")
py_compile.compile("src/wotcrew.py")

fZip = zipfile.ZipFile("wotcrew.zip", "w")
fZip.write("src/__init__.pyc", WOTVersion+"/scripts/client/mods/__init__.pyc")
fZip.write("src/wotcrew.pyc", WOTVersion+"/scripts/client/mods/wotcrew.pyc")
fZip.write("src/CameraNode.pyc", WOTVersion+"/scripts/client/CameraNode.pyc")
fZip.close()
