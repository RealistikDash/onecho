# onecho
# The single-file, dependency-less osu! server implementation.
# Made by:
# - RealistikDash
# - Lenfouriee
from __future__ import annotations

import asyncio
import random
import string
import struct
import traceback
import urllib.request
import urllib.parse
import json
import os
import time
import sys
import socket

from collections.abc import MutableMapping
from collections.abc import Mapping
from collections import OrderedDict

from typing import Any
from typing import Union
from typing import Callable
from typing import Awaitable
from typing import NamedTuple
from typing import get_type_hints

from enum import Enum
from enum import IntEnum
from enum import IntFlag
from dataclasses import dataclass
from dataclasses import field

# Global Constants START


DEBUG = "debug" in sys.argv
STATUS_CODE = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "(Unused)",  # ehhh
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",  # soon?
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}

# fmt: off
COUNTRY_CODES = {
    "oc": 1,   "eu": 2,   "ad": 3,   "ae": 4,   "af": 5,   "ag": 6,   "ai": 7,   "al": 8,
    "am": 9,   "an": 10,  "ao": 11,  "aq": 12,  "ar": 13,  "as": 14,  "at": 15,  "au": 16,
    "aw": 17,  "az": 18,  "ba": 19,  "bb": 20,  "bd": 21,  "be": 22,  "bf": 23,  "bg": 24,
    "bh": 25,  "bi": 26,  "bj": 27,  "bm": 28,  "bn": 29,  "bo": 30,  "br": 31,  "bs": 32,
    "bt": 33,  "bv": 34,  "bw": 35,  "by": 36,  "bz": 37,  "ca": 38,  "cc": 39,  "cd": 40,
    "cf": 41,  "cg": 42,  "ch": 43,  "ci": 44,  "ck": 45,  "cl": 46,  "cm": 47,  "cn": 48,
    "co": 49,  "cr": 50,  "cu": 51,  "cv": 52,  "cx": 53,  "cy": 54,  "cz": 55,  "de": 56,
    "dj": 57,  "dk": 58,  "dm": 59,  "do": 60,  "dz": 61,  "ec": 62,  "ee": 63,  "eg": 64,
    "eh": 65,  "er": 66,  "es": 67,  "et": 68,  "fi": 69,  "fj": 70,  "fk": 71,  "fm": 72,
    "fo": 73,  "fr": 74,  "fx": 75,  "ga": 76,  "gb": 77,  "gd": 78,  "ge": 79,  "gf": 80,
    "gh": 81,  "gi": 82,  "gl": 83,  "gm": 84,  "gn": 85,  "gp": 86,  "gq": 87,  "gr": 88,
    "gs": 89,  "gt": 90,  "gu": 91,  "gw": 92,  "gy": 93,  "hk": 94,  "hm": 95,  "hn": 96,
    "hr": 97,  "ht": 98,  "hu": 99,  "id": 100, "ie": 101, "il": 102, "in": 103, "io": 104,
    "iq": 105, "ir": 106, "is": 107, "it": 108, "jm": 109, "jo": 110, "jp": 111, "ke": 112,
    "kg": 113, "kh": 114, "ki": 115, "km": 116, "kn": 117, "kp": 118, "kr": 119, "kw": 120,
    "ky": 121, "kz": 122, "la": 123, "lb": 124, "lc": 125, "li": 126, "lk": 127, "lr": 128,
    "ls": 129, "lt": 130, "lu": 131, "lv": 132, "ly": 133, "ma": 134, "mc": 135, "md": 136,
    "mg": 137, "mh": 138, "mk": 139, "ml": 140, "mm": 141, "mn": 142, "mo": 143, "mp": 144,
    "mq": 145, "mr": 146, "ms": 147, "mt": 148, "mu": 149, "mv": 150, "mw": 151, "mx": 152,
    "my": 153, "mz": 154, "na": 155, "nc": 156, "ne": 157, "nf": 158, "ng": 159, "ni": 160,
    "nl": 161, "no": 162, "np": 163, "nr": 164, "nu": 165, "nz": 166, "om": 167, "pa": 168,
    "pe": 169, "pf": 170, "pg": 171, "ph": 172, "pk": 173, "pl": 174, "pm": 175, "pn": 176,
    "pr": 177, "ps": 178, "pt": 179, "pw": 180, "py": 181, "qa": 182, "re": 183, "ro": 184,
    "ru": 185, "rw": 186, "sa": 187, "sb": 188, "sc": 189, "sd": 190, "se": 191, "sg": 192,
    "sh": 193, "si": 194, "sj": 195, "sk": 196, "sl": 197, "sm": 198, "sn": 199, "so": 200,
    "sr": 201, "st": 202, "sv": 203, "sy": 204, "sz": 205, "tc": 206, "td": 207, "tf": 208,
    "tg": 209, "th": 210, "tj": 211, "tk": 212, "tm": 213, "tn": 214, "to": 215, "tl": 216,
    "tr": 217, "tt": 218, "tv": 219, "tw": 220, "tz": 221, "ua": 222, "ug": 223, "um": 224,
    "us": 225, "uy": 226, "uz": 227, "va": 228, "vc": 229, "ve": 230, "vg": 231, "vi": 232,
    "vn": 233, "vu": 234, "wf": 235, "ws": 236, "ye": 237, "yt": 238, "rs": 239, "za": 240,
    "zm": 241, "me": 242, "zw": 243, "xx": 244, "a2": 245, "o1": 246, "ax": 247, "gg": 248,
    "im": 249, "je": 250, "bl": 251, "mf": 252,
}
# fmt: on

HEADER_LEN = 7


class BanchoAction(IntEnum):
    IDLE = 0
    AFK = 1
    PLAYING = 2
    EDITING = 3
    MODDING = 4
    MULTIPLAYER = 5
    WATCHING = 6
    UNKNOWN = 7
    TESTING = 8
    SUBMITTING = 9
    PAUSED = 10
    LOBBY = 11
    MULTIPLAYING = 12
    OSU_DIRECT = 13


