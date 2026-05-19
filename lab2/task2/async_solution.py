import asyncio
import time
import uuid
import asyncpg
import aiohttp
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

NUM_WORKERS = 4
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; lab2-scraper/1.0)"}


async def parse_url(session: aiohttp.ClientSession, url: str) -> list[str]:
    clean_url = url.split("#")[0]
    timeout = aiohttp.ClientTimeout(total=15)
    async with session.get(clean_url, headers=HEADERS, timeout=timeout) as resp:
        resp.raise_for_status()
        html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

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


async def save_skills(pool: asyncpg.Pool, skills: list[str]):
    async with pool.acquire() as conn:
        async with conn.transaction():
            for name in skills:
                await conn.execute(
                    "INSERT INTO skills (id, name) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING",
                    uuid.uuid4(),
                    name,
                )


async def parse_and_save(session: aiohttp.ClientSession, pool: asyncpg.Pool, url: str):
    try:
        skills = await parse_url(session, url)
        await save_skills(pool, skills)
        print(f"[Async] ✓ {len(skills):>3} навыков  ←  {url}")
    except Exception as e:
        print(f"[Async] ✗ {url}: {e}")


async def worker(session: aiohttp.ClientSession, pool: asyncpg.Pool, urls_chunk: list):
    for url in urls_chunk:
        await parse_and_save(session, pool, url)


async def main():
    chunk_size = len(URLS) // NUM_WORKERS
    chunks = [URLS[i * chunk_size: (i + 1) * chunk_size] for i in range(NUM_WORKERS)]
    if len(URLS) % NUM_WORKERS:
        chunks[-1].extend(URLS[NUM_WORKERS * chunk_size:])

    pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=NUM_WORKERS)

    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[worker(session, pool, chunk) for chunk in chunks])

    await pool.close()
    print(f"\n[Async] Готово. Время: {time.perf_counter() - start:.4f} сек | Воркеров: {NUM_WORKERS}")


if __name__ == "__main__":
    asyncio.run(main())
