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
import hashlib
import glob
import json
import os
import time
import sys
import socket

from collections.abc import MutableMapping
from collections.abc import Mapping
from collections import OrderedDict

from typing import Any
from typing import TypedDict
from typing import Callable
from typing import Awaitable
from typing import NamedTuple
from typing import get_type_hints

from enum import Enum
from enum import StrEnum
from enum import IntEnum
from enum import IntFlag
from dataclasses import dataclass
from dataclasses import field

# Global Constants START


DEBUG = "debug" in sys.argv
SETTING_MAIN_DOMAIN = os.environ.get("MAIN_DOMAIN", "localhost")
SETTING_HTTP_PORT = int(os.environ.get("HTTP_PORT", 2137))
SETTING_HTTP_HOST = os.environ.get("HTTP_HOST", "0.0.0.0")

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


# Global Constants END


# Enums START


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


class OsuRelationship(StrEnum):
    FRIEND = "FRIEND"
    BLOCK = "BLOCK"


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


# Enums END


# Logger START


def info(text: str, *, extra: dict[str, Any] | None = None):
    data = {
        "level": "INFO",
        "message": text,
    }

    if extra:
        data["extra"] = extra # type: ignore
    print(json.dumps(data))


def error(text: str, *, extra: dict[str, Any] | None = None):
    data = {
        "level": "ERROR",
        "message": text,
    }

    if extra:
        data["extra"] = extra # type: ignore
    print(json.dumps(data))


def warning(text: str, *, extra: dict[str, Any] | None = None):
    data = {
        "level": "WARNING",
        "message": text,
    }

    if extra:
        data["extra"] = extra # type: ignore
    print(json.dumps(data))


def debug(text: str, *, extra: dict[str, Any] | None = None):
    if not DEBUG:
        return
    
    data = {
        "level": "DEBUG",
        "message": text,
    }

    if extra:
        data["extra"] = extra # type: ignore
    print(json.dumps(data))


# Logger END


# Database START


def _parse_to_type[T](value: str, value_type: type[T]) -> T:
    if value_type is str:
        return value_type(value)

    if issubclass(value_type, (int, str, float, Enum)):
        return value_type(value)

    if value_type is bool:
        return value_type(value.lower() == "true")

    raise ValueError("Skill issue type??")


def _parse_from_type(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, Enum):
        return _parse_from_type(value.value)

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
        model: type[T],
        increment_from: int = 0,
        cache_table: bool = True,
    ) -> None:
        self._parsing_model = model
        self._file_name = file_name
        self._increment_from = increment_from
        self._cache_table = cache_table
        self._table_cache: list[str] = []
        self.__innit__()

        if self._cache_table:
            if os.path.exists(self._file_name):
                with open(self._file_name, "r") as f:
                    self._table_cache = f.readlines()

    def __len__(self) -> int:
        if self._table_cache:
            return len(self._table_cache)

        with open(self._file_name, "r") as f:
            return len(f.readlines())

    def __innit__(self) -> None:
        if not os.path.exists(self._file_name):
            with open(self._file_name, "w+") as f:
                f.write("")

    def into_model(self, line: str) -> T:
        return self._parsing_model(*line.strip().split(","))

    def from_id(self, item_id: int) -> CSVResult[T] | None:
        if self._table_cache:
            if len(self._table_cache) + self._increment_from < item_id:
                return None

            record = self._table_cache[item_id - self._increment_from]
            if record.startswith("#"):
                return None

            return CSVResult(
                item_id,
                self.into_model(record),
            )

        with open(self._file_name, "r") as f:
            for i, line in enumerate(f, start=self._increment_from):
                if i == item_id - self._increment_from:
                    return CSVResult(item_id, self.into_model(line))

        return None

    def all(self) -> list[CSVResult[T]]:
        if self._table_cache:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(self._table_cache, start=self._increment_from)
                if line.strip() and not line.startswith("#")
            ]

        with open(self._file_name, "r") as f:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(f, start=self._increment_from)
                if line.strip() and not line.startswith("#")
            ]

    def insert(self, item: T) -> int:
        if self._cache_table:
            self._table_cache.append(",".join(item.into_str_list()) + "\n")

        with open(self._file_name, "a") as f:
            f.write(",".join(item.into_str_list()) + "\n")

        with open(self._file_name, "r") as f:
            line_count = len(f.readlines())

        return self._increment_from + line_count - 1

    def update(self, item_id: int, item: T) -> None:
        with open(self._file_name, "r") as f:
            lines = f.readlines()

        lines[item_id - self._increment_from] = ",".join(item.into_str_list()) + "\n"

        with open(self._file_name, "w") as f:
            f.writelines(lines)

        if self._cache_table:
            self._table_cache = lines

    def delete(self, item_id: int) -> None:
        with open(self._file_name, "r") as f:
            lines = f.readlines()

        lines[item_id - self._increment_from] = (
            "#" + lines[item_id - self._increment_from]
        )

        with open(self._file_name, "w") as f:
            f.writelines(lines)

        if self._cache_table:
            self._table_cache = lines

    def query(self, query: Callable[[T], bool]) -> list[CSVResult[T]]:
        if self._table_cache:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(self._table_cache, start=self._increment_from)
                if line.strip()
                and query(self.into_model(line))
                and not line.startswith("#")
            ]

        with open(self._file_name, "r") as f:
            return [
                CSVResult(i, self.into_model(line))
                for i, line in enumerate(f, start=self._increment_from)
                if line.strip()
                and query(self.into_model(line))
                and not line.startswith("#")
            ]

    def query_one(self, query: Callable[[T], bool]) -> CSVResult[T] | None:
        record = self.query(query)

        if not any(record):
            return None

        return record[0]


# Database END


# Database Models START


class UserStatsModel(CSVModel):
    user_id: int
    mode: int
    total_score: int = 0
    ranked_score: int = 0
    pp: int = 0
    playcount: int = 0
    playtime: int = 0
    accuracy: float = 0.0
    max_combo: int = 0
    total_hits: int = 0
    level: int = 1


class UserModel(CSVModel):
    username: str
    username_safe: str
    email: str
    password_md5: str  # TODO: encryption
    privileges: int
    country: str = "xx"
    silence_end: int = 0
    creation_time: int = 0
    latest_activity: int = 0


class UserRelationshipModel(CSVModel):
    user_id: int
    friend_id: int
    relation_type: OsuRelationship
    since: int  # unix


class ChannelModel(CSVModel):
    name: str
    topic: str
    write_privileges: int
    read_privileges: int
    auto_join: bool


# Database Models END


# Database Instances START


user_db = CSVBasedDatabase[UserModel](
    file_name="database/users.csv",
    model=UserModel,
    increment_from=3,  # 1 - bot (hardcoded), 2 - peppy (cannot message)
)

user_stats_db: dict[OsuMode, CSVBasedDatabase[UserStatsModel]] = {
    mode: CSVBasedDatabase[UserStatsModel](
        file_name=f"database/user_stats_{mode.name.lower()}.csv",
        model=UserStatsModel,
        increment_from=3,  # 1 - bot (hardcoded), 2 - peppy (cannot message)
    )
    for mode in OsuMode
}