class OsuMode(IntEnum):
    OSU = 0
    TAIKO = 1
    CTB = 2
    MANIA = 3


class OsuMods(IntFlag):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30

    SPEED_MODS = DOUBLETIME | NIGHTCORE | HALFTIME
    GAME_CHANGING = RELAX | AUTOPILOT


class BanchoPrivileges(IntFlag):
    PLAYER = 1 << 0
    MODERATOR = 1 << 1
    SUPPORTER = 1 << 2
    OWNER = 1 << 3
    DEVELOPER = 1 << 4
    TOURNAMENT = 1 << 5


class BanchoPacketID(IntEnum):
    OSU_CHANGE_ACTION = 0
    OSU_SEND_PUBLIC_MESSAGE = 1
    OSU_LOGOUT = 2
    OSU_REQUEST_STATUS_UPDATE = 3
    OSU_HEARTBEAT = 4
    SRV_LOGIN_REPLY = 5
    SRV_SEND_MESSAGE = 7
    SRV_HEARTBEAT = 8
    SRV_USER_STATS = 11
    SRV_USER_LOGOUT = 12
    SRV_SPECTATOR_JOINED = 13
    SRV_SPECTATOR_LEFT = 14
    SRV_SPECTATE_FRAMES = 15
    OSU_START_SPECTATING = 16
    OSU_STOP_SPECTATING = 17
    OSU_SPECTATE_FRAMES = 18
    SRV_VERSION_UPDATE = 19
    OSU_ERROR_REPORT = 20
    OSU_CANT_SPECTATE = 21
    SRV_SPECTATOR_CANT_SPECTATE = 22
    SRV_GET_ATTENTION = 23
    SRV_NOTIFICATION = 24
    OSU_SEND_PRIVATE_MESSAGE = 25
    SRV_UPDATE_MATCH = 26
    SRV_NEW_MATCH = 27
    SRV_DISPOSE_MATCH = 28
    OSU_PART_LOBBY = 29
    OSU_JOIN_LOBBY = 30
    OSU_CREATE_MATCH = 31
    OSU_JOIN_MATCH = 32
    OSU_PART_MATCH = 33
    SRV_TOGGLE_BLOCK_NON_FRIEND_DMS = 34
    SRV_MATCH_JOIN_SUCCESS = 36
    SRV_MATCH_JOIN_FAIL = 37
    OSU_MATCH_CHANGE_SLOT = 38
    OSU_MATCH_READY = 39
    OSU_MATCH_LOCK = 40
    OSU_MATCH_CHANGE_SETTINGS = 41
    SRV_FELLOW_SPECTATOR_JOINED = 42
    SRV_FELLOW_SPECTATOR_LEFT = 43
    OSU_MATCH_START = 44
    SRV_ALL_PLAYERS_LOADED = 45
    SRV_MATCH_START = 46
    OSU_MATCH_SCORE_UPDATE = 47
    SRV_MATCH_SCORE_UPDATE = 48
    OSU_MATCH_COMPLETE = 49
    SRV_MATCH_TRANSFER_HOST = 50
    OSU_MATCH_CHANGE_MODS = 51
    OSU_MATCH_LOAD_COMPLETE = 52
    SRV_MATCH_ALL_PLAYERS_LOADED = 53
    OSU_MATCH_NO_BEATMAP = 54
    OSU_MATCH_UNREADY = 55
    OSU_MATCH_FAILED = 56
    SRV_MATCH_PLAYER_FAILED = 57
    SRV_MATCH_COMPLETE = 58
    OSU_MATCH_HAS_BEATMAP = 59
    OSU_MATCH_SKIP_REQUEST = 60
    SRV_MATCH_SKIP = 61
    OSU_CHANNEL_JOIN = 63
    SRV_CHANNEL_JOIN_SUCCESS = 64
    SRV_CHANNEL_INFO = 65
    SRV_CHANNEL_KICK = 66
    SRV_CHANNEL_AUTO_JOIN = 67
    OSU_BEATMAP_INFO_REQUEST = 68
    SRV_BEATMAP_INFO_REPLY = 69
    OSU_MATCH_TRANSFER_HOST = 70
    SRV_PRIVILEGES = 71
    SRV_FRIENDS_LIST = 72
    OSU_FRIEND_ADD = 73
    OSU_FRIEND_REMOVE = 74
    SRV_PROTOCOL_VERSION = 75
    SRV_MAIN_MENU_ICON = 76
    OSU_MATCH_CHANGE_TEAM = 77
    OSU_CHANNEL_PART = 78
    OSU_RECEIVE_UPDATES = 79
    SRV_MATCH_PLAYER_SKIPPED = 81
    OSU_SET_AWAY_MESSAGE = 82
    SRV_USER_PRESENCE = 83
    OSU_USER_STATS_REQUEST = 85
    SRV_RESTART = 86
    OSU_MATCH_INVITE = 87
    SRV_MATCH_INVITE = 88
    SRV_CHANNEL_INFO_END = 89
    OSU_MATCH_CHANGE_PASSWORD = 90
    SRV_MATCH_CHANGE_PASSWORD = 91
    SRV_SILENCE_END = 92
    OSU_TOURNAMENT_MATCH_INFO_REQUEST = 93
    SRV_USER_SILENCED = 94
    SRV_USER_PRESENCE_SINGLE = 95
    SRV_USER_PRESENCE_BUNDLE = 96
    OSU_USER_PRESENCE_REQUEST = 97
    OSU_USER_PRESENCE_REQUEST_ALL = 98
    OSU_TOGGLE_BLOCK_NON_FRIEND_DMS = 99
    SRV_USER_DM_BLOCKED = 100
    SRV_TARGET_IS_SILENCED = 101
    SRV_VERSION_UPDATE_FORCED = 102
    SRV_SWITCH_SERVER = 103
    SRV_ACCOUNT_RESTRICTED = 104
    SRV_RTX = 105
    SRV_MATCH_ABORT = 106
    SRV_SWITCH_TOURNAMENT_SERVER = 107
    OSU_TOURNAMENT_JOIN_MATCH_CHANNEL = 108
    OSU_TOURNAMENT_LEAVE_MATCH_CHANNEL = 109


