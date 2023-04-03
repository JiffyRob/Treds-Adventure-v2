# What do all of the modules do?
A brief summary of every python module currently in the repo, located in the `src` folder (last updated 4/2/2023)
 - `bush` is a custom game engine written specifically for this game.  It will likely be used elsewhere later as well once it is in a more stable condition.  It has quite a few submodules:
   - `ai` is a subpackage for sprite behaviour:
     - `steering_behaviours.py` has a series of behaviours that can be called on sprites to make them perform the given action.
     - `scripting.py` holds a class for executing JSON data based on a custom API, as well as a decorator for functions to make them usable in this context.  We use a seperate method of scripting, so you can ignore that too.
     - `state.py` holds some useful classes for state stacks.  Other sorts of state machines will be added later. maybe.
   - `mapping` is a subpackage with stuff for level loading in it:
     - `group.py` has some specialized sprite groups for cameras, top down rendering, and sprite identification.
     - `mapping.py` holds a map loader that takes pygame tmx maps and loads them into sprites.  Meant to be extended.
   - `color.py` has some color constants.  This will probably be phased out as well.
   - `collision.py` contains collision functions for rects and masks.
   - `animation.py` contains classes for sprite animation.
   - `timer.py` contains a class for creating timers.  These can be updated to call their own functions or checked for completion.
   - `util.py` has a couple of neat utility functions.
   - `sound_manager.py` has a class for managing sound objects and playing them
   - `autotile.py` has a *very* primitive autotiler in it.
   - `joy_cursor.py` has a cursor class that takes an arbitrary image and uses it for the system cursor.  Meant to take input from a joystick.
   - `entity.py` contains basic sprite classes for use in the game.  Everything else is made to work with these.
   - `physics.py` has some very basic top down physics.
   - `asset_hander.py` holds a class for handling and caching assets of many different file types.  Use this if possible to prevent loading of files multiple times.
   - `util_load.py` has a bunch of functions to load files.  Usually used in the asset_handler, or for files that you know will only be loaded once.
   - `save_state.py` holds a couple of classes for global game state, things that would be saved in a save file
   - `event_binding.py` contains a class and some helper functions for complex input handling.  Use this if you want to use joystick input or rebind your keys
   - `__init__.py` imports the modules in the engine and makes them available to the outside.
 - `scripts` has python scripts for entities in it.  They are executed by certain GameObjects.  
   - `__init__.py` import all scripts and makes them available via import or through string id.
   - `base.py` contains a base class that all scripts derive from
   - `random_walk.py` is a script for an entity to walk around aimlessly, and sometimes stop.
   - `test.py` is a script for interaction.  It simply pulls up a little dialog and leaves it at that.
 - `game_objects` is a package containing all sprite classes in the game.  It's modules include:
   - `base.py` has a base class for game objects that do more than sit still and get bumped into.  It has two flavors: those which move are can be influenced by terrain, and those which don't move.  These are what execute scripts.
   - `npc.py` has two classes for NPCs.  One stays put and the other does not.  The only functionality that these classes have over the base GameObject classes in `base.py` is finding their images in `resources/sprites/npcs` .
   - `plant.py` has some plant classes in it.  Things like wheat plants and if we ever want to do anything with trees.  This will probably be phased out as the current farmplant classes' autotiling is a little cringy.
   - `player.py` houses the all-important player class.
   - `teleport.py` houses the class for the teleport, a handy little class that can be of arbitrary size and will move the play to a destination if he touches it (even if it's on another map)
 - `sky.py` has a class that handles the day/night cycle, and likely more advanced weather/time later
 - `environment.py` has a class that loads the environments of tiled maps and makes them visible to game objects.  Maybe move this into the `game_objects` package...?
 - `custom_mapper.py` has an extension of the original map loader from the bush module.
 - `game_state.py` holds all of the states of the game, like maps and menus.  This is what does the rendering and updating of everything on the map.
 - `menu.py` contains a helper function for creating menus and a couple of custom GUI elements.
 - `main.py` holds the class for the main game.  Running this runs the game (run from project root directory, NOT src)

Additionally, there is a seperate `run_game.py` module in the root directory of the repository.  As you probably figured out, it runs the game.  use this over `src/main.py` in order to avoid `sys.path` issues.  The other way to run the game is to run `python src/main.py` in terminal from the repository's root directory.  This is basically what `run_game.py` does.

 # Also in the data directories...
  - `resources` contains visual and audio assets:
    - `tiled` contains all maps and tileset files used in the game, as well as templates, world files, etc.  - `tiled` contains all maps and tileset files used in the game, as well as templates, world files, etc.
    - `hud` has GUI stuff
    - `masks` has collision shapes for some static sprites
    - `particlefx` has particle effects
    - `sounds` has sounds
    - `sprites` has sprites
    - `tiles` has tilesets
    - `data` contains save files and input bindings, as well as item and weapon definitions, etc.
    - `music` contains the game's music.  It is currently a bit empty as I figure out instruments, but has the alpha theme song in it for testing of soundtracks.
    
# Additionally, in root directory of the repository
  - `credits.txt` is the credits of the game.  When end of game credits are implemented, it will just scroll through this file.
  - `main.spec` is specifications for distributing binaries.  Do not touch.
  - `LICENSE` is the code's license.  Currently MIT, but may be switched later.
  - `screenshot.png` - if you hit the 's' key while the game is running, it takes a screenshot and puts it here.  I might add this file to `.gitignore` in the future, I might not.