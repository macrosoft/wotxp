import py_compile, zipfile, os

WOTVersion = "0.9.15"

if os.path.exists("wotxp.zip"):
    os.remove("wotxp.zip")

py_compile.compile("src/mod_wotxp.py")

fZip = zipfile.ZipFile("wotxp.zip", "w")
fZip.write("src/mod_wotxp.pyc", WOTVersion+"/scripts/client/gui/mods/mod_wotxp.pyc")
fZip.write("data/mod_wotxp.json", WOTVersion+"/scripts/client/gui/mods/mod_wotxp.json")
fZip.close()