# Global Constants END


# Logger START


class Ansi(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    GRAY = 90
    LRED = 91
    LGREEN = 92
    LYELLOW = 93
    LBLUE = 94
    LMAGENTA = 95
    LCYAN = 96
    LWHITE = 97

    RESET = 0

    def __str__(self) -> str:
        return f"\x1b[{self.value}m"


def _log(content: str, action: str, colour: Ansi = Ansi.WHITE):
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    sys.stdout.write(  # This is mess but it forms in really cool log.
        f"\x1b[90m[{timestamp} - {colour}\033[1"
        f"m{action}\033[0m\x1b[90m]: \x1b[94m{content}\x1b[0m\n"
    )


def info(text: str):
    _log(text, "INFO", Ansi.GREEN)


def error(text: str):
    _log(text, "ERROR", Ansi.RED)


def warning(text: str):
    _log(text, "WARNING", Ansi.BLUE)


def debug(text: str):
    if DEBUG:
        _log(text, "DEBUG", Ansi.WHITE)


# Logger END


# Database START
def _parse_to_type[T](value: str, value_type: type[T]) -> T:
    if value_type is str:
        return value

    if issubclass(value_type, (int, str, float, Enum)):
        return value_type(value)

    if value_type is bool:
        return value.lower() == "true"

    raise ValueError("Skill issue type??")


def _parse_from_type[T](value: T) -> str:
    if isinstance(value, Enum):
        return value.value

    return str(value)


class CSVResult[T](NamedTuple):
    id: int
    result: T


class CSVModel:
    def __init__(self, *args, **kwargs) -> None:
        for (value, type), arg in zip(get_type_hints(self).items(), args):
            setattr(self, value, _parse_to_type(arg, type))

        for value, type in get_type_hints(self).items():
            if value not in kwargs:
                continue

            setattr(self, value, _parse_to_type(kwargs[value], type))

    def into_str_list(self) -> list[str]:
        return [
            _parse_from_type(getattr(self, value)) for value in get_type_hints(self)
        ]


class CSVBasedDatabase[T: CSVModel]:  # Based af.
    def __init__(
        self,
        *,
        file_name: str,
        model: T,
        cache_table: bool = False,
    ) -> None:
        self._parsing_model = model
        self._file_name = file_name
        self._table_cache: list[str] = []
        self.__innit__()

        if cache_table:
            with open(self._file_name, "r") as f:
                self._table_cache = f.readlines()

    def __innit__(self) -> None:
        if not os.path.exists(self._file_name):
            with open(self._file_name, "w") as f:
                f.write("")

    def into_model(self, line: str) -> T:
        return self._parsing_model(*line.strip().split(","))

    def from_id(self, item_id: int) -> CSVResult[T] | None:
        line_number = item_id + 1
        if self._table_cache:
            if len(self._table_cache) < line_number:
                return None
            return CSVResult(item_id, self.into_model(self._table_cache[line_number]))

        with open(self._file_name, "r") as f:
            for i, line in enumerate(f):
                if i == line_number:
                    return CSVResult(item_id, self.into_model(line))

        return None

    def all(self) -> list[CSVResult[T]]:
        if self._table_cache:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(self._table_cache)
            ]

        with open(self._file_name, "r") as f:
            return [CSVResult(i, self.into_model(line)) for i, line in enumerate(f)]

    def insert(self, item: T) -> None:
        with open(self._file_name, "a") as f:
            f.write(",".join(item.into_str_list()) + "\n")

        if self._table_cache:
            self._table_cache.append(",".join(item.into_str_list()) + "\n")

    def update(self, item_id: int, item: T) -> None:
        with open(self._file_name, "r") as f:
            lines = f.readlines()

        lines[item_id] = ",".join(item.into_str_list()) + "\n"

        with open(self._file_name, "w") as f:
            f.writelines(lines)

        if self._table_cache:
            self._table_cache = lines

    def delete(self, item_id: int) -> None:
        with open(self._file_name, "r") as f:
            lines = f.readlines()

        del lines[item_id]

        with open(self._file_name, "w") as f:
            f.writelines(lines)

        if self._table_cache:
            self._table_cache = lines

    def query(self, query: Callable[[T], bool]) -> list[CSVResult[T]]:
        if self._table_cache:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(self._table_cache)
                if query(self.into_model(line))
            ]

        with open(self._file_name, "r") as f:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(f)
                if query(self.into_model(line))
            ]


# Database END

# Shared state

# user_db = CSVBasedDatabase(
#     file_name="users.csv",
#     model=User,
# )

# HTTP Server START


class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return ((lowerkey, keyval[1]) for (lowerkey, keyval) in self._store.items())

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