user_relationship_db = CSVBasedDatabase[UserRelationshipModel](
    file_name="database/user_relationships.csv",
    model=UserRelationshipModel,
)

channel_db = CSVBasedDatabase[ChannelModel](
    file_name="database/channels.csv",
    model=ChannelModel,
)


# Database Instances END


# Database Functions START


class UserCreationResponse(TypedDict):
    user_id: int
    user_model: UserModel


def create_user_in_database(
    username: str,
    email: str,
    password_md5: str,
    country_acronym: str,
) -> UserCreationResponse:

    default_perms = BanchoPrivileges.PLAYER | BanchoPrivileges.SUPPORTER
    user_model = UserModel(
        username=username,
        username_safe=safe_string(username),
        email=email,
        password_md5=password_md5,
        country=country_acronym,
        privileges=default_perms.value,
        creation_time=int(time.time()),
        latest_activity=int(time.time()),
    )

    user_id = user_db.insert(user_model)
    return {"user_id": user_id, "user_model": user_model}


def update_user_in_database(user: User) -> None:
    user_model = user_db.from_id(user.user_id)

    if not user_model:
        return  # what

    # update what we can
    user_model.result.username = user.username
    user_model.result.username_safe = user.username_safe
    user_model.result.email = user.email
    user_model.result.privileges = user.privileges.value
    user_model.result.silence_end = user.silence_end
    user_model.result.latest_activity = user.latest_activity

    user_db.update(user.user_id, user_model.result)


def create_user_stats_in_database(user_id: int) -> None:
    for mode in OsuMode:
        database = user_stats_db[mode]

        user_stats = UserStatsModel(
            user_id=user_id,
            mode=mode.value,
        )
        database.insert(user_stats)


def create_channel_in_database(
    name: str,
    topic: str,
    write_privileges: BanchoPrivileges = BanchoPrivileges.PLAYER,
    read_privileges: BanchoPrivileges = BanchoPrivileges.PLAYER,
    auto_join: bool = False,
) -> None:
    channel_model = ChannelModel(
        name=name,
        topic=topic,
        write_privileges=write_privileges.value,
        read_privileges=read_privileges.value,
        auto_join=auto_join,
    )

    channel_db.insert(channel_model)


def create_user_relationship_in_database(
    user_id: int,
    friend_id: int,
    relation_type: OsuRelationship,
) -> None:
    relationship_model = UserRelationshipModel(
        user_id=user_id,
        friend_id=friend_id,
        relation_type=relation_type,
        since=int(time.time()),
    )

    user_relationship_db.insert(relationship_model)


def delete_user_relationship_in_database(
    user_id: int,
    friend_id: int,
    relation_type: OsuRelationship,
) -> None:
    relationship_model = user_relationship_db.query_one(
        lambda x: x.user_id == user_id
        and x.friend_id == friend_id
        and x.relation_type == relation_type
    )

    if not relationship_model:
        return

    user_relationship_db.delete(relationship_model.id)


# Database Functions END


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

        ending_route = self.path.split("/")[-1]
        if ending_route and ending_route[0] == "{" and ending_route[-1] == "}":
            # let the handler handle the rest
            endpoint_route_without_param = "/".join(self.path.split("/")[:-1])
            return path.startswith(endpoint_route_without_param)

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

        info(
            f"Starting HTTP server on {self.address}:{self.port}",
        )

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


@dataclass
class UserGeolocalisation:
    country_acronym: str
    country_code: int
    latitude: float
    longitude: float


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
            country_acronym="in",
            country_code=COUNTRY_CODES["in"],
            latitude=19.0760,
            longitude=72.7777,  # Fixed this.
        )

    country_acronym = json_data["countryCode"].lower()
    return UserGeolocalisation(
        country_acronym=country_acronym,
        country_code=COUNTRY_CODES[country_acronym],
        latitude=json_data["lat"],
        longitude=json_data["lon"],
    )


def check_password(password: str, db_password: str) -> bool:
    # Since for now we are using md5, we can just compare them.
    return password == db_password


# Helper functions END


# Bancho Packets START


ByteLike = bytes | bytearray


