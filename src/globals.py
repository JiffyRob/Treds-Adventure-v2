"""
This module houses global variables and services accessed by the entirety of the game
Do NOT add variables to this unless it falls under these criteria or is approved upon talking with other developers:
  1) Will be used in almost all parts of the codebase
  2) Would have to be piped through at least 4 interfaces to reach its destination
  3) Inherantly there should only be one of them

All variables here to be modified in the "global state setting" section of the main.Game.__init__() function
"""

player = None  # player object, to be phased out
engine = None
