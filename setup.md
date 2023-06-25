# Setup for coding
Welcome to the development team!  Here is how to set things up to get coding.  The code is done in python3.10+ and pygame-ce 2.  Code goals are simplicity, scalability, readability, and performance.
## Downloading and installing code and packages and such
1. Install Python and verify it works.  (https://python.org/download for windows/mac users.  Linux users can get it from their package managers if it isn't there already)
2. Set up git and github (https://docs.github.com/en/get-started/quickstart/set-up-git) for more details
3. In terminal at proper working directory type `git clone https://github.com/JiffyRob/Treds-Adventure-v2.git`.
4. Go into generated directory for the repo and type in `pip install -r requirements.txt` or `python -m pip -r install requirements.txt`.  This will add the python libraries that the game needs.  As of time of writing the game requires nothing but pygame-ce.  pytmx is also a requirement, but was added manually (`pytmx` folder in `src`) because pygbag doesn't support it yet.
6. Also run `pip install requirements-dev.txt` or `python -m pip install requirements-dev.txt` to install the development dependencies.  These include black and isort, as well as pre-commit.  Black and isort help pretty up the code, and pre-commit sets things up so that they are run before commmits.  Additionally, this will add pygbag, the library used to build the game for the web.
7. It is also recommended that you install an IDE for coding in.  Some reccomended applications are:
   - Microsoft Visual Studio Code
   - Jetbrains Pycharm
8. Run `pre-commit install` to setup pre-commit hooks.  Git commits will now fail if not properly formatted.
9. `cd src` to go to the code directory and `python main.py` to run the game
10. (Optional) Run `pygbag src` and then go to the url `localhost:8000`.  This should show the game on browser.  Note that it has been tested in chroe, brave, and firefox.  It doesn't work in teh debian stable version of firefox.

## Virtual Environments
You may want to create a virtual environment in order to isolate your packages.  If so, make sure to not create it in the `src` folder or any of its subdirectories.  If you do then pygbag will try to package the entire shebang when testing the web build and error out on pygame's example directories.

## Dependency List
For those of you who want to know what all these libraries do, here is a list:
 - pygame-ce (https://pyga.me) video, audio, vector math, sprites, etc
 - pytmx (https://pytmx.readthedocs.io/en/latest/) python map loading for .tmx maps

...which reminds me:
Maps are done with the Tiled Map Editor (https://www.mapeditor.org/).  You can open the project from the `src/assets/tiled` directory in the repository.  It should have all the tilesets and object templates you need to make maps.

## Code commit policy
Because the web version of the game is based off the `main` branch, please do not push any experimental, partially complete, or broken features to it.  Instead make changes to a local branch (or a remote one, but please clean up after yourself) and merge in once you're done.  Try not to push to `main` every five minutes because every time you do that github will remake the web build.  Because the code is public the process is free but we don't want to abuse thins *too* much :)

All code must be `black`ed and `isort --profile black`ed before commiting to `main`.  The `pre-commit` library will yell at you if you don't.

## Some conventions and best practices
### imports
You always import by module.  One line per package, or per module without package.  eg:
 - `import random` V - `random` is a module
 - `import pygame, random` X - should be in two lines
 - `import pygame as pg` X - no aliases please
 - `from random import randint` X - import modules, not functions
 - `from bush import entity` V - entity is a module in `bush`
 - `import bush` X - `bush` is a package.  Import modules from it.
 - `import pygame` V - `pygame` is special.  Import it even though it is a package.
 - `from pygame.locals import *` X - You may have seen this elsewhere but it is a no no for this repo.
 - `from bush import entity, timer` V - don't split into two lines because it is all from one module

**Why would we do this?**  Because this is what I (JiffyRob) did by default when the codebase is started, and we have hit 5000 lines of code roughly.  With a codebase that large, you have to be consistent.  This helps keep the code looking the same across all of the different modules and packages.

### Game objects
#### Arguments
*game entities* are anything on the map that gets updated in game.  A grass tile is not a game entity.  A tree, if animated, is.  All game entities (aside from `entity.Entity` , which the map loader sometimes uses directly) are either *base classes* which give additional functionality to a specific type of entity, like an enemy or a throwable, or *entity classes* which can derive from these classes and are created by the map.  All entity classes must take a first positional argument of `data`, which corresponds to a `game_objects.arg.GameObjectArgs` object.  Other than that base classes and **base classes ONLY** can take additional arguments which change based on subclass.  For example, the `Enemy` base class can take a `speed` parameter along with `data` so that a slime will pass a different value and therefore move at a different speed than a sewer rat.  Any tiled properties not directly assigned to a property of the `data` parameter will go in the `data.misc` dictionary.  Try not to use this if possible, but it is there.  The teleport uses it to get the width and height of the object.

#### When to make a package
You probably noticed that the enemies get their own package, and the plants don't.  That is because I forsee many many types of enemies in the game and spreading them out into a package makes things easier to find.  There will not be many plant classes, only at most 3, so those can go in a module.  Additionally, there is no common `plant` base class.  This last point is the largest.  If whatever you are making does not have enough variation and repition to warrant an extra base class then just make it a module.  This is a pattern that you will see all over.  I should probably rename all the `base` modules at some point.

#### When to put things in `bush` and when not to
Let's make the abstraction clear.  `bush` is a set of utilities that goes into other games as well.  Things like map loading or physics that many games do should go in here.  Anything specific to this project goes outside the directory.

# What now?
Congrats!  You now should be able to add code in and commit it.  Right now we use the honor system, (if you have write privs) so make sure to test things before pushing to main.  As to what you can code in to contribute, look around in issues or the roadmap at the bottom of the readme.