class PacketWriter:
    __slots__ = ("_packet_id", "_buf")

    def __init__(self, packet_id: BanchoPacketID) -> None:
        self._packet_id = packet_id
        self._buf = bytearray()

    def write_i8(self, value: int) -> PacketWriter:
        self._buf.append(value)
        return self

    def write_u8(self, value: int) -> PacketWriter:
        self._buf.append(value)
        return self

    def write_i16(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<h", value))
        return self

    def write_u16(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<H", value))
        return self

    def write_i32(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<i", value))
        return self

    def write_u32(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<I", value))
        return self

    def write_i64(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<q", value))
        return self

    def write_u64(self, value: int) -> PacketWriter:
        self._buf.extend(struct.pack("<Q", value))
        return self

    def write_f32(self, value: float) -> PacketWriter:
        self._buf.extend(struct.pack("<f", value))
        return self
    
    def write_raw(self, value: bytes) -> PacketWriter:
        self._buf.extend(value)
        return self

    def write_uleb128(self, value: int) -> PacketWriter:
        while value >= 0x80:
            self._buf.append((value & 0x7F) | 0x80)
            value >>= 7
        self._buf.append(value)
        return self

    def write_str(self, value: str) -> PacketWriter:
        # Exists byte.
        if not value:
            self.write_i8(0)
            return self

        self.write_i8(0xB)
        data = value.encode("utf-8", "ignore")
        self.write_uleb128(len(data))
        self._buf.extend(data)
        return self

    def write_list(self, values: list[int]) -> PacketWriter:
        self.write_u16(len(values))
        for value in values:
            self.write_i32(value)
        return self

    def finish(self) -> bytearray:
        packet_bytes = bytearray()

        packet_bytes += struct.pack("<h", self._packet_id.value)
        packet_bytes += b"\x00"
        packet_bytes += struct.pack("<l", len(self._buf))
        packet_bytes += self._buf

        return packet_bytes


class PacketReader:
    __slots__ = (
        "_buf",
        "_pos",
    )

    @property
    def empty(self) -> bool:
        return self._pos >= len(self._buf)

    def __init__(self, buf: ByteLike) -> None:
        self._buf = buf
        self._pos = 0

    def read_i8(self) -> int:
        value = self._buf[self._pos]
        self._pos += 1
        return value

    def read_u8(self) -> int:
        value = self._buf[self._pos]
        self._pos += 1
        return value

    def read_i16(self) -> int:
        value = struct.unpack("<h", self._buf[self._pos : self._pos + 2])[0]
        self._pos += 2
        return value

    def read_u16(self) -> int:
        value = struct.unpack("<H", self._buf[self._pos : self._pos + 2])[0]
        self._pos += 2
        return value

    def read_i32(self) -> int:
        value = struct.unpack("<i", self._buf[self._pos : self._pos + 4])[0]
        self._pos += 4
        return value

    def read_u32(self) -> int:
        value = struct.unpack("<I", self._buf[self._pos : self._pos + 4])[0]
        self._pos += 4
        return value

    def read_i64(self) -> int:
        value = struct.unpack("<q", self._buf[self._pos : self._pos + 8])[0]
        self._pos += 8
        return value

    def read_u64(self) -> int:
        value = struct.unpack("<Q", self._buf[self._pos : self._pos + 8])[0]
        self._pos += 8
        return value

    def read_f32(self) -> float:
        value = struct.unpack("<f", self._buf[self._pos : self._pos + 4])[0]
        self._pos += 4
        return value

    def read_uleb128(self) -> int:
        value = 0
        shift = 0
        while True:
            byte = self._buf[self._pos]
            self._pos += 1
            value |= (byte & 0x7F) << shift
            if byte < 0x80:
                return value
            shift += 7

    def read_str(self) -> str:
        if self.read_i8() != 0xB:
            return ""

        length = self.read_uleb128()
        string = self._buf[self._pos : self._pos + length].decode()
        self._pos += length
        return string

    def read_list(self) -> list[int]:
        length = self.read_u16()
        return [self.read_i32() for _ in range(length)]

    def skip(self, length: int) -> None:
        self._pos += length

    def read_header(self) -> tuple[BanchoPacketID, int]:
        packet_id = BanchoPacketID(self.read_u16())
        # Pad byte.
        self.skip(1)
        packet_length = self.read_u32()
        return packet_id, packet_length

    def remove_excess(self, packet_size: int) -> bytes:
        excess = self._buf[self._pos + packet_size :]
        self._buf = self._buf[: self._pos + packet_size]
        return excess
    

    def read_remaining_bytes(self) -> bytes:
        return self._buf[self._pos :]

    def __iter__(self) -> PacketReader:
        return self

    def __next__(self) -> tuple[BanchoPacketID, int]:
        if self.empty:
            raise StopIteration
        return self.read_header()


@dataclass
class PacketContext:
    id: BanchoPacketID
    length: int
    reader: PacketReader

    @staticmethod
    def create_from_buffers(buf: ByteLike) -> list[PacketContext]:
        reader = PacketReader(buf)
        ctxs: list[PacketContext] = []

        while not reader.empty:
            packet_id, length = reader.read_header()
            ctxs.append(PacketContext(packet_id, length, reader))
            reader = PacketReader(reader.remove_excess(length))

        return ctxs


PacketHandler = Callable[[PacketReader, "User"], Awaitable[None]]


class PacketRouter:
    __slots__ = ("_restricted_packets", "_handlers")

    def __init__(self) -> None:
        self._restricted_packets: list[int] = []
        self._handlers: dict[BanchoPacketID, PacketHandler] = {}

    def add_handler(self, packet_id: BanchoPacketID, restricted=False) -> Callable:
        def decorator(handler: PacketHandler) -> PacketHandler:
            self._handlers[packet_id] = handler

            if restricted:
                self._restricted_packets.append(packet_id.value)

            return handler

        return decorator

    async def route(self, ctx: PacketContext, user: User) -> None:
        if ctx.id in self._handlers:

            if not ctx.id.value in self._restricted_packets and user.restricted:
                return

            await self._handlers[ctx.id](ctx.reader, user)
        else:
            warning(
                f"Unhandled packet ID {ctx.id} from {user.username} ({user.user_id})"
            )


def bancho_notification_packet(message: str) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_NOTIFICATION)
    packet.write_str(message)
    return packet.finish()


def bancho_login_reply_packet(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_LOGIN_REPLY)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_logout_packet(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_USER_LOGOUT)
    packet.write_i32(user_id)
    packet.write_u8(0)
    return packet.finish()


def bancho_protocol_packet() -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_PROTOCOL_VERSION)
    packet.write_i32(19)
    return packet.finish()


def bancho_channel_info_packet(channel: BanchoChannel) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_CHANNEL_INFO)
    packet.write_str(channel.name)
    packet.write_str(channel.topic)
    packet.write_u16(len(channel))
    return packet.finish()


def bancho_channel_join_success_packet(channel: BanchoChannel) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_CHANNEL_JOIN_SUCCESS)
    packet.write_str(channel.name)
    return packet.finish()


def bancho_channel_kick_packet(channel: BanchoChannel) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_CHANNEL_KICK)
    packet.write_str(channel.name)
    return packet.finish()


def bancho_channel_info_end_packet() -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_CHANNEL_INFO_END)
    packet.write_u32(0)
    return packet.finish()


def bancho_silence_end_packet(silence_end: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SILENCE_END)
    packet.write_u32(silence_end)
    return packet.finish()


def bancho_login_perms_packet(privileges: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_PRIVILEGES)
    packet.write_u32(privileges)
    return packet.finish()


def bancho_user_presence_packet(user: User) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_USER_PRESENCE)
    packet.write_i32(user.user_id)
    packet.write_str(user.username)
    packet.write_u8(user.utc_offset + 24)
    packet.write_u8(user.geoloc.country_code)
    packet.write_u8(user.privileges)
    packet.write_f32(user.geoloc.longitude)
    packet.write_f32(user.geoloc.latitude)
    packet.write_i32(user.current_stats.rank)
    return packet.finish()


def bancho_user_stats_packet(user: User) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_USER_STATS)
    packet.write_i32(user.user_id)
    packet.write_u8(user.status.action.value)
    packet.write_str(user.status.action_text)
    packet.write_str(user.status.action_md5)
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
    packet = PacketWriter(BanchoPacketID.SRV_FRIENDS_LIST)
    packet.write_list(friends_list)
    return packet.finish()


def bancho_user_dm_blocked_packet(username: str) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_USER_DM_BLOCKED)
    packet.write_str("")
    packet.write_str("")
    packet.write_str(username)
    packet.write_i32(0)
    return packet.finish()


def bancho_user_silenced_packet(username: str) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_TARGET_IS_SILENCED)
    packet.write_str("")
    packet.write_str("")
    packet.write_str(username)
    packet.write_i32(0)
    return packet.finish()


def bancho_send_message_packet(
    sender: str, message: str, recipient: str, sender_id: int
) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SEND_MESSAGE)
    packet.write_str(sender)
    packet.write_str(message)
    packet.write_str(recipient)
    packet.write_i32(sender_id)
    return packet.finish()


def bancho_server_restart_packet(ms: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_RESTART)
    packet.write_i32(ms)
    return packet.finish()


def bancho_join_watch_party(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_FELLOW_SPECTATOR_JOINED)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_leave_watch_party(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_FELLOW_SPECTATOR_LEFT)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_watch_party_joined_host(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SPECTATOR_JOINED)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_watch_party_left_host(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SPECTATOR_LEFT)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_watch_party_no_maidens(user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SPECTATOR_CANT_SPECTATE)
    packet.write_i32(user_id)
    return packet.finish()

# TODO: Actually bother building this and maybe do realtime PP :eyes:
def bancho_spectate_frames(frame_data: bytes) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SPECTATE_FRAMES)
    packet.write_raw(frame_data)
    return packet.finish()


def bancho_spectate_no_beatmap_notify(lame_user_id: int) -> bytes:
    packet = PacketWriter(BanchoPacketID.SRV_SPECTATOR_CANT_SPECTATE)
    packet.write_i32(lame_user_id)
    return packet.finish()

