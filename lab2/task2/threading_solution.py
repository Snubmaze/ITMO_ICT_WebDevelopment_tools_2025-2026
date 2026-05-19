import threading
import time
import uuid
import requests
import psycopg2
from bs4 import BeautifulSoup

DB_DSN = "postgresql://postgres:password@localhost/teamfinder"

URLS = [
    "https://stackoverflow.com/tags?page=1&tab=popular",
    "https://stackoverflow.com/tags?page=2&tab=popular",
    "https://stackoverflow.com/tags?page=3&tab=popular",
    "https://stackoverflow.com/tags?page=4&tab=popular",
    "https://github.com/topics?page=1",
    "https://github.com/topics?page=2",
    "https://github.com/topics?page=3",
    "https://github.com/topics?page=4",
    "https://en.wikipedia.org/wiki/List_of_programming_languages#0",
    "https://en.wikipedia.org/wiki/List_of_programming_languages#1",
    "https://en.wikipedia.org/wiki/List_of_programming_languages#2",
    "https://en.wikipedia.org/wiki/List_of_programming_languages#3",
]

NUM_THREADS = 4
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; lab2-scraper/1.0)"}

db_lock = threading.Lock()


def get_connection():
    return psycopg2.connect(DB_DSN)


def parse_url(url: str) -> list[str]:
    """Загружает страницу и возвращает список названий навыков."""
    clean_url = url.split("#")[0]
    resp = requests.get(clean_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    if "stackoverflow.com" in url:
        tags = soup.find_all("a", class_="post-tag")
        return [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]

    if "github.com/topics" in url:
        items = soup.find_all("p", class_=lambda c: c and "f3" in c.split())
        return [p.get_text(strip=True) for p in items if p.get_text(strip=True)]

    if "wikipedia.org" in url:
        fragment = url.split("#")[-1] if "#" in url else "0"
        slice_idx = int(fragment) if fragment.isdigit() else 0

        content = soup.find("div", class_="mw-parser-output")
        if not content:
            return []
        skills = []
        for li in content.find_all("li"):
            a = li.find("a")
            if a:
                name = a.get_text(strip=True)
                if name and len(name) <= 100 and not name.startswith("["):
                    skills.append(name)

        chunk = max(len(skills) // 4, 1)
        start = slice_idx * chunk
        end = start + chunk if slice_idx < 3 else len(skills)
        return skills[start:end]

    return []


def save_skills(conn, skills: list[str]):
    with conn.cursor() as cur:
        for name in skills:
            cur.execute(
                "INSERT INTO skills (id, name) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (str(uuid.uuid4()), name),
            )
    conn.commit()


def parse_and_save(url: str):
    try:
        skills = parse_url(url)
        with db_lock:
            conn = get_connection()
            try:
                save_skills(conn, skills)
            finally:
                conn.close()
        print(f"[Threading] ✓ {len(skills):>3} навыков  ←  {url}")
    except Exception as e:
        print(f"[Threading] ✗ {url}: {e}")


def worker(urls_chunk: list):
    for url in urls_chunk:
        parse_and_save(url)


def main():
    chunk_size = len(URLS) // NUM_THREADS
    chunks = [URLS[i * chunk_size: (i + 1) * chunk_size] for i in range(NUM_THREADS)]
    if len(URLS) % NUM_THREADS:
        chunks[-1].extend(URLS[NUM_THREADS * chunk_size:])

    threads = []
    start = time.perf_counter()

    for chunk in chunks:
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"\n[Threading] Готово. Время: {time.perf_counter() - start:.4f} сек | Потоков: {NUM_THREADS}")


if __name__ == "__main__":
    main()
