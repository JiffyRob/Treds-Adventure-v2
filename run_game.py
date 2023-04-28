import asyncio
import os
import sys

os.chdir("src")
sys.path.append("src")

import main

asyncio.run(main.Game().run())