class HTTPRequest:
    def __init__(self, client: socket.socket, server: AsyncHTTPServer) -> None:
        self._client = client
        self._server = server

        self.method: str
        self.path: str
        self.version: str
        self.body: bytes

        self.headers: CaseInsensitiveDict = CaseInsensitiveDict()
        self.query_params: dict[str, str] = {}
        self.post_params: dict[str, str] = {}
        self.files: dict[str, bytes] = {}

    async def send_response(
        self,
        status_code: int,
        headers: dict[str, str] = {},
        body: bytes = b"",
    ) -> None:
        response = f"HTTP/1.1 {status_code} {STATUS_CODE[status_code]}\r\n"

        for key, value in headers.items():
            response += f"{key}: {value}\r\n"

        response += f"Content-Length: {len(body)}\r\n\r\n"

        response = response.encode("utf-8") + body

        try:
            await asyncio.get_event_loop().sock_sendall(self._client, response)
        except BrokenPipeError:
            pass

    async def send_json_response(
        self,
        status_code: int,
        headers: dict[str, str] = {},
        data: dict[str, Any] = {},
    ) -> None:
        headers["Content-Type"] = "application/json"

        await self.send_response(
            status_code,
            headers,
            json.dumps(data).encode("utf-8"),
        )

    def _parse_headers(self, headers_bytes: bytes) -> None:
        headers = headers_bytes.decode("utf-8").split("\r\n")

        self.method, self.path, self.version = headers.pop(0).split(" ")

        if "?" in self.path:
            self.path, query_params_raw = self.path.split("?")

            for query_param in query_params_raw.split("&"):
                key, value = query_param.split("=", 1)

                self.query_params[urllib.parse.unquote(key)] = urllib.parse.unquote(
                    value
                ).strip()

        for header in headers:
            key, value = header.split(": ")
            self.headers[key] = value.strip()

    def _parse_multipart(self) -> None:
        if "Content-Type" not in self.headers:
            return

        boundary = "--" + self.headers["Content-Type"].split("; boundary=")[1]

        form_data = self.body.split(boundary.encode("utf-8"))
        for form_entry in form_data[:-1]:
            if not form_entry.strip():
                continue

            headers, body = form_entry.split(b"\r\n\r\n", 1)
            data_type, name = headers.split(b";")[1].strip().split(b"=")

            match data_type:
                case b"name":
                    self.post_params[name.decode().strip('"')] = body.decode(
                        "utf-8"
                    ).strip()
                case b"filename":
                    self.files[name.decode().strip('"')] = body

    def _parse_www_form(self) -> None:
        form_data = self.body.decode("utf-8")

        for form_entry in form_data.split("&"):
            key, value = form_entry.split("=", 1)

            self.post_params[urllib.parse.unquote(key)] = urllib.parse.unquote(
                value
            ).strip()

    async def _parse_request(self) -> None:
        buffer = bytearray()

        loop = asyncio.get_event_loop()
        while b"\r\n\r\n" not in buffer:
            buffer += await loop.sock_recv(self._client, 1024)

        headers, self.body = buffer.split(b"\r\n\r\n", 1)
        self._parse_headers(headers)

        try:
            content_len = int(self.headers["Content-Length"])
        except KeyError:
            return

        if content_len > len(self.body):
            self.body += await loop.sock_recv(
                self._client, content_len - len(self.body)
            )

        content_type = self.headers.get("Content-Type", "")
        if (
            content_type.startswith("multipart/form-data")
            or "form-data" in content_type
            or "multipart/form-data" in content_type
        ):
            self._parse_multipart()
        elif content_type in ("x-www-form", "application/x-www-form-urlencoded"):
            self._parse_www_form()


HttpHandler = Callable[[HTTPRequest], Awaitable[None]]
ServerEventHandler = Callable[[], Awaitable[None]]


class Endpoint:
    def __init__(self, path: str | set[str], handler: HttpHandler, methods: list[str]):
        self.path = path
        self.handler = handler
        self.methods = methods

    def match(self, path: str) -> bool:
        if isinstance(self.path, set):
            return path in self.path

        return self.path == path


class Router:
    def __init__(self, domains: str | set[str]) -> None:
        self.domains = domains
        self.endpoints: set[Endpoint] = set()

    def add_endpoint(
        self, path: str | set[str], methods: list[str] = ["GET"]
    ) -> Callable:
        def decorator(handler: HttpHandler) -> HttpHandler:
            self.endpoints.add(Endpoint(path, handler, methods))
            return handler

        return decorator

    def match(self, domain: str) -> bool:
        if isinstance(self.domains, set):
            return domain in self.domains

        return self.domains == domain

    def find_endpoint(self, path: str) -> Endpoint | None:
        for endpoint in self.endpoints:
            if endpoint.match(path):
                return endpoint

        return None


class AsyncHTTPServer:
    def __init__(self, *, address: str, port: int) -> None:
        self.address = address
        self.port = port

        self.on_start_server_coroutine: ServerEventHandler | None = None
        self.on_close_server_coroutine: ServerEventHandler | None = None

        self.before_request_coroutines: list[HttpHandler] = []
        self.after_request_coroutines: list[HttpHandler] = []

        self.routes: set[Router] = set()

        # statistics!
        self.requests_served = 0

    def on_start_server(self, coro: ServerEventHandler) -> None:
        self.on_start_server_coroutine = coro

    def on_close_server(self, coro: ServerEventHandler) -> None:
        self.on_close_server_coroutine = coro

    def find_router(self, domain: str) -> Router | None:
        for router in self.routes:
            if router.match(domain):
                return router

        return None

    def add_router(self, router: Router) -> None:
        self.routes.add(router)

    async def _handle_routing(self, request: HTTPRequest) -> None:
        try:
            host = request.headers["Host"]
            router = self.find_router(host)

            if router is None:
                await response_404(request)
                return

            endpoint = router.find_endpoint(request.path)

            if endpoint is None:
                await response_404(request)
                return

            if request.method not in endpoint.methods:
                await response_405(request)
                return

            for coro in self.before_request_coroutines:
                await coro(request)

            await endpoint.handler(request)

            for coro in self.after_request_coroutines:
                await coro(request)

        except Exception:
            tb = traceback.format_exc()
            error(f"An error occurred while handling request.\n{tb}")
            await response_500(request, tb)

    async def _handle_request(self, client: socket.socket) -> None:
        request = HTTPRequest(client, self)
        await request._parse_request()

        if "Host" not in request.headers:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            return

        await self._handle_routing(request)

        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except OSError:
            pass

        self.requests_served += 1

        path = f"{request.headers['Host']}{request.path}"
        info(f"Handled {request.method} {path}")

    async def start_server(self) -> None:
        if self.on_start_server_coroutine is not None:
            await self.on_start_server_coroutine()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            sock.bind((self.address, self.port))
            sock.listen(5)

            loop = asyncio.get_event_loop()
            should_close = False
            try:
                while not should_close:
                    await asyncio.sleep(0.01)

                    client, _ = await loop.sock_accept(sock)
                    loop.create_task(self._handle_request(client))
            except asyncio.exceptions.CancelledError:
                should_close = True

        if self.on_close_server_coroutine is not None:
            await self.on_close_server_coroutine()