packets_router = PacketRouter()


@packets_router.add_handler(BanchoPacketID.OSU_HEARTBEAT, restricted=True)
async def bancho_heartbeat_handler(reader: PacketReader, user: User) -> None:
    pass


@packets_router.add_handler(BanchoPacketID.OSU_CHANGE_ACTION, restricted=True)
async def bancho_change_action_handler(reader: PacketReader, user: User) -> None:
    user.status.action = BanchoAction(reader.read_u8())
    user.status.action_text = reader.read_str()
    user.status.action_md5 = reader.read_str()
    user.status.mods = OsuMods(reader.read_i32())
    user.status.mode = OsuMode(reader.read_u8())
    user.status.beatmap_id = reader.read_i32()

    if not user.restricted:
        broadcast_to_online_users(bancho_user_stats_packet(user))


@packets_router.add_handler(BanchoPacketID.OSU_REQUEST_STATUS_UPDATE, restricted=True)
async def bancho_request_status_update_handler(
    reader: PacketReader, user: User
) -> None:
    user.enqueue(bancho_user_stats_packet(user))


@packets_router.add_handler(BanchoPacketID.OSU_USER_STATS_REQUEST, restricted=True)
async def bancho_user_stats_request_handler(reader: PacketReader, user: User) -> None:
    user_ids = reader.read_list()

    for user_id in filter(lambda x: x != user.user_id, user_ids):
        token = user_id_to_token.get(user_id)
        if token is None:
            continue

        requested_user = users.get(token)
        if requested_user is None:
            continue

        if requested_user.restricted:
            continue

        user.enqueue(bancho_user_stats_packet(requested_user))


@packets_router.add_handler(BanchoPacketID.OSU_USER_PRESENCE_REQUEST)
async def bancho_user_presence_request_handler(
    reader: PacketReader, user: User
) -> None:
    user_ids = reader.read_list()

    for user_id in user_ids:
        token = user_id_to_token.get(user_id)
        if token is None:
            continue

        requested_user = users.get(token)
        if requested_user is None:
            continue

        user.enqueue(bancho_user_presence_packet(requested_user))


@packets_router.add_handler(BanchoPacketID.OSU_USER_PRESENCE_REQUEST_ALL)
async def bancho_user_stats_request_all_handler(
    reader: PacketReader, user: User
) -> None:
    buffer = bytearray()
    for online_user in users.values():
        if online_user.restricted:
            continue

        buffer += bancho_user_presence_packet(online_user)

    user.enqueue(bytes(buffer))


@packets_router.add_handler(BanchoPacketID.OSU_CHANNEL_JOIN, restricted=True)
async def bancho_channel_join_handler(reader: PacketReader, user: User) -> None:
    channel_name = reader.read_str()

    if not channel_name.startswith("#"):
        return

    channel = channels.get(channel_name)

    if channel is None or not user.join_channel(channel):
        error(f"{user.username} failed to join {channel_name}")


IGNORED_CHANNELS = ["#userlog"]


@packets_router.add_handler(BanchoPacketID.OSU_CHANNEL_PART, restricted=True)
async def bancho_channel_part_handler(reader: PacketReader, user: User) -> None:
    channel_name = reader.read_str()

    if not channel_name.startswith("#"):
        return

    if channel_name in IGNORED_CHANNELS:
        return

    channel = channels.get(channel_name)

    if channel is None or not user.leave_channel(channel):
        error(f"{user.username} failed to leave {channel_name}")


@packets_router.add_handler(BanchoPacketID.OSU_LOGOUT, restricted=True)
async def bancho_logout_handler(reader: PacketReader, user: User) -> None:
    if (time.time() - user.login_time) < 1:
        return

    user.logout()
    user.update_user()


@packets_router.add_handler(BanchoPacketID.OSU_RECEIVE_UPDATES, restricted=True)
async def bancho_receive_updates_handler(reader: PacketReader, user: User) -> None:
    pass  # client does that automatically


@packets_router.add_handler(BanchoPacketID.OSU_TOGGLE_BLOCK_NON_FRIEND_DMS)
async def bancho_toggle_block_non_friend_dms_handler(
    reader: PacketReader, user: User
) -> None:
    value = reader.read_i32()
    user.pm_private = value == 1


@packets_router.add_handler(BanchoPacketID.OSU_FRIEND_ADD)
async def bancho_friend_add_handler(reader: PacketReader, user: User) -> None:
    user_id = reader.read_i32()

    token = user_id_to_token.get(user_id)
    if token is None:
        return

    requested_user = users.get(token)
    if requested_user is None:
        return

    if requested_user.is_bot_client:  # bot is immune
        return

    if user_id in user.blocks:
        user.remove_block(user_id)

    if user_id in user.friends:
        return

    user.update_user()
    user.add_friend(user_id)


@packets_router.add_handler(BanchoPacketID.OSU_FRIEND_REMOVE)
async def bancho_friend_remove_handler(reader: PacketReader, user: User) -> None:
    user_id = reader.read_i32()

    token = user_id_to_token.get(user_id)
    if token is None:
        return

    requested_user = users.get(token)
    if requested_user is None:
        return

    if requested_user.is_bot_client:  # bot is immune
        return

    if not user_id in user.friends:
        return

    user.update_user()
    user.remove_friend(user_id)


@packets_router.add_handler(BanchoPacketID.OSU_JOIN_LOBBY)
async def bancho_join_lobby_handler(reader: PacketReader, user: User) -> None:
    user.in_lobby = True

    # TODO: list all matches


@packets_router.add_handler(BanchoPacketID.OSU_PART_LOBBY)
async def bancho_part_lobby_handler(reader: PacketReader, user: User) -> None:
    user.in_lobby = False


@packets_router.add_handler(BanchoPacketID.OSU_SEND_PRIVATE_MESSAGE)
async def bancho_send_private_message_handler(reader: PacketReader, user: User) -> None:
    reader.read_str()
    message = reader.read_str()
    recipient = reader.read_str()
    reader.read_i32()

    if user.silenced:
        return

    message = message.strip()
    if not message:
        return

    targe_osu_token = username_to_token.get(safe_string(recipient))
    if targe_osu_token is None:
        return

    target = users.get(targe_osu_token)
    if target is None:
        return

    if user.user_id in target.blocks:
        user.enqueue(bancho_user_dm_blocked_packet(target.username))
        return

    if target.pm_private and user.user_id not in target.friends:
        user.enqueue(bancho_user_dm_blocked_packet(target.username))
        return

    if target.silenced:
        user.enqueue(bancho_user_silenced_packet(target.username))
        return

    if len(message) > 2000:
        message = f"{message[:2000]}... (truncated)"

    if target.is_bot_client:
        if not message.startswith("!"):
            user.send(f"{target.username} is gonna get you.", sender=target)
            return

        resp = await bancho_bot.handle_commands(user, message, in_channel=False)
        if resp is None:
            user.send("Command not found.", sender=target)
            return

        if resp.response is None:
            return

        user.send(resp.response, sender=target)
    else:
        target.send(message, sender=user)

    user.update_user()


