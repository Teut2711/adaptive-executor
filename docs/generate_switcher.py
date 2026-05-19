import json
from pathlib import Path

import tomllib

# Read version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)
    version = data["project"]["version"]

# Take only major.minor (e.g. 0.3)
short_version = ".".join(version.split(".")[:2])

switcher = [{"name": f"{short_version} (latest)", "version": short_version, "url": "/"}]

Path("docs/_static").mkdir(parents=True, exist_ok=True)
Path("docs/_static/switcher.json").write_text(json.dumps(switcher, indent=2))
print(f"Generated switcher.json for version {short_version}")
