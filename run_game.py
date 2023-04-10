import os
import sys

os.chdir("src")
sys.path.append("src")

import main

main.Game().run()
