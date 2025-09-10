import requests
import os
import platform
import sys
from datetime import datetime, UTC
from urllib.parse import urlsplit


API_KEY = "cji0O8JFE0ySmZmXajp8tkZckylj1ZG7jcZZr6eN"
APOD_URL = "https://api.nasa.gov/planetary/apod"
TIMEOUT = 10

def open_file_with_default_app(path: str) -> None:
    if platform.system() == 'Windows':
        os.startfile(path)
    else:
        print("Error. Run on Windows Machine")


def download_file(url:str, filename: str, timeout: int = TIMEOUT) -> None:
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    with open(filename, "wb") as fh:
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                fh.write(chunk)


def fetch_apod(api_key: str = API_KEY, date: str | None = None, count: int | None = None, hd: bool = True):
    params = {"api_key": api_key}
    if count:
        params["count"] = count
    elif date:
        try:
            datetime.strptime(date, "%y-%m-%d")
        except ValueError:
            raise ValueError("date must be in YYY-MM-DD format")
        params["date"] = date
        if hd:
            params["hd"] = "True"

    resp = requests.get(APOD_URL, params=params, timeout = TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def main():
    try:
        data = fetch_apod()
    except requests.exceptions.RequestException as e:
        print("Network/API error:", e)
        sys.exit(1)


    results = data if isinstance(data, list) else[data]

    for idx, item in enumerate(results, start=1):
        print(f"\n=== APOD#{idx} ===")
        print("Title:", item.get("title"))
        print("Date:", item.get("date:"))
        print("Media type:", item.get("media_type"))
        print("Copyright:", item.get("copyright", "Public Domain / N/A"))
        print("Explanation:", item.get("explanation", "")[:400]+ ("..." if len(item.get("explanation", ""))>400 else ""))
        url = item.get("hdurl") or item.get("url")
        if not url:
            print("No URL returned for this APOD")

        if item.get("media_type") == "video" :
            print("APOD is a video. URL:", url)
            continue

        try:
            parsed = urlsplit(url)
            basename = os.path.basename(parsed.path)
            date_part = item.get("date", datetime.now(UTC).strftime("%Y-%m-%d"))
            filename = f"apod_{date_part}_{basename}"
            print("Donwloading image:", url)
            download_file(url, filename)
            print("Saved to", filename)
            open_file_with_default_app(filename)
        except requests.exceptions.RequestException as e:
            print ("Failed to download image:", e)
        except Exception as e:
            print("Unexpected error while saving/opening image:", e)

if __name__ == "__main__":
    main()