@packets_router.add_handler(BanchoPacketID.OSU_SEND_PUBLIC_MESSAGE)
async def bancho_send_public_message_handler(reader: PacketReader, user: User) -> None:
    reader.read_str()
    message = reader.read_str()
    recipient = reader.read_str()
    reader.read_i32()

    if user.silenced:
        return

    message = message.strip()
    if not message:
        return

    if recipient in IGNORED_CHANNELS:
        return
    elif recipient == "#spectator":
        if user.watch_party is not None:
            channel = user.watch_party.channel
        else:
            return
    elif recipient == "#multiplayer":
        ...
        # TODO: multiplayer
    else:
        channel = channels.get(recipient)

    if channel is None:
        return

    if user not in channel.users:
        return

    if not channel.can_write(user.privileges):
        return

    if len(message) > 2000:
        message = f"{message[:2000]}... (truncated)"

    channel.send(message, sender=user)
    if message.startswith("!"):
        resp = await bancho_bot.handle_commands(user, message, in_channel=True)

        if resp is None:
            channel.send("Command not found.", sender=bancho_bot)
            return

        if resp.response is None:
            return

        if resp.invisible_response:
            user.send(resp.response, sender=bancho_bot, channel=channel)
        else:
            channel.send(resp.response, sender=bancho_bot)

    user.update_user()


@packets_router.add_handler(BanchoPacketID.OSU_START_SPECTATING)
async def bancho_start_spectating_handler(reader: PacketReader, user: User) -> None:
    user_id = reader.read_i32()

    token = user_id_to_token.get(user_id)
    if token is None:
        return

    target = users.get(token)
    if target is None:
        return

    if target.is_bot_client:
        user.enqueue(bancho_notification_packet("The bot is immune to spectating."))
        user.enqueue(bancho_leave_watch_party(user.user_id))
        return


    target.join_watch_party(user)


@packets_router.add_handler(BanchoPacketID.OSU_STOP_SPECTATING)
async def bancho_stop_spectating_handler(reader: PacketReader, user: User) -> None:
    if user.watch_party is None:
        error(
            f"{user.username!r} has dementia and tried to stop spectating despite not spectating."
        )
        return

    user.watch_party.the_watched.leave_watch_party(user)



@packets_router.add_handler(BanchoPacketID.OSU_SPECTATE_FRAMES)
async def bancho_spectate_frames_handler(reader: PacketReader, user: User) -> None:
    frame_data = reader.read_remaining_bytes()

    if user.watch_party is None:
        error(
            f"{user.username!r} is not in a watch party BUT tried submitting frames. "
            "Its like a ghost in the machine. - GitHub Copilot"
        )
        return
    
    if user.watch_party.the_watched != user:
        error(
            f"{user.username!r} tried submitting frames for {user.watch_party.the_watched.username!r} "
            "despite them being more than capable of doing it themselves."
        )
        return
    
    user.watch_party.enqueue(
        bancho_spectate_frames(frame_data)
    )


@packets_router.add_handler(BanchoPacketID.OSU_CANT_SPECTATE)
async def bancho_cant_spectate_haha_handler(reader: PacketReader, user: User) -> None:
    if user.watch_party is None:
        error(
            f"{user.username!r} tried telling us they can't spectate despite not spectating. "
            "They are a special kind of stupid."
        )
        return
    
    user.watch_party.enqueue(
        bancho_watch_party_no_maidens(user.user_id)
    )


# Bancho Packets END


# Budget Redis START


def __partition(array: list[LeaderboardEntry], low: int, high: int) -> int:
    i = low - 1
    j = low

    while j < high:
        if array[j]["score"] > array[high]["score"]:
            array[i + 1], array[j] = array[j], array[i + 1]
            i += 1
        j += 1

    array[i + 1], array[high] = array[high], array[i + 1]
    return i + 1


def reversed_quick_sort(array: list[LeaderboardEntry], low: int, high: int) -> None:
    if low < high:
        pi = __partition(array, low, high)
        reversed_quick_sort(array, low, pi - 1)
        reversed_quick_sort(array, pi + 1, high)


def sort_leaderboard(array: list[LeaderboardEntry]):
    reversed_quick_sort(array, 0, len(array) - 1)


class LeaderboardEntry(TypedDict):
    user_id: int
    score: int


class BanchoLeaderboard:
    __slots__ = ("_lock", "_leaderboard", "_lookup_table")

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._leaderboard: list[LeaderboardEntry] = []
        self._lookup_table: dict[int, int] = {}  # user_id -> placement

    def __len__(self) -> int:
        return len(self._leaderboard)

    async def _rebuild_leaderboard(self) -> None:
        async with self._lock:
            sort_leaderboard(self._leaderboard)
            for placement, entry in enumerate(self._leaderboard):
                self._lookup_table[entry["user_id"]] = placement

    async def get_placement(self, user_id: int) -> int | None:
        async with self._lock:
            return self._lookup_table.get(user_id)

    async def add_entry(self, user_id: int, score: int) -> None:
        async with self._lock:
            if user_id in self._lookup_table:
                self._leaderboard[self._lookup_table[user_id]]["score"] = score
            else:
                self._leaderboard.append({"user_id": user_id, "score": score})

        await self._rebuild_leaderboard()

    async def update_entry(self, user_id: int, score: int) -> None:
        await self.add_entry(user_id, score)

    async def remove_entry(self, user_id: int) -> None:
        async with self._lock:
            placement = self._lookup_table.pop(user_id)
            self._leaderboard.pop(placement)

        await self._rebuild_leaderboard()


# fmt: off
leaderboards = {
    mode: BanchoLeaderboard()
    for mode in OsuMode
}
# fmt: on


# Budget Redis END


# Bancho Objects START


@dataclass
class BanchoUserStatus:
    action: BanchoAction = BanchoAction.IDLE
    action_text: str = ""
    action_md5: str = ""
    mods: OsuMods = OsuMods.NOMOD
    mode: OsuMode = OsuMode.OSU
    beatmap_id: int = 0


@dataclass
class UserStatistics:
    total_score: int
    ranked_score: int
    pp: int
    playcount: int
    playtime: int
    accuracy: float
    max_combo: int
    total_hits: int
    level: int
    rank: int

    @staticmethod
    def from_model(model: UserStatsModel) -> UserStatistics:
        return UserStatistics(
            total_score=model.total_score,
            ranked_score=model.ranked_score,
            pp=model.pp,
            playcount=model.playcount,
            playtime=model.playtime,
            accuracy=model.accuracy,
            max_combo=model.max_combo,
            total_hits=model.total_hits,
            level=model.level,
            rank=0,
        )


@dataclass
class UserWatchParty:
    the_watched: User
    the_watchers: list[User]
    channel: BanchoChannel


    def enqueue(self, packet: bytes) -> None:
        for watcher in self.the_watchers:
            watcher.enqueue(packet)

