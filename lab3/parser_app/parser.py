import aiohttp
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; lab3-scraper/1.0)"}


async def parse_url(url: str) -> list[str]:
    clean_url = url.split("#")[0]
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession() as session:
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

    links = soup.find_all("a")
    return [a.get_text(strip=True) for a in links if a.get_text(strip=True)][:50]