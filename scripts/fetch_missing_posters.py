from pathlib import Path
from io import BytesIO
import requests
from PIL import Image, ImageOps

SOURCES = {
    12: [
        "https://s3.amazonaws.com/criterion-production/films/34e65cf527a81c5635a889541a2f499c/frUwKXMtUOoA2izF8DCHzw8kM06yLX_large.jpg",
        "https://img.myvideo.net.tw/images/LOT010/0000/0196/202312080931217394.jpg",
    ],
    56: [
        "https://hotori.jp/storage/movies/662/poster.jpg?v=1782467878",
        "https://www.hadashi-movie.com/img/main_img_sp.jpg",
    ],
}

OUT = Path("posters")
OUT.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/155 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
})

failed = []
for movie_id, urls in SOURCES.items():
    dest = OUT / f"{movie_id}.webp"
    ok = False
    for url in urls:
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = ImageOps.exif_transpose(img)
            img.thumbnail((720, 1080), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (720, 1080), "#eee5dc")
            # Fit without cropping so poster artwork isn't cut off.
            fitted = ImageOps.contain(img, (720, 1080), Image.Resampling.LANCZOS)
            x = (720 - fitted.width) // 2
            y = (1080 - fitted.height) // 2
            canvas.paste(fitted, (x, y))
            canvas.save(dest, "WEBP", quality=78, method=6)
            print(f"OK {movie_id}: {url} -> {dest.stat().st_size} bytes")
            ok = True
            break
        except Exception as e:
            print(f"FAIL {movie_id}: {url} :: {e}")
    if not ok:
        failed.append(movie_id)

print("FAILED_IDS=" + ",".join(map(str, failed)))
if failed:
    raise SystemExit(1)