# HTTP Server END


# HTTP Middleware START


async def response_404(request: HTTPRequest) -> None:
    await request.send_response(
        status_code=404,
        body=b"404 Not Found",
    )


async def response_405(request: HTTPRequest) -> None:
    await request.send_response(
        status_code=405,
        body=b"405 Method Not Allowed",
    )


async def response_500(request: HTTPRequest, tb: str) -> None:
    await request.send_response(
        status_code=500,
        body=f"500 Whoops! Fuck python!\n\n{tb}".encode(),
    )


# HTTP Middleware END


# HTTP Client START


@dataclass
class HTTPResponse:
    url: str
    status_code: int
    http_version: int
    headers: CaseInsensitiveDict
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="ignore")

    def json(self):
        return json.loads(self.body)


class HTTPClient:
    async def __make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        query_params: dict[str, Any] = {},
        body: bytes = b"",
    ) -> HTTPResponse:
        query_data = urllib.parse.urlencode(query_params)
        if query_data:
            url += f"?{query_data}"

        req = urllib.request.Request(url, method=method, data=body, headers=headers)
        response = await asyncio.to_thread(urllib.request.urlopen, req)
        body = await asyncio.to_thread(response.read)

        case_headers = CaseInsensitiveDict()
        for key, value in response.headers.items():
            case_headers[key] = value

        return HTTPResponse(
            url=response.url,
            status_code=response.status,
            http_version=response.version,
            headers=case_headers,
            body=body,
        )

    async def get(
        self,
        url: str,
        headers: dict[str, Any] = {},
        query_params: dict[str, Any] = {},
        body: bytes = b"",
    ) -> HTTPResponse:
        return await self.__make_request("GET", url, headers, query_params, body)

    async def post(
        self,
        url: str,
        headers: dict[str, Any] = {},
        query_params: dict[str, Any] = {},
        body: bytes = b"",
    ) -> HTTPResponse:
        return await self.__make_request("POST", url, headers, query_params, body)


# HTTP Client END


# Helper functions START


def safe_string(s: str) -> str:
    return s.lower().strip().replace(" ", "_")


def create_random_string(n: int) -> str:
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
    )


async def get_user_geolocalisation(ip: str | None) -> UserGeolocalisation:
    http_client = HTTPClient()

    if ip is None or ip in ("127.0.0.1", "localhost"):
        url = "http://ip-api.com/json"
    else:
        url = f"http://ip-api.com/json/{ip}"

    response = await http_client.get(
        url,
        query_params={"fields": "status,countryCode,lat,lon"},
    )
    json_data = response.json()

    if json_data["status"] == "fail":
        return UserGeolocalisation(  # Mumbai, India.
            country_acronym="IN",
            country_code=COUNTRY_CODES["in"],
            latitude=19.0760,
            longitude=72.7777,  # Fixed this.
        )

    return UserGeolocalisation(
        country_acronym=json_data["countryCode"],
        country_code=COUNTRY_CODES[json_data["countryCode"].lower()],
        latitude=json_data["lat"],
        longitude=json_data["lon"],
    )


# Helper functions END


# Bancho Packets START


class BinaryReader:
    def __init__(self, bytes_data: bytes) -> None:
        self.__buffer = bytearray(bytes_data)
        self.__offset = 0

    def __len__(self) -> int:
        return len(self.__buffer[self.__offset :])

    def read(self, offset: int = -1) -> bytes:
        if offset < 0:
            offset = len(self.__buffer) - self.__offset

        data = self.__buffer[self.__offset : self.__offset + offset]
        self.__offset += offset
        return data

    def read_osu_header(self) -> tuple[BanchoPacketID, int]:
        packet_id, size = struct.unpack("<HxI", self.read(HEADER_LEN))
        return BanchoPacketID(packet_id), size

    def read_int(self, size: int, signed: bool) -> int:
        return int.from_bytes(
            self.read(size),
            byteorder="little",
            signed=signed,
        )

    def read_u8(self) -> int:
        return self.read_int(1, False)

    def read_u16(self) -> int:
        return self.read_int(2, False)

    def read_i16(self) -> int:
        return self.read_int(2, True)

    def read_u32(self) -> int:
        return self.read_int(4, False)

    def read_i32(self) -> int:
        return self.read_int(4, True)

    def read_u64(self) -> int:
        return self.read_int(8, False)

    def read_i64(self) -> int:
        return self.read_int(8, True)

    def read_f32(self) -> float:
        return struct.unpack("<f", self.read(4))[0]

    def read_f64(self) -> float:
        return struct.unpack("<f", self.read(8))[0]

    def read_uleb128(self) -> int:
        if self.read_u8() != 0x0B:
            return 0

        val = shift = 0
        while True:
            b = self.read_u8()
            val |= (b & 0b01111111) << shift
            if (b & 0b10000000) == 0:
                break
            shift += 7
        return val

    def read_string(self) -> str:
        s_len = self.read_uleb128()
        return self.read(s_len).decode()

    def read_osu_list(self) -> list[int]:
        count = self.read_u16()
        return [self.read_i32() for _ in range(count)]


