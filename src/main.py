import asyncio
import sys
from .database import init_db
from .glassdoor import search_glassdoor

async def main():
    init_db()
    await search_glassdoor()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except SystemExit as e:
        if e.code == 2:
            import os
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            raise
