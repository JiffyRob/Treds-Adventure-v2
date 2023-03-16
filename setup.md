# Intro
Welcome to the development team!  Here is how to set things up to get coding.  The code is done in python3.10+ and pygame-ce 2.  Code goals are simplicity, scalability, readability, and performance.
# Setup
1. Install Python https://python.org/download (make sure to add python to PATH) and make sure it works
2. Set up git and github (https://docs.github.com/en/get-started/quickstart/set-up-git) for more details
3. In terminal at proper working directory type `git clone https://github.com/JiffyRob/Treds-Adventure-v2.git`.
4. Go into generated directory for the repo and type in `pip install -r requirements.txt` or `python -m pip -r install requirements.txt`.  This will add the python libraries that the game needs.
5. Also run `pip install requirements-dev.txt` or `python -m pip install requirements.txt` to install the development dependencies.  These include black and isort, as well as pre-commit.  Black and isort help pretty up the code, and pre-commit sets things up so that they are run before commmits.
6. It is also recommended that you install an IDE for coding in.  Some reccomended applications are:
   - Microsoft Visual Studio Code
   - Jetbrains Pycharm
7. Run `pre-commit install` to setup pre-commit hooks.  Git commits will now fail if not properly formatted.
8. Run `python main.py` and see if it runs.  If it does not contact me (@JiffyRob)

# Dependency List
For those of you who want to know what all these libraries do, here is a list:
 - pygame-ce (https://pyga.me) video, audio, vector math, sprites, etc
 - pytmx (https://pytmx.readthedocs.io/en/latest/) python map loading for .tmx maps
 - pygame-gui widgets for the ui and HUD

...which reminds me:
Maps are done with the Tiled Map Editor (https://www.mapeditor.org/).  You can open the project from the tiled directory in the repository.  It should have all the tilesets and object templtates you need to make maps.

# What now?
Congrats!  You now should be able to add code in and commit it.  Right now we use the honor system, so make sure to test things before pushing to main.  As to what you can code in to contribute, we can figure that out later.