@dataclass
class User:
    user_id: int
    username: str
    username_safe: str

    email: str

    osu_token: str
    osu_version: str

    utc_offset: int
    pm_private: bool
    privileges: BanchoPrivileges

    geoloc: UserGeolocalisation

    silence_end: int
    login_time: int
    latest_activity: int

    stats: dict[OsuMode, UserStatistics] = field(default_factory=dict)
    status: BanchoUserStatus = field(default_factory=BanchoUserStatus)

    friends: list[int] = field(default_factory=list)
    blocks: list[int] = field(default_factory=list)

    channels: list[BanchoChannel] = field(default_factory=list)
    watch_party: UserWatchParty | None = None

    in_lobby: bool = False

    is_bot_client: bool = False
    _packet_queue: bytearray = field(default_factory=bytearray)

    @property
    def restricted(self) -> bool:
        return self.privileges & BanchoPrivileges.PLAYER == 0

    @property
    def remaining_silence(self) -> int:
        return max(0, int(self.silence_end - time.time()))

    @property
    def silenced(self) -> bool:
        return self.remaining_silence != 0

    @property
    def current_stats(self) -> UserStatistics:
        return self.stats[self.status.mode]

    def fetch_stats_from_database(self) -> None:
        for mode in OsuMode:
            record = user_stats_db[mode].from_id(self.user_id)

            assert record is not None
            self.stats[mode] = UserStatistics.from_model(record.result)

    async def update_ranks(self) -> None:
        for mode in OsuMode:
            placement = await leaderboards[mode].get_placement(self.user_id)
            if placement is not None:
                self.stats[mode].rank = placement + 1
            else:
                self.stats[mode].rank = 0

    def fetch_friends_and_blocks_from_database(self) -> None:
        friends = user_relationship_db.query(
            lambda x: x.user_id == self.user_id
            and x.relation_type == OsuRelationship.FRIEND
        )

        blocks = user_relationship_db.query(
            lambda x: x.user_id == self.user_id
            and x.relation_type == OsuRelationship.BLOCK
        )

        # Bot is friends with everyone.
        self.friends = [1] + [record.result.friend_id for record in friends]
        self.blocks = [record.result.friend_id for record in blocks]

    def presence_and_stats_packet(self) -> bytes:
        return bancho_user_presence_packet(self) + bancho_user_stats_packet(self)

    def update_user(self) -> None:
        self.latest_activity = int(time.time())

        update_user_in_database(self)

    def enqueue(self, data: bytes) -> None:
        self._packet_queue += data

    def dequeue(self) -> bytearray:
        data = self._packet_queue.copy()
        self._packet_queue.clear()
        return data

    def add_friend(self, friend_id: int) -> None:
        create_user_relationship_in_database(
            self.user_id, friend_id, OsuRelationship.FRIEND
        )

        self.friends.append(friend_id)

    def add_block(self, block_id: int) -> None:
        create_user_relationship_in_database(
            self.user_id, block_id, OsuRelationship.BLOCK
        )

        self.blocks.append(block_id)

    def remove_friend(self, friend_id: int) -> None:
        delete_user_relationship_in_database(
            self.user_id, friend_id, OsuRelationship.FRIEND
        )

        self.friends.remove(friend_id)

    def remove_block(self, block_id: int) -> None:
        delete_user_relationship_in_database(
            self.user_id, block_id, OsuRelationship.FRIEND
        )

        self.blocks.append(block_id)

    def join_channel(self, channel: BanchoChannel) -> bool:
        if (
            self in channel.users
            or not channel.can_read(self.privileges)
            or channel._name == "#lobby"
            and not self.in_lobby
        ):
            return False

        channel.append(self)
        self.channels.append(channel)

        self.enqueue(bancho_channel_join_success_packet(channel))

        channel.send_updates()
        return True

    def leave_channel(self, channel: BanchoChannel, kick: bool = False) -> bool:
        if self not in channel.users:
            return False

        channel.remove(self)
        self.channels.remove(channel)

        if kick:
            self.enqueue(bancho_channel_kick_packet(channel))

        channel.send_updates()
        return True

    def logout(self) -> None:
        token = self.osu_token
        self.osu_token = ""

        # TODO: multiplayer check

        # TODO: spectator check

        while self.channels:
            self.leave_channel(self.channels[0])

        users.pop(token)
        user_id_to_token.pop(self.user_id)

        if not self.restricted:
            broadcast_to_online_users(bancho_logout_packet(self.user_id))

    def send(
        self, message: str, sender: User, channel: BanchoChannel | None = None
    ) -> None:
        if channel is not None:
            recipient = channel.name
        else:
            recipient = self.username

        self.enqueue(
            bancho_send_message_packet(
                sender=sender.username,
                message=message,
                recipient=recipient,
                sender_id=sender.user_id,
            )
        )

    
    def join_watch_party(self, user: User) -> None:
        """Makes the given `user` join this user's watch party."""

        # This has the funny side effect that if you spec someone that is specing someone else, you will join their watch party.
        # Imo that is bing chilling.
        if self.watch_party is None:
            self.watch_party = UserWatchParty(
                the_watched=self,
                the_watchers=[user],
                channel=BanchoChannel(
                    _name=f"#spec_{self.user_id}",
                    topic=f"Watch party for {self.username!r}",
                    write_privileges=BanchoPrivileges.PLAYER,
                    read_privileges=BanchoPrivileges.PLAYER,
                    auto_join=False,
                    temporary=True,
                ),
            )
            self.join_channel(self.watch_party.channel)
            user.join_channel(self.watch_party.channel)
        
        else:
            self.watch_party.the_watchers.append(user)
            user.join_channel(self.watch_party.channel)

        self.watch_party.the_watched.enqueue(
            bancho_join_watch_party(user.user_id)
        )
        self.watch_party.the_watched.enqueue(
            bancho_watch_party_joined_host(user.user_id)
        )


    def leave_watch_party(self, user: User) -> None:
        """Makes the given `user` leave this user's watch party."""

        if self.watch_party is None:
            return

        self.watch_party.the_watchers.remove(user)
        user.leave_channel(self.watch_party.channel)

        self.watch_party.the_watched.enqueue(
            bancho_leave_watch_party(user.user_id)
        )

        if not self.watch_party.the_watchers:
            self.watch_party.the_watched.leave_channel(self.watch_party.channel)
            self.watch_party = None


@dataclass
class BanchoChannel:
    _name: str
    topic: str
    write_privileges: BanchoPrivileges
    read_privileges: BanchoPrivileges
    auto_join: bool

    temporary: bool = False
    users: list[User] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.users)

    @property
    def _fixed_name(self) -> str:
        if self._name.startswith("#"):
            return self._name

        return f"#{self._name}"

    @property
    def name(self) -> str:
        if self._fixed_name.startswith("#spec_"):
            return "#spectator"
        elif self._fixed_name.startswith("#multi_"):
            return "#multiplayer"

        return self._fixed_name

    def can_read(self, privs: BanchoPrivileges) -> bool:
        return privs & self.read_privileges != 0

    def can_write(self, privs: BanchoPrivileges) -> bool:
        return privs & self.write_privileges != 0

    @staticmethod
    def from_model(model: ChannelModel) -> BanchoChannel:
        return BanchoChannel(
            _name=model.name,
            topic=model.topic,
            write_privileges=BanchoPrivileges(model.write_privileges),
            read_privileges=BanchoPrivileges(model.read_privileges),
            auto_join=model.auto_join,
        )

    def append(self, user: User) -> None:
        self.users.append(user)

    def remove(self, user: User) -> None:
        self.users.remove(user)

        if not any(self.users) and self.temporary:
            del channels[self.name]

    def send_updates(self) -> None:
        channel_packet = bancho_channel_info_packet(self)

        if self.temporary:
            self.enqueue(channel_packet)
        else:
            for user in users.values():
                if self.can_read(user.privileges):
                    user.enqueue(channel_packet)

    def enqueue(self, data: bytes, exclude: list[int] = []) -> None:
        for user in self.users:
            if user.user_id not in exclude:
                user.enqueue(data)

    def send(self, message: str, sender: User) -> None:
        for user in filter(lambda x: x != sender, self.users):
            user.send(message, sender, self)


