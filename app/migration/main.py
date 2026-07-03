import sys
import asyncio

from app.migration.cli_migrator import main

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))