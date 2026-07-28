import os
import re
import urllib.request

BASE_URL = "http://lplan.steadyinfo.net"

files = [
    "/static/assets/css/main.css",
    "/static/assets/css/noscript.css",
    "/static/assets/js/jquery.min.js",
    "/static/assets/js/jquery.scrollex.min.js",
    "/static/assets/js/jquery.scrolly.min.js",
    "/static/assets/js/browser.min.js",
    "/static/assets/js/breakpoints.min.js",
    "/static/assets/js/util.js",
    "/static/assets/js/main.js",
    "/static/images/planner.jpg",
    "/static/images/spotlight01.jpg",
    "/static/images/spotlight02.jpg",
    "/static/images/spotlight03.jpg",
]

for i in range(1, 7):
    files.append(f"/static/images/gallery/thumbs/0{i}.jpg")
    files.append(f"/static/images/gallery/fulls/0{i}.jpg")

for file_path in files:
    local_path = file_path.lstrip('/')
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    url = BASE_URL + file_path
    try:
        urllib.request.urlretrieve(url, local_path)
        print(f"Downloaded: {file_path} ({os.path.getsize(local_path)} bytes)")
    except Exception as e:
        print(f"Failed {file_path}: {e}")

# Parse main.css for webfonts and relative assets
main_css_path = "static/assets/css/main.css"
if os.path.exists(main_css_path):
    with open(main_css_path, "r", encoding="utf-8", errors="ignore") as f:
        css_content = f.read()

    # Find url(...) references
    matches = re.findall(r'url\((["\']?)(.*?)\1\)', css_content)
    for quote, rel_url in matches:
        if rel_url.startswith("data:"):
            continue
        # Clean relative URL
        clean_url = rel_url.split("?")[0].split("#")[0]
        if clean_url.startswith("../"):
            target_path = "static/assets/" + clean_url[3:]
            url = BASE_URL + "/" + target_path
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            try:
                urllib.request.urlretrieve(url, target_path)
                print(f"Downloaded CSS asset: {target_path}")
            except Exception as e:
                print(f"Failed CSS asset {target_path}: {e}")

print("Assets download process finished.")