class BinaryWriter:
    def __init__(self) -> None:
        self.buffer = bytearray()

    def write_raw(self, data: bytes) -> BinaryWriter:
        self.buffer += data
        return self

    def write_i8(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<b", data)
        return self

    def write_u8(self, data: int) -> BinaryWriter:
        self.buffer.append(data)
        return self

    def write_i16(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<h", data)
        return self

    def write_u16(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<H", data)
        return self

    def write_i32(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<i", data)
        return self

    def write_u32(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<I", data)
        return self

    def write_i64(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<q", data)
        return self

    def write_u64(self, data: int) -> BinaryWriter:
        self.buffer += struct.pack("<Q", data)
        return self

    def write_f32(self, data: float) -> BinaryWriter:
        self.buffer += struct.pack("<f", data)
        return self

    def write_uleb128(self, data: int) -> BinaryWriter:
        arr = bytearray()
        length = 0

        if data == 0:
            self.write_raw(b"\x00")
            return self

        while data > 0:
            arr.append(data & 127)
            data >>= 7
            if data != 0:
                arr[length] |= 128
            length += 1

        self.write_raw(arr)
        return self

    def write_string(self, data: str) -> BinaryWriter:
        if not data:
            self.write_uleb128(0)
            return self

        str_bytes = data.encode("utf-8", "ignore")
        self.write_raw(b"\x0B")
        self.write_uleb128(len(str_bytes))
        self.write_raw(str_bytes)
        return self

    def write_osu_list(self, data: list[int]) -> BinaryWriter:
        self.write_u16(len(data))
        for i in data:
            self.write_i32(i)
        return self


class PacketBuilder(BinaryWriter):
    def __init__(self, packet_id: BanchoPacketID) -> None:
        self.packet_id = packet_id
        super().__init__()

    def finish(self) -> bytearray:
        packet_bytes = bytearray()

        packet_bytes += struct.pack("<h", self.packet_id.value)
        packet_bytes += b"\x00"
        packet_bytes += struct.pack("<l", len(self.buffer))
        packet_bytes += self.buffer

        return packet_bytes


def bancho_notification_packet(message: str) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_NOTIFICATION)
    packet.write_string(message)
    return packet.finish()


def bancho_login_reply_packet(user_id: int) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_LOGIN_REPLY)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_protocol_packet() -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_PROTOCOL_VERSION)
    packet.write_i32(19)
    return packet.finish()


def bancho_channel_info_end_packet() -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_CHANNEL_INFO_END)
    packet.write_u32(0)
    return packet.finish()


def bancho_silence_end_packet(silence_end: int) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_SILENCE_END)
    packet.write_u32(silence_end)
    return packet.finish()


def bancho_login_perms_packet(privileges: int) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_PRIVILEGES)
    packet.write_u32(privileges)
    return packet.finish()


def bancho_user_presence_packet(user: User) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_USER_PRESENCE)
    packet.write_i32(user.user_id)
    packet.write_string(user.username)
    packet.write_u8(user.utc_offset + 24)
    packet.write_u8(user.geoloc.country_code)
    packet.write_u8(user.privileges)
    packet.write_f32(user.geoloc.longitude)
    packet.write_f32(user.geoloc.latitude)
    packet.write_i32(user.current_stats.rank)
    return packet.finish()


def bancho_user_stats_packet(user: User) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_USER_STATS)
    packet.write_i32(user.user_id)
    packet.write_u8(user.status.action.value)
    packet.write_string(user.status.action_text)
    packet.write_string(user.status.action_md5)
    packet.write_i32(user.status.mods.value)
    packet.write_u8(user.status.mode.value)
    packet.write_i32(user.status.beatmap_id)
    packet.write_i64(user.current_stats.ranked_score)
    packet.write_f32(user.current_stats.accuracy / 100)
    packet.write_i32(user.current_stats.playcount)
    packet.write_i64(user.current_stats.total_score)
    packet.write_i32(user.current_stats.rank)
    packet.write_i32(user.current_stats.pp)

    return packet.finish()


def bancho_user_friends_packet(friends_list: list[int]) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_FRIENDS_LIST)
    packet.write_osu_list(friends_list)
    return packet.finish()


def bancho_server_restart_packet(ms: int) -> bytes:
    packet = PacketBuilder(BanchoPacketID.SRV_RESTART)
    packet.write_i32(ms)
    return packet.finish()


packet_handlers: dict[
    BanchoPacketID, Callable[[BinaryReader, User], Awaitable[None]]
] = {}


def register_packet_handler(packet_id: BanchoPacketID) -> Callable:
    def decorator(handler: Callable[[BinaryReader, User], Awaitable[None]]) -> Callable:
        packet_handlers[packet_id] = handler
        return handler

    return decorator


@register_packet_handler(BanchoPacketID.OSU_HEARTBEAT)
async def handle_heartbeat(_: BinaryReader, __: User) -> None:
    pass


@register_packet_handler(BanchoPacketID.OSU_CHANGE_ACTION)
async def handle_change_action(reader: BinaryReader, user: User) -> None:
    user.status.action = BanchoAction(reader.read_u8())
    user.status.action_text = reader.read_string()
    user.status.action_md5 = reader.read_string()
    user.status.mods = OsuMods(reader.read_i32())
    user.status.mode = OsuMode(reader.read_u8())
    user.status.beatmap_id = reader.read_i32()

    # TODO: restricted check
    broadcast_to_all(bancho_user_stats_packet(user))


@register_packet_handler(BanchoPacketID.OSU_REQUEST_STATUS_UPDATE)
async def handle_request_status_update(_: BinaryReader, user: User) -> None:
    user.enqueue(bancho_user_stats_packet(user))


