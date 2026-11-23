from pathlib import Path
import json
import urllib.request

BASE = Path(__file__).resolve().parent
url = "https://api.github.com/repos/leanprover/lean4/releases/tags/v4.35.0-rc2"
request = urllib.request.Request(url, headers={"User-Agent": "Conway99-local-verification"})
with urllib.request.urlopen(request) as response:
    data = json.load(response)
assets = [a for a in data["assets"] if "linux" in a["name"] and "aarch64" not in a["name"]]
record = {"tag": data["tag_name"], "url": data["html_url"],
          "assets": [{k: a.get(k) for k in ("name", "size", "digest", "browser_download_url")}
                     for a in assets]}
(BASE / "lean_release_metadata.json").write_text(json.dumps(record, indent=4))
print(json.dumps(record, indent=2))