users: dict[str, User] = {}
user_id_to_token: dict[int, str] = {}
username_to_token: dict[str, str] = {}
channels: dict[str, BanchoChannel] = {}


def broadcast_to_online_users(data: bytes, exclude: list[int] = []) -> None:
    for user in users.values():
        if user.user_id not in exclude:
            user.enqueue(data)


def add_user_to_cache(user: User) -> None:
    users[user.osu_token] = user
    user_id_to_token[user.user_id] = user.osu_token
    username_to_token[user.username_safe] = user.osu_token


# Bancho Objects END


# Bancho Bot START


class BanchoBot(User):
    def __init__(self) -> None:
        self.user_id = 1
        self.username = "Męski oszuścik"
        self.username_safe = safe_string(self.username)

        self.email = "bot@osu.com"

        self.osu_token = create_random_string(32)
        self.osu_version = "bot"

        self.utc_offset = 2
        self.pm_private = False
        self.privileges = BanchoPrivileges.PLAYER | BanchoPrivileges.DEVELOPER

        self.geoloc = UserGeolocalisation(
            country_acronym="ro",
            country_code=COUNTRY_CODES["ro"],
            # Pyongyang, North Korea.
            latitude=39.039219,
            longitude=125.762524,
        )

        self.silence_end = 0
        self.login_time = int(time.time())
        self.latest_activity = int(time.time())

        super().__init__(
            user_id=self.user_id,
            username=self.username,
            username_safe=self.username_safe,
            email=self.email,
            osu_token=self.osu_token,
            osu_version=self.osu_version,
            utc_offset=self.utc_offset,
            pm_private=self.pm_private,
            privileges=self.privileges,
            geoloc=self.geoloc,
            silence_end=self.silence_end,
            login_time=self.login_time,
            latest_activity=self.latest_activity,
        )

        self.status = BanchoUserStatus(
            action=BanchoAction.TESTING,
            action_text="users patience.",
        )

        self.is_bot_client = True
        self._commands: dict[str, BotCommand] = {}

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
            level=1,
        )

    def add_command(self, command: BotCommand) -> None:
        self._commands[command.name] = command

        for alias in command.aliases:
            self._commands[alias] = command

    async def handle_commands(
        self, user: User, message: str, in_channel: bool
    ) -> BotCommand | None:
        args = message.strip().split(" ")
        assert any(args), "Empty message."

        command_name = args[0].lower()
        command_cls = self._commands.get(command_name)

        if command_cls is None:
            return None

        resp = await command_cls.execute(user, args[1:], in_channel)
        return resp


bancho_bot = BanchoBot()


class BotCommand:
    def __init__(
        self,
        name: str,
        description: str,
        aliases: list[str] = [],
        priv_req: BanchoPrivileges | None = None,
        allow_dms: bool = True,
        allow_channels: bool = True,
        invisible_response: bool = False,
    ) -> None:
        self.name = name
        self.description = description
        self.aliases = aliases
        self.priv_req = priv_req
        self.allow_dms = allow_dms
        self.allow_channels = allow_channels
        self.invisible_response = invisible_response

        self.response: str | None = None

    def _process_sanity_checks(self, user: User, in_channel: bool) -> bool:
        if not self.allow_dms and not in_channel:
            return False

        if not self.allow_channels and in_channel:
            return False

        if self.priv_req is not None and not user.privileges & self.priv_req:
            return False

        return True

    async def execute(
        self, user: User, args: list[str], in_channel: bool = False
    ) -> BotCommand | None:
        raise NotImplementedError


class PingCommand(BotCommand):
    def __init__(self) -> None:
        super().__init__(
            name="!ping",
            description="Check if the bot is alive.",
            invisible_response=True,
        )

    async def execute(
        self, user: User, args: list[str], in_channel: bool = False
    ) -> BotCommand | None:
        if not self._process_sanity_checks(user, in_channel):
            return None

        self.response = "Pong!"
        return self


bancho_bot.add_command(PingCommand())


# Bancho Bot END


# Bancho HTTP Logic START


bancho_router = Router(
    {
        f"c.{SETTING_MAIN_DOMAIN}",
        f"ce.{SETTING_MAIN_DOMAIN}",
        f"c4.{SETTING_MAIN_DOMAIN}",
        f"c6.{SETTING_MAIN_DOMAIN}",
    }
)


async def bancho_post(request: HTTPRequest) -> None:
    if request.headers["user-agent"] != "osu!":
        await bancho_get(request)
        return

    osu_token = request.headers.get("osu-token")
    if osu_token is None:
        login_response = await bancho_login_handler(request)
        await request.send_response(
            status_code=200,
            headers={"cho-token": login_response["osu_token"]},
            body=login_response["packets"],
        )
        return

    user = users.get(osu_token)
    if user is None:
        await request.send_response(
            status_code=200,
            body=bancho_notification_packet("Server has restarted!")
            + bancho_server_restart_packet(0),
        )
        return

    packets = PacketContext.create_from_buffers(request.body)
    for packet in packets:
        await packets_router.route(packet, user)

    user.update_user()
    response = user.dequeue()

    await request.send_response(
        status_code=200,
        body=response,
    )


class BanchoLoginResponse(TypedDict):
    osu_token: str
    packets: bytes


