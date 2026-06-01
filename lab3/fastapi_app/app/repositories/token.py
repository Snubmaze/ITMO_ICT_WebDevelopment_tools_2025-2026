_blacklist: set[str] = set()


async def is_blacklisted(token: str) -> bool:
    return token in _blacklist


async def add_to_blacklist(token: str) -> None:
    _blacklist.add(token)
