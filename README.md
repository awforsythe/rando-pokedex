# Rando Pokédex

This project is a web app, with a complementary Lua script, that displays information about a playthrough of Pokémon Black or White. Importantly, it does so in a way that supports randomizer runs. Since every randomized ROM is different &mdash; different move stats, different types, and even different sprite graphics &mdash; we can't just pull from established data sources to get information about Pokemon and their moves. Instead, we read directly from memory to get the information we need, supplemented with screenshots (triggered manually but captured and processed automatically) to get sprite images and fill in the gaps.

The webapp provides a few different views as an end result. There's a customized stream overlay suitable for use as a Browser Source in OBS:

![hud](doc/readme_01_hud.png)

And there's also a web frontend that displays all the information that's collected so far. This includes a roster page, listing the details for all the Pokémon that have been captured:

![roster](doc/readme_02_roster.png)

...a Pokédex page, which lists an overview of all Pokémon and their types:

![pokedex](doc/readme_03_pokedex.png)

...and finally, a Moves page, which shows the randomized stats and types for all moves that captured Pokémon have learned.

![moves](doc/readme_04_moves.png)

The webapp uses a database to store this information persistently. It runs a worker thread that watches for screenshots and memory dumps from the accompanying Lua script: when new data is received, it's decrypted, parsed, and processed, the results are fed into the webapp via an HTTP API, and the web pages update in real-time (via socket.io) to reflect the new information.

At time of writing, a working example can be seen here: https://rando-pokedex.herokuapp.com

## Caveats

Currently, the Lua script used to dump screenshots requires a custom build of DeSmuME that adds a Lua function for toggling display layers, so I wouldn't call this project ready for public consumption.

Building the frontend _(which is optional, since bundled Javascript is versioned in `static/dist`)_ requires NodeJS. Install NodeJS and npm, and then you should be able to run `npm run build` from the root directory.

Running the server requires Python 3.6.8 and Pipenv. Install Python, then run `pip install --user pipenv` to get Pipenv, and then you should be able to run `pipenv install` and `pipenv run pokeserver` from the root directory. `http://localhost:5000` should bring up the web frontend, and `http://localhost:5000/hud` will display an overlay suitable for use in OBS via a Browser Source.

The server can run locally (for lightning-fast updates to the OBS overlay) while also updating a remote copy hosted on the internet so that viewers can see stats in real-time. At the moment this is accomplished in a very hacky way: the local instance simply forwards all API update requests to a remote mirror, and simple validation is performed with a secret API key. This configuration probably deserves some rethinking. Also, the SocketIO setup that drives real-time updates of all the frontend pages is not particularly robust in real-world, open-internet conditions, so sometimes the remote mirror needs to be manually reloaded to refetch missing data.

The Lua script run by DeSmuME simply dumps memory and screenshots to disk. The accompanying Python code in `python/pokedata` implements all the decryption, parsing, and image processing required to suss out the data that's relevant to this application. The application itself is a Flask app that stores Pokemon and move information in a database, and that serves up a React-based frontend to display that data to users. Parsing of memory dumps and screenshots takes place in a worker greenthread, which communicates new data to the webapp via an HTTP API.

## DeSmuME modification

In the future I might be able to find a way to grab sprites and type data without extra Lua functionality, or I might submit the requisite Lua changes to the maintainers of DeSmuME. In the meantime, just for posterity, here's a rundown of what I did to add a custom Lua function to DeSmuME.

After cloning or downloading the DeSmuME source, edit `src/lua-engine.cpp`. Add `#include "display.h"` to the list of project includes, and in the `guilib` array, add `{"togglelayer", gui_togglelayer},` just above the line for `gui_gdscreenshot`. Then, above `DEFINE_LUA_FUNCTION(gui_gdscreenshot, "[whichScreen='both']")`, add this function definition:

    DEFINE_LUA_FUNCTION(gui_togglelayer, "screen,layer")
    {
        lua_Integer screen = luaL_checkint(L, 1);
        lua_Integer layer = luaL_checkint(L, 2);
        if (screen == 0)
        {
            switch (layer)
            {
                case 0: TwiddleLayer(IDM_MBG0, 0, 0); break;
                case 1: TwiddleLayer(IDM_MBG1, 0, 1); break;
                case 2: TwiddleLayer(IDM_MBG2, 0, 2); break;
                case 3: TwiddleLayer(IDM_MBG3, 0, 3); break;
                case 4: TwiddleLayer(IDM_MOBJ, 0, 4); break;
                default:
                    break;
            }
        }
        else if (screen == 1)
        {
            switch (layer)
            {
                case 0: TwiddleLayer(IDM_SBG0, 1, 0); break;
                case 1: TwiddleLayer(IDM_SBG1, 1, 1); break;
                case 2: TwiddleLayer(IDM_SBG2, 1, 2); break;
                case 3: TwiddleLayer(IDM_SBG3, 1, 3); break;
                case 4: TwiddleLayer(IDM_SOBJ, 1, 4); break;
                default:
                    break;
            }
        }
        return 0;
    }

Then build in Release configuration from `src/frontend/windows/DeSmuME.sln` (or the equivalent for your platform). The executable in `src/frontend/windows/__bins` is the one you should use to run `pokedump.lua`.
