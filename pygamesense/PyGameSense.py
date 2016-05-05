# -------------------------------------------------------------------------------
# Name:        PYTHON_GAMESENSE
#
# Author:      Julius
#
# Created:     25/11/2015
# Copyright:   (c) Julius 2015
#
# GradientHandler      handler = self.build_handler("rgb-2-zone", "two", "color", {"gradient": {"zero": {"red": 0, "green": 0, "blue": 0}, "hundred": {"red": r, "green": g, "blue":b}}})
# StaticColorHandler   handler = self.build_handler("rgb-2-zone", "two", "color", {"red": r, "green": g, "blue":b})
# -------------------------------------------------------------------------------

import requests
import time

COREPROPS = "C:/ProgramData/SteelSeries/SteelSeries Engine 3/coreProps.json"

# HELPER FUNCTIONS
def parse_core_props(path=COREPROPS):
    """Returns IP, then port."""
    f = open(path, 'r')
    io = StringIO(unicode(f.read()))
    addr = json.load(io)["address"].split(":")
    return (addr[0], addr[1])

# STATIC COLORS
class Colors:
    WHITE  = (255, 255, 255)
    BLACK  = (0, 0, 0)
    RED    = (255, 0, 0)
    GREEN  = (0, 255, 0)
    BLUE   = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PINK   = (255, 0, 255)
    CYAN   = (0, 255, 255)


# GAMESENSEBRIDGE MAIN CLASS
class GameSenseBridge:
    """Can be initialized with (core_props_path) or (gs_ip, gs_port)

    Example usage:

    from pygamesense import *

    gs = GameSenseBridge(gs_ip, gs_port)
    gs = GameSenseBridge(core_props_path)
    gs = GameSenseBridge()

    Calling this method with no arguments will default to:
    gs = GameSenseBridge(COREPROPS)

    If core_props_path is invalid, IOError will be raised.
    """

    # -----INIT-----
    def __init__(self,  *args, **kwargs):
        if len(args) == 2:
            self.gs_ip, self.gs_port = args
        elif len(args) > 2:
            raise ValueError("0-2 arguments expected. Got: " + str(len(args)))
        else:
            self.gs_ip, self.gs_port = parse_core_props(*args)

        # ESTABLISH OUR CONNECTION TO STEELSERIES SERVER
        self.gsurl = "http://%s:%s/" % (gs_ip, gs_port)
        # OUR REQUEST SESSION
        self.session = requests.session()
        # MISC
        self.is_connected = self.reachable_host(self.gsurl)
        self.effects = None

    # -----HELPER FUNCTIONS-----
    # GET THE EFFECTS CLASS
    def getEffects(self):
        if self.effects is None:
            self.effects = GameSenseEffects(self)
        return self.effects

    # BUILD A NEW UNIVERSIAL HANDLER
    def build_handler(self, device_type, zone, mode, color):
        handler = {"device-type": device_type, "zone": zone, "mode": mode}
        handler["color"] = color
        return [handler]

    # CHECK IF AN GAMESENSE SERVER IS REACHABLE
    def reachable_host(self, url):
        try:
            self.session.get(url)
            return True
        except:
            return False

    # -----API FUNCTIONS-----
    # SEND REQUEST TO RESTFULL API
    def _post(self, endpoint, payload):
        try:
            self.session.post(self.gsurl + endpoint, json=(payload))
            return True
        except:
            return False

    # REGISTER A NEW GAME
    def register_game(self, game_name, game_display_name, icon_color_id):
        payload = {"game": game_name, "game_display_name": game_display_name,
            "icon_color_id": icon_color_id}

        return self._post("game_metadata", payload)

    # REMOVES THE GAME WITH NAME
    def unregister_game(self, game_name):
        payload = {"game": game_name}
        return self._post("remove_game", payload)

    # REGISTER A NEW EVENT
    def register_event(self, game_name, event, min_value, max_value, icon_id):
        payload = {"game": game_name, "event": event, "min_value": min_value,
            "max_value": max_value, "icon_id": icon_id}

        return self._post("register_game_event", payload)

    # REMOVES AN EVENT
    def unregister_event(self, game_name, event):
        payload = {"game": game_name, "event": event}
        return self._post("remove_game_event", payload)

    # BINDS AN EVENT TO A HANDLER
    def bind_event(self, game_name, event, min_value, max_value, icon_id, handler):
        payload = {"game": game_name, "event": event, "min_value": min_value,
            "max_value": max_value, "icon_id": icon_id}

        payload["handlers"] = handler
        return self._post("bind_game_event", payload)

    # TRIGGERS A GAMEEVENT FOR THE GIVEN GAME NAME
    def send_gameevent(self, game_name, event, value):
        payload = {"game": game_name, "event": event}
        payload["data"] = {"value": value}
        return self._post("game_event", payload)

    # SENDING KEEP ALIVE PACKAGES
    def send_hartbeat(self, game_name):
        payload = {"game": game_name}
        return self._post("game_heartbeat", payload)

    def enter_heartbeat_loop(self, game_name):
        try:
            while True:
                self.send_hartbeat(game_name)
                time.sleep(10)
        except KeyboardInterrupt:
            return None


# GAMESENSEBRIDGE
class GameSenseEffects:
    def __init__(self, gs):
        self.gs = gs

    # SHOW A STATIC COLOR
    def show_static_color(self, game_name, device_type, zones, color):
        (r, g, b) = color
        for zone in zones:
            handler = self.gs.build_handler(
                device_type, zone,
                "color", {"red": r, "green": g, "blue": b})

            self.gs.bind_event(game_name, "COLOR", 0, 100, 16, handler)
            self.gs.send_gameevent(game_name, "COLOR", 100)

    # SINGLE COLOR RAINBOW
    def show_rgb_rainbow(self, game_name, device_type, zones):
        # Editor's note: Why is there no time.sleep here? Won't this be a huge
        # CPU hog? It looks like it infinitely loops as fast as the processor
        # can handle it.
        while True:
            for i in range(0, 250, 5):
                self.show_static_color(
                    game_name, device_type, zones,
                    (255-i, i, 0))

            for i in range(0, 250, 5):
                self.show_static_color(
                    game_name, device_type, zones,
                    (0, 255-i, i)) # GREEN -> BLUE

            for i in range(0, 250, 5):
                self.show_static_color(
                    game_name, device_type, zones,
                    (i, 0, 255-i)) # BLUE -> RED


# ----DEVICE INFO----
class MouseRival:
    DEVICE_TYPE = "rgb-2-zone"
    ZONES = ["one", "two"]