@register_packet_handler(BanchoPacketID.OSU_USER_STATS_REQUEST)
async def handle_user_stats_request(reader: BinaryReader, user: User) -> None:
    user_ids = reader.read_osu_list()

    # TODO: restricted check
    for user_id in filter(lambda x: x != user.user_id, user_ids):
        osu_token = users_id_lookup_cache.get(user_id)
        if osu_token is None:
            continue

        requested_user = users_cache.get(osu_token)
        if requested_user is None:
            continue

        user.enqueue(bancho_user_presence_packet(requested_user))


# Bancho Packets END


# Bancho Models START


@dataclass
class UserGeolocalisation:
    country_acronym: str
    country_code: int
    latitude: float
    longitude: float


@dataclass
class UserStatistics:
    total_score: int = 0
    ranked_score: int = 0
    pp: int = 0
    accuracy: float = 0.0
    playcount: int = 0
    playtime: int = 0
    max_combo: int = 0
    total_hits: int = 0
    rank: int = 0


@dataclass
class UserStatus:
    action: BanchoAction = BanchoAction.IDLE
    action_text: str = ""
    action_md5: str = ""
    mods: OsuMods = OsuMods.NOMOD
    mode: OsuMode = OsuMode.OSU
    beatmap_id: int = 0


class User(CSVModel):
    user_id: int
    username: str
    username_safe: str

    osu_token: str
    osu_version: str

    utc_offset: int
    pm_private: bool
    privileges: BanchoPrivileges

    geoloc: UserGeolocalisation

    silence_end: int
    login_time: int
    latest_activity: int

    status: UserStatus = field(default_factory=UserStatus)
    stats: dict[OsuMode, UserStatistics] = field(
        default_factory=lambda: {mode: UserStatistics() for mode in OsuMode}
    )

    friends: list[int] = field(default_factory=lambda: [1])  # Bot is always a friend.

    is_bot: bool = False

    _packet_queue = bytearray()

    @property
    def current_stats(self) -> UserStatistics:
        return self.stats[self.status.mode]

    def presence_and_stats(self) -> bytes:
        return bancho_user_presence_packet(self) + bancho_user_stats_packet(self)

    def enqueue(self, data: bytes) -> None:
        self._packet_queue += data

    def dequeue(self) -> bytearray:
        data = self._packet_queue.copy()
        self._packet_queue.clear()
        return data


# TODO: Database functionality
def initialise_new_user(
    username: str,
    osu_version: str,
    utc_offset: int,
    geoloc: UserGeolocalisation,
    pm_private: bool,
) -> User:
    return User(
        user_id=len(users_cache) + 2,
        username=username,
        username_safe=safe_string(username),
        osu_token=create_random_string(32),
        osu_version=osu_version,
        utc_offset=utc_offset,
        pm_private=pm_private,
        privileges=BanchoPrivileges.PLAYER
        | BanchoPrivileges.DEVELOPER
        | BanchoPrivileges.SUPPORTER,
        geoloc=geoloc,
        silence_end=0,
        login_time=int(time.time()),
        latest_activity=int(time.time()),
    )


# Bancho Models END


# Bancho Bot START


class BanchoBot(User):

    def __init__(self) -> None:
        self.user_id = 1
        self.username = "Męski oszuścik"
        self.username_safe = safe_string(self.username)

        self.osu_token = create_random_string(32)
        self.osu_version = "bot"

        self.utc_offset = 2
        self.pm_private = False
        self.privileges = BanchoPrivileges.PLAYER | BanchoPrivileges.DEVELOPER

        self.geoloc = UserGeolocalisation(
            country_acronym="RO",
            country_code=COUNTRY_CODES["ro"],
            # Pyongyang, North Korea.
            latitude=39.039219,
            longitude=125.762524,
        )

        self.silence_end = 0
        self.login_time = int(time.time())
        self.latest_activity = int(time.time())

        self.status = UserStatus(
            action=BanchoAction.TESTING,
            action_text="users patience.",
        )

        self.is_bot = True

    def enqueue(self, data: bytes) -> None:
        pass

    @property
    def current_stats(self) -> UserStatistics:
        return UserStatistics(
            total_score=0,
            ranked_score=0,
            pp=2137,
            accuracy=100.0,
            playcount=0,
            playtime=0,
            max_combo=0,
            total_hits=0,
            rank=0,
        )


# Bancho Bot END


# Bancho Cache START


users_id_lookup_cache: dict[int, str] = {}  # user_id: uuid
users_cache: dict[str, User] = {}  # uuid: User


def broadcast_to_all(data: bytes) -> None:
    for user in users_cache.values():
        user.enqueue(data)


# TODO: extend this function
async def add_user_globally(user: User) -> None:
    users_id_lookup_cache[user.user_id] = user.osu_token
    users_cache[user.osu_token] = user


# Bancho Cache END


# Bancho HTTP Logic START


bancho_router = Router(
    {
        "c.akatsuki.gg",
        "ce.akatsuki.gg",
        "c4.akatsuki.gg",
        "c6.akatsuki.gg",
        "127.0.0.1:2137",
    }
)  # funny meme

