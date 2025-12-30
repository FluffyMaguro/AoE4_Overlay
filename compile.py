"""
This manages compiling the app with Nuitka and packaging it

"""

import json
import os
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

# Get version
try:
    with open('version.json', 'r') as f:
        data = json.load(f)
        VERSION = data['version']
except Exception:
    VERSION = "1.0.0"
    print("Failed to read version.json")

# Run nuitka
os.system(f'cmd /c "python -m nuitka'
          f' --plugin-enable=pyqt5'
          f' --standalone'
          f' --windows-disable-console'
          f' --windows-icon-from-ico=src/img/aoe4_sword_shield.ico'
          f' --company-name="FluffyMaguro"'
          f' --product-name="AoE4 Overlay"'
          f' --file-version={VERSION}'
          f' --product-version={VERSION}'
          f' --file-description="Overlay for Age of Empires IV"'
          f' --copyright="Copyright © 2023 FluffyMaguro"'
          f' --assume-yes-for-downloads'
          f' --nofollow-import-to=tkinter'
          f' --nofollow-import-to=unittest'
          f' --include-data-dir=src/img=img'
          f' --include-data-dir=src/html=html'
          f' src/AoE4_Overlay.py"')

# Zip
file_name = f"AoE4_Overlay.zip"

to_zip = []
folder = 'AoE4_overlay.dist'
for root, directories, files in os.walk(folder):
    for f in files:
        to_zip.append(os.path.join(root, f))

print('Compressing files...')
with ZipFile(file_name, 'w', compression=ZIP_DEFLATED) as zip:
    for f in to_zip:
        if "custom.js" in f or "custom.css" in f:
            continue
        zip.write(f, f"AoE4_Overlay/{f[len(folder)+1:]}")

# Cleanup
for item in (folder, ):
    if os.path.isdir(item):
        shutil.rmtree(item)
