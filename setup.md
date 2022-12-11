# Intro
Welcome to the development team!  Here is how to set things up to get coding.  THe code is done in python3.10+ and pygame 2.  Code goals are simplicity, scalability, readability, and performance.
# Setup
1. Install Python https://python.org/download (make sure to add python to PATH) and make sure it works
2. Set up git and github (https://docs.github.com/en/get-started/quickstart/set-up-git) for more details
3. In terminal at proper working directory type `git clone https://github.com/JiffyRob/Treds-Adventure-v2.git`.
4. Go into generated directory for the repo and type in `pip install -r requirements.txt` or `python -m pip -r install requirements.txt`.  This will add the python libraries that the game needs.
5. Also it is recommended but not required that you install these libraries for development:
   - black: `pip install black` or `python -m pip install black` (formats code)
   - isort: `pip install isort` or `python -m pip install isort` (formats imports)
6. It is also recommended that you install an IDE for coding in.  Some reccomended applications are:
   - Microsoft Visual Studio Code
   - Jetbrains Pycharm
7. run `python main.py` and see if it runs.  It might not because @JiffyRob has been reworking the physics

# Dependency List
For those of you who want to know what all these libraries do, here is a list:
 - pygame (https://pygame.org) video, audio, vector math, sprites, etc
 - shapely (https://shapely.readthedocs.io/en/stable/manual.html)
 - lupa (https://github.com/scoder/lupa) lua bindings for python (NPC scripting)
 - pytmx (https://pytmx.readthedocs.io/en/latest/) python map loading for .tmx maps

...which reminds me:
Maps are done with the Tiled Map Editor (https://www.mapeditor.org/).  You can open the project from the tiled directory in the repository.  It should have all the tilesets and object templtates you need to make maps.

# Job Listings
 - Engine Programming (currently @JiffyRob)
 - Physics (currently @JiffyRob)
 - GUI (currently @zclimb)
 - Data Generation (eg. weaponry stats) (currently @JiffyRob)
 - Design of Game Logic (currently @JiffyRob and @zclimb)
 - Implementation of Game Logic (currently @JiffyRob)
 - Higher Level Storyline Programming (currently @zclimb)
 - Resource Handling (currently @JiffyRob)
 - Playtesting (currently @zclimb)
 - Audio + Music integration (currently @JiffyRob)
 - Map Designer (currently @JiffyRob and @zclimb)
 - Map Maker (currently @JiffyRob)
 - Pixel Artists (currently none of them are on github)
 - Debugging (currently @JiffyRob + @zclimb)
 - Soundtrack Composition and Arrangement (now and forever @JiffyRob)
