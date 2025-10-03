import asyncio
from .database import init_db
from .glassdoor import search_glassdoor

async def main():
    init_db()
    await search_glassdoor()

if __name__ == "__main__":
    asyncio.run(main())