QUOTES = [
    "Commit your RealistikPanel changes.",
    "Den Bensch.",
    "I'm a bot, I don't have feelings. - GitHub Copilot",
    "Męski oszuścik is gonna get you.",
    "The sigma is crying.",
    "Kill yourself",
    "KYS - Kuopion yliopistollinen sairaala",
    "'shoot yourself' - 'i mean shoot your shot",
]
GIFS = [
    "https://media1.tenor.com/m/omHmObRADasAAAAd/finnish-hospital-kys.gif",
    "https://cdn.discordapp.com/attachments/748687781605408911/1241086998471508179/caption-6.gif?ex=66c43016&is=66c2de96&hm=ad646c33412aedfc6c1ce847a40b9ca951118a6e497d0dded14f89c9a41edc96&",
    "https://media1.tenor.com/m/fkVF3jbeRw0AAAAC/tusk.gif",
    "https://media1.tenor.com/m/5U1iPUrdTc0AAAAC/computer-works-for-me.gif",
    "https://media.discordapp.net/attachments/860168510080024630/1170384558693290004/watermark.gif?ex=66c40dcf&is=66c2bc4f&hm=9288e17e4955871c7d7b77a1f77dcbfaa6ee3a6d72d0cdbcf4b867fad92fca24&",
    "https://media.discordapp.net/attachments/1224840114442862703/1229035907219456090/caption.gif?ex=66c482e2&is=66c33162&hm=d182754a709d146e476e38b1aafff74e7d8fdc69bf4ff4596d85ed7b1d9fbbb4&",
    "https://cdn.discordapp.com/attachments/784836328964489226/1198035021097869453/caption.gif?ex=66c4734f&is=66c321cf&hm=e56cd1f7f427c042d8d0580ecb48aece5cd4f69590932b67a46ef64bada95b33&",
    "https://media.discordapp.net/attachments/860168510080024630/1117605803428433960/togif.gif?ex=66c486c3&is=66c33543&hm=713ce507aa7578a7889fd936b2df8886b987e67b62f14265cfd8e7c2d6e7dffd&",
    "https://media1.tenor.com/m/9B2tvz_W9OQAAAAd/im-in-your-walls.gif",
    "https://media.discordapp.net/attachments/529631920380968972/1184168699695988856/attachment.gif?ex=66c41a4a&is=66c2c8ca&hm=3e5071da1065eda1b0c8d480a97b3baaf754b6473b2de5af1932625b5743f000&",
    "https://media1.tenor.com/m/uGN34orccIEAAAAC/skillissue-skill.gif",
    "https://cdn.discordapp.com/attachments/789123994750025728/1236739139194589204/meski_oszuscik.gif?ex=66c430d4&is=66c2df54&hm=22fe6db029b001196b056961990a1a40950933d24fe797b102a8250fadb57311&",
    "https://media1.tenor.com/m/vRL2z5-nwa8AAAAd/furina-sad.gif",
    "https://media.discordapp.net/attachments/1175144161662488688/1177186929662500954/attachment-2.gif?ex=66c46943&is=66c317c3&hm=4ece032c22bf660e8c723688299c92610a5dfaa5b390dda9461895145b3827af&",
    "https://media1.tenor.com/m/uGN34orccIEAAAAC/skillissue-skill.gif",
]


async def bancho_get(request: HTTPRequest) -> None:
    very_cool = random.choice(QUOTES)
    piwko_of_today = random.choice(GIFS)
    rapapara = f"""
    <center style='font-family: "Comic Sans MS", "Comic Sans", cursive;'>
        <h1>onecho!</h1> <h2>{very_cool}</h2> <br> <img src='{piwko_of_today}'>
    </center>
    """
    await request.send_response(
        status_code=200,
        body=rapapara.encode("utf-8"),
        headers={
            "Content-Type": "text/html; charset=utf-8",
        },
    )


async def bancho_post(request: HTTPRequest) -> None:
    if request.headers["user-agent"] != "osu!":
        await bancho_get(request)
        return

    osu_token = request.headers.get("osu-token")
    if osu_token is None:
        uuid, packets = await bancho_login_handler(request)
        await request.send_response(
            status_code=200,
            headers={"cho-token": uuid},
            body=packets,
        )
        return

    user = users_cache.get(osu_token)
    if user is None:
        await request.send_response(
            status_code=200,
            body=bancho_notification_packet("Server has restarted!")
            + bancho_server_restart_packet(0),
        )
        return

    reader = BinaryReader(request.body)
    while len(reader):
        packet_id, size = reader.read_osu_header()
        packet_reader = BinaryReader(reader.read(size))

        if packet_id in packet_handlers:
            await packet_handlers[packet_id](packet_reader, user)
        else:
            warning(f"Unhandled packet ID {packet_id} from {user.username}")

    user.latest_activity = int(time.time())

    response = user.dequeue()
    await request.send_response(
        status_code=200,
        body=response,
    )


async def bancho_login_handler(request: HTTPRequest) -> tuple[str, bytes]:
    username, password_hash, additional_data, _ = request.body.decode().split("\n")
    osu_ver, utc_offset, _, _, pm_private = additional_data.split("|")

    geolocalisation = await get_user_geolocalisation(
        request.headers.get("x-forwarded-for")
    )

    # Ok so for now we are doing database-less login.
    # TODO: Implement database login
    packet_response = bytearray()

    user = initialise_new_user(
        username,
        osu_ver,
        int(utc_offset),
        geolocalisation,
        pm_private == "1",
    )

    packet_response += bancho_login_reply_packet(user.user_id)
    packet_response += bancho_protocol_packet()
    packet_response += bancho_channel_info_end_packet()
    packet_response += bancho_silence_end_packet(user.silence_end)
    packet_response += bancho_login_perms_packet(user.privileges)

    for online_user in users_cache.values():
        packet_response += online_user.presence_and_stats()

    packet_response += user.presence_and_stats()
    packet_response += bancho_user_friends_packet(user.friends)

    packet_response += bancho_notification_packet("onecho! - because it's that simple!")

    await add_user_globally(user)
    return user.osu_token, packet_response


@bancho_router.add_endpoint("/", methods=["GET", "POST"])
async def bancho_root_handler(request: HTTPRequest) -> None:
    if request.method == "GET":
        await bancho_get(request)
        return

    await bancho_post(request)


# Bancho HTTP Logic END


# Server Entry Point START


async def main() -> int:
    # Initialise bot
    bancho_bot = BanchoBot()
    await add_user_globally(bancho_bot)

    # Initialise server
    server = AsyncHTTPServer(address="127.0.0.1", port=2137)
    server.add_router(bancho_router)

    @server.on_start_server
    async def on_start_server() -> None:
        info("Server started!")

    @server.on_close_server
    async def on_close_server() -> None:
        info("Server closed!")

    await server.start_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))


# Server Entry Point END