async def bancho_login_handler(request: HTTPRequest) -> BanchoLoginResponse:
    username, password_hash, additional_data, _ = request.body.decode().split("\n")
    osu_ver, utc_offset, _, _, pm_private = additional_data.split("|")

    geolocalisation = await get_user_geolocalisation(
        request.headers.get("x-forwarded-for")
    )

    packet_response = bytearray()

    user_result = user_db.query_one(lambda x: x.username_safe == safe_string(username))
    if user_result is None:
        just_registered = True
        user_resp = create_user_in_database(
            username=username,
            email=f"changeme_{create_random_string(10)}@lol.xd",
            password_md5=password_hash,
            country_acronym=geolocalisation.country_acronym,
        )

        user_id = user_resp["user_id"]
        user_model = user_resp["user_model"]
        create_user_stats_in_database(user_id)
    else:
        just_registered = False
        user_id = user_result.id
        user_model = user_result.result

    if not check_password(password_hash, user_model.password_md5):
        return {
            "osu_token": "invalid-password",
            "packets": (
                bancho_login_reply_packet(-1)
                + bancho_notification_packet("onecho!: Invalid password.")
            ),
        }

    user = User(
        user_id=user_id,
        username=user_model.username,
        username_safe=user_model.username_safe,
        osu_token=create_random_string(32),
        osu_version=osu_ver,
        email=user_model.email,
        utc_offset=int(utc_offset),
        pm_private=bool(int(pm_private)),
        privileges=BanchoPrivileges(user_model.privileges),
        geoloc=geolocalisation,
        silence_end=user_model.silence_end,
        login_time=int(time.time()),
        latest_activity=int(time.time()),
    )
    user.fetch_stats_from_database()
    user.fetch_friends_and_blocks_from_database()

    if just_registered:
        for mode in OsuMode:
            await leaderboards[mode].add_entry(
                user_id=user.user_id,
                score=0,
            )

    await user.update_ranks()

    packet_response += bancho_login_reply_packet(user.user_id)
    packet_response += bancho_protocol_packet()

    for channel in channels.values():
        if (
            not channel.auto_join
            or not channel.can_read(user.privileges)
            or channel._fixed_name == "#lobby"
        ):
            continue

        chan_packet = bancho_channel_info_packet(channel)
        packet_response += chan_packet

        for u in users.values():
            if channel.can_read(u.privileges):
                u.enqueue(chan_packet)

    packet_response += bancho_channel_info_end_packet()
    packet_response += bancho_silence_end_packet(user.silence_end)
    packet_response += bancho_login_perms_packet(user.privileges)

    for online_user in users.values():
        if online_user.restricted:
            continue

        packet_response += online_user.presence_and_stats_packet()

    packet_response += user.presence_and_stats_packet()
    packet_response += bancho_user_friends_packet(user.friends)

    quote = random.choice(QUOTES)
    packet_response += bancho_notification_packet(f"onecho! - {quote}")

    if not user.restricted:
        broadcast_to_online_users(user.presence_and_stats_packet())

    add_user_to_cache(user)

    user.update_user()
    return {
        "osu_token": user.osu_token,
        "packets": packet_response,
    }


QUOTES = [
    "Commit your RealistikPanel changes.",
    "Den Bensch.",
    "I'm a bot, I don't have feelings. - GitHub Copilot",
    "Męski oszuścik is gonna get you.",
    "The sigma is crying.",
    "Kill yourself",
    "KYS - Kuopion yliopistollinen sairaala",
    "'shoot yourself' - 'i mean shoot your shot",
    "ZE CO DO CHUJA?",
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
    quote = random.choice(QUOTES)
    gif = random.choice(GIFS)

    html_response = f"""
    <center style='font-family: "Comic Sans MS", "Comic Sans", cursive;'>
        <h1>onecho!</h1> <h2>{quote}</h2> <br> <img src='{gif}'>
    </center>
    """

    await request.send_response(
        status_code=200,
        body=html_response.encode("utf-8"),
        headers={
            "Content-Type": "text/html; charset=utf-8",
        },
    )


@bancho_router.add_endpoint("/", methods=["GET", "POST"])
async def bancho_root_handler(request: HTTPRequest) -> None:
    match request.method:
        case "GET":
            await bancho_get(request)
        case "POST":
            await bancho_post(request)
        case _:
            raise ValueError("Not allowed method.")


# Bancho HTTP Logic END


# Avatar Domain START


avatar_router = Router(f"a.{SETTING_MAIN_DOMAIN}")

DEFAULT_AVATAR_LIST = glob.glob("avatars/default/*.png") + glob.glob("avatars/default/*.jpg")

def hash_string_as_integer(string: str) -> int:
    return int(hashlib.sha256((string).encode()).hexdigest(), 16)

def get_random_avatar(user_id: int | str) -> str:
    user_hash = hash_string_as_integer(str(user_id))
    hashed_filenames = {hash_string_as_integer(filename): filename for filename in DEFAULT_AVATAR_LIST}
    
    # Sort the hashed filenames and find the closest hash to the user_hash
    sorted_hashes = sorted(hashed_filenames.keys())
    closest_hash = next(filter(lambda x: user_hash <= x, sorted_hashes), sorted_hashes[0])
    return hashed_filenames[closest_hash]


def get_avatar_data(user_id: int) -> bytes:
    if os.path.exists(f"avatars/{user_id}.png"):
        path = f"avatars/{user_id}.png"
    elif os.path.exists(f"avatars/{user_id}.jpg"):
        path = f"avatars/{user_id}.jpg"
    else:
        path = get_random_avatar(user_id)

    with open(path, "rb") as f:
        return f.read()


@avatar_router.add_endpoint("/{}", methods=["GET"])
async def avatar_handler(request: HTTPRequest) -> None:
    user_id = request.path.split("/")[-1]
    if not user_id.isdigit():
        path = get_random_avatar(user_id)
        with open(path, "rb") as f:
            avatar_data = f.read()
        await request.send_response(
            status_code=200,
            body=avatar_data,
            headers={
                "Content-Type": "image/png",
            },
        )
        return

    avatar_data = get_avatar_data(int(user_id))

    await request.send_response(
        status_code=200,
        body=avatar_data,
        headers={
            "Content-Type": "image/png",
        },
    )


# Avatar Domain END


# Server Entry Point START


DEFAULT_CHANNELS = [
    ChannelModel(
        name="osu",
        topic="Welcome to onecho!",
        write_privileges=BanchoPrivileges.PLAYER.value,
        read_privileges=BanchoPrivileges.PLAYER.value,
        auto_join=True,
    ),
    ChannelModel(
        name="lobby",
        topic="Lobby discussion channel.",
        write_privileges=BanchoPrivileges.PLAYER.value,
        read_privileges=BanchoPrivileges.PLAYER.value,
        auto_join=False,
    ),
    ChannelModel(
        name="polish",
        topic="POLISH MOUNTAIN JEBAC KURWY",
        write_privileges=BanchoPrivileges.PLAYER.value,
        read_privileges=BanchoPrivileges.PLAYER.value,
        auto_join=False,
    ),
]


async def main() -> int:
    info(
        "onecho - The osu private server that is not a private server, but a public server."
    ) # Written by Copilot
    # Initialise bot
    add_user_to_cache(bancho_bot)

    # Initialise leaderboards
    for mode in OsuMode:
        records = user_stats_db[mode].all()
        for record in records:
            await leaderboards[mode].add_entry(
                user_id=record.result.user_id,
                score=record.result.pp,
            )

    # Initialise channels
    if not len(channel_db):
        for channel in DEFAULT_CHANNELS:
            channel_db.insert(channel)

    for channel in channel_db.all():
        # hashtag is reserved for removed databases entries so we have to improvise
        channels[f"#{channel.result.name}"] = BanchoChannel.from_model(channel.result)

    # Initialise server
    server = AsyncHTTPServer(address=SETTING_HTTP_HOST, port=SETTING_HTTP_PORT)
    server.add_router(bancho_router)
    server.add_router(avatar_router)

    await server.start_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))


# Server Entry Point END
