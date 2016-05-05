# IMPORTS
from io import StringIO
import json

# GAMESENSE MODULE
import pygamesense as PyGameSense

GAME = "PYGS"
COREPROPS_PATH = "C:/ProgramData/SteelSeries/SteelSeries Engine 3/coreProps.json"

# EXAMPLE CODE
gs = PyGameSense.GameSenseBridge(COREPROPS_PATH) # ("127.0.0.1", 49157)

if(gs.is_connected):
    gs.unregister_game(GAME) # DONE TO CLEAN UP THE DATABASE
    gs.register_game(GAME , "PythonBridge", 5)

    gs.getEffects().show_rgb_rainbow(GAME, PyGameSense.MouseRival.DEVICE_TYPE, PyGameSense.MouseRival.ZONES)

    # gs.enter_heartbeat_loop(GAME)

    # gs.unregister_game(GAME) # DONE TO CLEAN UP THE DATABASE
