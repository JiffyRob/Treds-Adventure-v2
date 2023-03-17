# What do all of the modules do?
A brief summary of every python module currently in the repo (last updated 3/16/2023)
 - `bush` is a custom game engine written specifically for this game.  It will likely be used elsewhere later as well once it is in a more stable condition.  It has quite a few submodules:
   - `ai` is a subpackage for sprite behaviour:
     - `command.py` has a class that abstracts arbitrary function calls.  Ignore it - it will probably be removed pretty soon.
     - `steering_behaviours.py` has a series of behaviours that can be called on sprites to make them perform the given action.
     - `scripting.py` holds a class for executing JSON data based on a custom API, as well as a decorator for functions to make them usable in this context
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
   - `entity_component.py` has some components for entities in it.  Currently only deals with health, but more will be added as needed.
   - `entity.py` contains basic sprite classes for use in the game.  Everything else is made to work with these.
   - `physics.py` has some very basic top down physics.
   - `asset_hander.py` holds a class for handling and caching assets of many different file types.  Use this if possible to prevent loading of files multiple times.
   - `util_load.py` has a bunch of functions to load files.  Usually used in the asset_handler, or for files that you know will only be loaded once.
   - `save_state.py` holds a couple of classes for global game state, things that would be saved in a save file
   - `event_binding.py` contains a class and some helper functions for complex input handling.  Use this if you want to use joystick input or rebind your keys
   - `__init__.py` imports the modules in the engine and makes them available to the outside.
 - `motion_objects.py` will hold classes for game objects later.
 - `sky.py` has a class that handles the day/night cycle
 - `environment.py` has a class that loads the environments of tiled maps and a superclass for sprites that get affected by it
 - `game_objects.py` has a series of static objects in it (like trees)
 - `event_objects.py` has game objects that mess around with game state or help progress the story.
 - `custom_mapper.py` has an extension of the original map loader from the bush module.
 - `game_state.py` holds all of the states of the game, like maps and menus.
 - `player.py` holds the class for the player.  This will get pretty complicated as time goes on, which is why it gets its own module.
 - `menu.py` contains a helper function for creating menus and a couple of custom GUI elements.
 - `Main.py` holds the class for the main game.  Running this runs the game (run from project root directory, NOT src)
 
 ## Notes:
 - modules `bush.physics` and `bush.ai.command` are scheduled to be phased out of the codebase.
 - modules `game_objects`, `motion_objects` and `event_objects` are likely to be renamed and/or rearranged in the near future.  The current sprite divisions are not intuitive enough.
 # Also in the data directories...
  - `tiled` contains all maps and tileset files used in the game, as well as templates, world files, etc.
  - `resources` contains visual and audio assets:
    - `hud` has GUI stuff
    - `masks` has collision shapes for some static sprites
    - `particlefx` has particle effects
    - `sounds` has sounds
    - `sprites` has sprites
    - `tiles` has tilesets
  - `scripts` contains JSON scripts for NPC scripting.  This is also scheduled to be phased out in favor of straight python scripting.
  - `data` contains save files and input bindings, as well as item and weapon definitions, etc.
  - `credits.txt` is the credits of the game.  When end of game credits are implemented, it will just scroll through this file.
  - `main.spec` is specifications for distributing binaries.  Do not touch.
  
## Notes:
 - all of these are scheduled to be put in a single `resources` folder, with the current `resources` possibly getting renamed to `assets`.
 - eventually there will also be a `music` folder with original compositions by myself.