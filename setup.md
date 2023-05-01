# Intro
Welcome to the development team!  Here is how to set things up to get coding.  The code is done in python3.10+ and pygame-ce 2.  Code goals are simplicity, scalability, readability, and performance.
# Setup
1. Install Python https://python.org/download (make sure to add python to PATH) and make sure it works
2. Set up git and github (https://docs.github.com/en/get-started/quickstart/set-up-git) for more details
3. In terminal at proper working directory type `git clone https://github.com/JiffyRob/Treds-Adventure-v2.git`.
4. Go into generated directory for the repo and type in `pip install -r requirements.txt` or `python -m pip -r install requirements.txt`.  This will add the python libraries that the game needs.  As of time of writing the game requires nothing but pygame-ce.  pytmx is also a requirement, but was added manually (`pytmx` folder in `src`) because pygbag doesn't support it yet.
6. Also run `pip install requirements-dev.txt` or `python -m pip install requirements-dev.txt` to install the development dependencies.  These include black and isort, as well as pre-commit.  Black and isort help pretty up the code, and pre-commit sets things up so that they are run before commmits.  Additionally, this will add pygbag, the library used to build the game for the web.
7. It is also recommended that you install an IDE for coding in.  Some reccomended applications are:
   - Microsoft Visual Studio Code
   - Jetbrains Pycharm
8. Run `pre-commit install` to setup pre-commit hooks.  Git commits will now fail if not properly formatted.
9. Run `python run_game.py` and see if it runs.  If it does not contact me (@JiffyRob)
10. (Optional) Run `pygbag src` and then go to the url `localhost:8000`.  This should show the game on browser.  Note that it has been tested in chroe, brave, and firefox.  It doesn't work in teh debian stable version of firefox.

# Virtual Environments
You may want to create a virtual environment in order to isolate your packages.  If so, make sure to not create it in the `src` folder or any of its subdirectories.  If you do then pygbag will try to package the entire shebang when testing the web build.

# Dependency List
For those of you who want to know what all these libraries do, here is a list:
 - pygame-ce (https://pyga.me) video, audio, vector math, sprites, etc
 - pytmx (https://pytmx.readthedocs.io/en/latest/) python map loading for .tmx maps

...which reminds me:
Maps are done with the Tiled Map Editor (https://www.mapeditor.org/).  You can open the project from the `src/assets/tiled` directory in the repository.  It should have all the tilesets and object templates you need to make maps.

# Code commit policy
Because the web version of the game is based off the `main` branch, please do not push any experimental, partially complete, or broken features to it.  Instead make changes to a local branch and merge in once you're done.  After a major change is made (or a minor one, if you want), you can update the web build by going to to the `actions` tab in the repository and running the `pygbag_build` action.  I'm pretty sure the action to deploy the new build runs automatically.

All code must be `black`ed and `isort`ed before commiting to `main`.  The `pre-commit` library should take care of this for you.

# What now?
Congrats!  You now should be able to add code in and commit it.  Right now we use the honor system, (if you have write privs) so make sure to test things before pushing to main.  As to what you can code in to contribute, look around in issues or the roadmap at the bottom of the readme.
