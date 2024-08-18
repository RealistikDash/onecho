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
from typing import (
    Any,
    Iterator,
    TypeVar,
    Union,
    Callable,
    Awaitable,
)
from enum import IntEnum

import urllib.parse
import json
import os
import time
import sys
import socket

# Config Globals
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


# Logger
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

# Database
JsonTypes = Union[str, int, dict]
JsonIndexes = Union[str, int]
JsonLike = Union[dict[JsonIndexes, JsonTypes], list[JsonTypes]]


class JSONDatabase:
    """A searchable collection of JSON objects."""

    __slots__ = (  # speed go brrrrrrr
        "_directory",
        "_data",
        "_index",
        "_autoincr",
        "_index_fields",
    )

    def __init__(
        self,
        indexed_fileds: list[JsonIndexes],
        directory: str,
    ) -> None:
        self._directory = directory
        # Autoincremented
        self._data: dict[int, JsonLike] = {}
        # How indexes work:
        # Store a dict key entry of the indexed field
        # Have that dict be indexed by possible values
        # To those values is attached a list of all field IDs for that value.
        ## ONLY WORKS FOR EXACT SEARCHES.
        self._index: dict[JsonIndexes, dict[JsonTypes, list[int]]] = {}
        self._index_fields: list[JsonIndexes] = indexed_fileds

        self._autoincr = 1  # The next available ID.

        self.try_load()

    def add_new_index(self, field_name: JsonIndexes) -> None:
        """Populates _index with boilerplate data for index."""

        self._index[field_name] = {}

    def init_new_indexes(self) -> None:
        """Adds boilerplate for a new index list. Assumes no data present."""

        assert (
            not self._data
        ), "New indexes may only be initialised if no data is present"

        for idx in self._index_fields:
            self.add_new_index(idx)

    def acquire_id(self) -> int:
        """Gets the next autoincr id and incr."""

        aincr = self._autoincr
        self._autoincr += 1
        return aincr

    def try_load(self) -> bool:
        """Tries to load the database."""

        if not os.path.exists(self._directory):
            info(
                f"A database does not exist for {self._directory}. Starting from scratch."
            )
            self.init_new_indexes()
            return False

        self.load()
        info(f"Loaded database from {self._directory}!")
        return True

    def load(self) -> None:
        """Loads data from self._directory."""

        with open(self._directory, "r") as f:
            read_db = json.load(f)

        self._data = {int(index): value for index, value in read_db["data"].items()}
        self._index = read_db["index"]
        self._autoincr = read_db["autoincr"]
        self._index_fields = read_db["index_fields"]

    def into_dict(self) -> dict:
        return {
            "data": self._data,
            "index": self._index,
            "autoincr": self._autoincr,
            "index_fields": self._index_fields,
        }

    def save(self) -> None:
        """Saves the file to directory."""

        with open(self._directory, "w") as f:
            json.dump(
                self.into_dict(),
                f,
            )

        info(f"Saved database info {self._directory}")

    def add_index_id(self, idx: JsonIndexes, value: JsonTypes, obj_id: int):
        idx_val = self._index[idx]

        value_idx = idx_val.get(value)
        if value_idx is None:
            idx_val[value] = value_idx = []

        value_idx.append(obj_id)

        debug(f"Indexed row id {obj_id}'s field {idx} for value {value}")

    def insert(self, obj: JsonLike) -> int:
        """Inserts an object into the db. Returns object id."""

        # Acquire the id.
        obj_id = self.acquire_id()

        # Insert into db.
        self._data[obj_id] = obj
        debug(f"Inserted object into ID {obj_id}")

        # Handle indexes.
        for idx in self._index_fields:
            if res := obj.get(idx):
                self.add_index_id(
                    idx,
                    res,
                    obj_id,
                )

        return obj_id

    def query(self, lam: Callable[[JsonLike], bool]) -> list[JsonLike]:
        """Iterates over entire db, returning results that match the lambda.
        Does not use indexes.
        """

        return [obj for obj in self._data.values() if lam(obj)]

    def fetch_eq(self, field: JsonIndexes, value: JsonTypes) -> list[JsonLike]:
        """Fetches all results where `field` == `value`. Uses indexes when
        possible. Else is a wrapper around `query`."""

        if field in self._index_fields:
            debug("Fetching using index.")
            val_rows = self._index[field].get(value)

            if not val_rows:
                return []
            return [self._data[row_id] for row_id in val_rows]
        else:
            debug("Fetching using query.")
            return self.query(lambda x: x[field] == value)

    def query_limit(
        self, lam: Callable[[JsonLike], bool], limit: int
    ) -> list[JsonLike]:
        """Like `JSONDatabase.query` but allows you to specify a limit for
        the amount of results."""

        am = 0  # So we dont have to compute len(res)
        res = []

        for row in self._data.values():
            if lam(row):
                res.append(row)
                am += 1

            if am >= limit:
                break

        return res


# Database END
# Shared state

user_db = JSONDatabase(
    ["username"],
    "user_db.json",
)

# Shared state END

# HTTP Server

T = TypeVar("T")


class CaseInsensitiveDict[T]:
    def __init__(self) -> None:
        self._dict: dict[str, T] = {}

    def __repr__(self) -> str:
        return f"<CaseInsensitiveDict {self._dict!r}>"

    def __setitem__(self, key: str, val: Any) -> None:
        self._dict[key.lower()] = val

    def __getitem__(self, key: str) -> T:
        return self._dict[key.lower()]

    def __delitem__(self, key: str) -> None:
        del self._dict[key.lower()]

    def __iter__(self) -> Iterator[str]:
        for k in self._dict:
            yield k

    def __not__(self) -> bool:
        return not self._dict

    def __concat__(self, d: dict | CaseInsensitiveDict) -> None:
        self.__conv_dict(d)

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._dict

    def __conv_dict(self, d: dict | CaseInsensitiveDict) -> None:
        for k, v in d.items():
            if k.__class__ is str:
                k = k.lower()
            self._dict[k] = v

    def items(self):
        return self._dict.items()

    def keys(self) -> tuple:
        return tuple(self._dict.keys())

    def get(self, key: str, default: T) -> T:
        return self._dict.get(key.lower(), default)


class HTTPRequest:
    def __init__(self, client: socket.socket, server: AsyncHTTPServer) -> None:
        self._client = client
        self._server = server

        self.method: str
        self.path: str
        self.version: str
        self.body: bytes

        self.headers: CaseInsensitiveDict[str] = CaseInsensitiveDict()
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

    async def parse_request(self) -> None:
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


HTTP_HANDLER = Callable[[HTTPRequest], Awaitable[None]]


class Endpoint:
    def __init__(
        self, path: str, handler: HTTP_HANDLER, methods: list[str] = ["GET"]
    ) -> None:
        self.path = path
        self.handler = handler
        self.methods = methods

    def match(self, path: str) -> bool:
        return self.path == path


class Router:
    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.endpoints: set[Endpoint] = set()

    def match(self, path: str) -> bool:
        return self.domain == path

    def find_endpoint(self, path: str) -> Endpoint | None:
        for endpoint in self.endpoints:
            if endpoint.match(path):
                return endpoint

        return None

    def add_endpoint(self, path: str, methods: list[str] = ["GET"]) -> Callable:
        def decorator(handler: HTTP_HANDLER) -> HTTP_HANDLER:
            self.endpoints.add(Endpoint(path, handler, methods))
            return handler

        return decorator


class AsyncHTTPServer:
    def __init__(self, *, address: str, port: int) -> None:
        self.address = address
        self.port = port

        self.on_start_server_coroutine: Callable[..., Awaitable[None]] | None = None
        self.on_close_server_coroutine: Callable[..., Awaitable[None]] | None = None

        self.before_request_coroutines: list[HTTP_HANDLER] = []
        self.after_request_coroutines: list[HTTP_HANDLER] = []

        self.routes: set[Router] = set()

        # statistics!
        self.requests_served = 0

    def on_start_server(self, coro: Callable[..., Awaitable[None]]) -> None:
        self.on_start_server_coroutine = coro

    def on_close_server(self, coro: Callable[..., Awaitable[None]]) -> None:
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
            await response_500(request)

    async def _handle_request(self, client: socket.socket) -> None:
        request = HTTPRequest(client, self)
        await request.parse_request()

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

            info(f"Server started on {self.address}:{self.port}")

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

# HTTP Responses


async def response_404(request: HTTPRequest) -> None:
    await request.send_response(
        status_code=404,
        body=b"Not Found",
    )


async def response_405(request: HTTPRequest) -> None:
    await request.send_response(
        status_code=405,
        body=b"Method Not Allowed",
    )


async def response_500(request: HTTPRequest) -> None:
    tb = traceback.format_exc()

    await request.send_response(
        status_code=500,
        body=f"Whoops! Fuck python!\n\n{tb}".encode(),
    )


# HTTP Responses END

# String Helpers


def safe_string(s: str) -> str:
    return s.lower().strip().replace(" ", "_")

def create_random_string(n: int) -> str:
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])


# String Helpers END

# Bancho custom country enums

COUNTRY_DICT = {
    "IO": 104,
    "PS": 178,
    "LV": 132,
    "GI": 82,
    "MZ": 154,
    "BZ": 37,
    "TR": 217,
    "CV": 52,
    "BI": 26,
    "CM": 47,
    "JM": 109,
    "GU": 91,
    "CY": 54,
    "BW": 35,
    "KW": 120,
    "MY": 153,
    "SH": 193,
    "PG": 171,
    "PW": 180,
    "FM": 72,
    "HR": 97,
    "YT": 238,
    "JO": 110,
    "HK": 94,
    "MW": 151,
    "AZ": 18,
    "IQ": 105,
    "DO": 60,
    "RS": 239,
    "PK": 173,
    "BR": 31,
    "SN": 199,
    "LI": 126,
    "CD": 40,
    "MG": 137,
    "PE": 169,
    "CK": 45,
    "SJ": 195,
    "SZ": 205,
    "PM": 175,
    "LY": 133,
    "BV": 34,
    "KN": 117,
    "GR": 88,
    "CC": 39,
    "IN": 103,
    "DZ": 61,
    "SK": 196,
    "VC": 229,
    "GW": 92,
    "BQ": 0,
    "UM": 224,
    "AF": 5,
    "TZ": 221,
    "AO": 11,
    "AW": 17,
    "AE": 0,
    "PF": 170,
    "MK": 139,
    "AR": 13,
    "AQ": 12,
    "SL": 197,
    "HT": 98,
    "NF": 158,
    "SS": 190,
    "MU": 149,
    "VA": 228,
    "EC": 62,
    "LC": 125,
    "MX": 152,
    "CW": 0,
    "LT": 130,
    "GN": 85,
    "ZM": 241,
    "LU": 131,
    "NG": 159,
    "MS": 147,
    "MV": 150,
    "DJ": 57,
    "MQ": 145,
    "IE": 101,
    "CG": 40,
    "LK": 127,
    "NZ": 166,
    "KR": 119,
    "RO": 184,
    "KE": 112,
    "MF": 252,
    "SR": 201,
    "PA": 168,
    "KI": 115,
    "NL": 161,
    "DM": 59,
    "TC": 206,
    "KZ": 122,
    "CR": 50,
    "NR": 164,
    "UZ": 227,
    "GE": 79,
    "KP": 118,
    "PN": 176,
    "BY": 36,
    "NI": 160,
    "IR": 106,
    "VI": 232,
    "MA": 134,
    "NO": 162,
    "PT": 179,
    "PY": 181,
    "CU": 51,
    "SC": 189,
    "TT": 218,
    "CA": 38,
    "IT": 108,
    "GF": 80,
    "CN": 48,
    "GQ": 87,
    "LR": 128,
    "BA": 19,
    "TD": 207,
    "AU": 16,
    "MM": 141,
    "HU": 99,
    "EG": 64,
    "JE": 250,
    "IL": 102,
    "BL": 251,
    "BS": 32,
    "SE": 191,
    "MC": 135,
    "SD": 190,
    "ZA": 240,
    "IM": 249,
    "MO": 143,
    "GL": 83,
    "TV": 219,
    "FK": 71,
    "GB": 77,
    "NA": 155,
    "AM": 9,
    "WS": 236,
    "UY": 226,
    "EE": 63,
    "TL": 216,
    "BT": 33,
    "VU": 234,
    "WF": 235,
    "AX": 247,
    "TK": 212,
    "MN": 142,
    "SB": 188,
    "XK": 0,
    "BH": 25,
    "ID": 100,
    "SV": 203,
    "TG": 209,
    "BF": 23,
    "GG": 248,
    "IS": 107,
    "FJ": 70,
    "KG": 113,
    "BD": 21,
    "ZW": 243,
    "AI": 7,
    "NP": 163,
    "KH": 114,
    "BJ": 27,
    "EH": 65,
    "BE": 22,
    "SM": 198,
    "CX": 53,
    "TW": 220,
    "KM": 116,
    "AS": 14,
    "AT": 15,
    "LA": 123,
    "US": 225,
    "SY": 204,
    "SO": 200,
    "AD": 3,
    "OM": 167,
    "GT": 90,
    "CF": 41,
    "GY": 93,
    "VN": 233,
    "VE": 230,
    "PH": 172,
    "TM": 213,
    "VG": 231,
    "GP": 86,
    "CZ": 55,
    "GM": 84,
    "MR": 146,
    "TN": 214,
    "SI": 194,
    "TO": 215,
    "UG": 223,
    "SA": 187,
    "ST": 202,
    "QA": 182,
    "FI": 69,
    "CO": 49,
    "AG": 6,
    "PR": 177,
    "PL": 174,
    "GH": 81,
    "GA": 76,
    "TJ": 211,
    "SX": 0,
    "KY": 121,
    "BO": 30,
    "UA": 222,
    "MP": 144,
    "TF": 208,
    "LB": 124,
    "MT": 148,
    "FR": 74,
    "JP": 111,
    "RU": 185,
    "RW": 186,
    "NC": 156,
    "NE": 157,
    "BN": 29,
    "CI": 44,
    "TH": 210,
    "DE": 56,
    "ET": 68,
    "FO": 73,
    "YE": 237,
    "DK": 58,
    "BG": 24,
    "GS": 89,
    "HM": 95,
    "BB": 20,
    "BM": 28,
    "ML": 140,
    "SG": 192,
    "GD": 78,
    "NU": 165,
    "RE": 183,
    "LS": 129,
    "ER": 66,
    "ME": 242,
    "HN": 96,
    "AL": 8,
    "CH": 43,
    "MD": 136,
    "ES": 67,
    "CL": 46,
    "MH": 138,
}

# Bancho custom country enums END


# Bancho Packets
class PacketID(IntEnum):
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


class BinaryReader:
    def __init__(self, bytes_data: bytearray) -> None:
        self.__buffer = bytes_data
        self.__offset = 0

    def __len__(self) -> int:
        return len(self.__buffer)

    def read(self, offset: int = -1) -> bytes:
        if offset < 0:
            offset = len(self.__buffer) - self.__offset

        data = self.__buffer[self.__offset : self.__offset + offset]
        self.__offset += offset
        return data

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
    def __init__(self, packet_id: PacketID) -> None:
        self.packet_id = packet_id
        super().__init__()

    def finish(self) -> bytearray:
        packet_bytes = bytearray()

        packet_bytes += struct.pack("<h", self.packet_id)
        packet_bytes += b"\x00"
        packet_bytes += struct.pack("<l", len(self.buffer))
        packet_bytes += self.buffer

        return packet_bytes


def bancho_notification_packet(message: str) -> bytes:
    packet = PacketBuilder(PacketID.SRV_NOTIFICATION)
    packet.write_string(message)
    return packet.finish()


def bancho_login_reply_packet(user_id: int) -> bytes:
    packet = PacketBuilder(PacketID.SRV_LOGIN_REPLY)
    packet.write_i32(user_id)
    return packet.finish()


def bancho_protocol_packet() -> bytes:
    packet = PacketBuilder(PacketID.SRV_PROTOCOL_VERSION)
    packet.write_i32(19)
    return packet.finish()


def bancho_channel_info_end_packet() -> bytes:
    packet = PacketBuilder(PacketID.SRV_CHANNEL_INFO_END)
    packet.write_u32(0)
    return packet.finish()


def bancho_silence_end_packet(silence_end: int) -> bytes:
    packet = PacketBuilder(PacketID.SRV_SILENCE_END)
    packet.write_u32(silence_end)
    return packet.finish()


def bancho_login_perms_packet(privileges: int) -> bytes:
    packet = PacketBuilder(PacketID.SRV_PRIVILEGES)
    packet.write_u32(privileges)
    return packet.finish()


def bancho_user_presence_packet(
    user_id: int,
    username: str,
    timezone_offset: int,
    country_enum: int,
    privileges: int,
    longitude: float,
    latitude: float,
    rank: int,
) -> bytes:
    packet = PacketBuilder(PacketID.SRV_USER_PRESENCE)
    packet.write_i32(user_id)
    packet.write_string(username)
    packet.write_u8(timezone_offset + 24)
    packet.write_u8(country_enum)
    packet.write_u8(privileges)
    packet.write_f32(longitude)
    packet.write_f32(latitude)
    packet.write_i32(rank)
    return packet.finish()


def bancho_user_stats_packet(
    user_id: int,
    action_id: int,
    action_text: str,
    action_md5: str,
    action_mods: int,
    mode: int,
    action_map_id: int,
    ranked_score: int,
    accuracy: float,
    playcount: int,
    total_score: int,
    rank: int,
    pp: int,
) -> bytes:
    packet = PacketBuilder(PacketID.SRV_USER_STATS)
    packet.write_i32(user_id)
    packet.write_u8(action_id)
    packet.write_string(action_text)
    packet.write_string(action_md5)
    packet.write_i32(action_mods)
    packet.write_u8(mode)
    packet.write_i32(action_map_id)
    packet.write_i64(ranked_score)
    packet.write_f32(accuracy / 100)
    packet.write_i32(playcount)
    packet.write_i64(total_score)
    packet.write_i32(rank)
    packet.write_i32(pp)
    return packet.finish()


# Bancho Packets END

# Bancho HTTP Logic

bancho_router = Router("c.akatsuki.gg")  # funny meme
USERS = {}


async def bancho_get(request: HTTPRequest) -> None:
    await request.send_response(
        status_code=200,
        body=b"onecho! - because it's that simple!",
    )


async def bancho_post(request: HTTPRequest) -> None:
    if request.headers["user-agent"] != "osu!":
        await bancho_get(request)
        return

    osu_token = request.headers.get("osu-token", "")
    if not osu_token:
        uuid, packets = await bancho_login_handler(request)
        await request.send_response(
            status_code=200,
            headers={"cho-token": uuid},
            body=packets,
        )
        return


async def bancho_login_handler(request: HTTPRequest) -> tuple[str, bytes]:
    username, password_hash, additional_data, _ = request.body.decode().split("\n")
    username_safe = safe_string(username)

    osu_ver, timezone, _, client_hashes, allow_pms = additional_data.split("|")
    # osu_hash, _, adapter_md5, osu_uninst, serial_md5, _ = client_hashes.split(":")

    # Ok so for now we are doing database-less login.
    packet_response = bytearray()
    user_id = len(USERS) + 1
    packet_response += bancho_login_reply_packet(user_id)
    packet_response += bancho_protocol_packet()
    packet_response += bancho_channel_info_end_packet()
    packet_response += bancho_silence_end_packet(0)
    packet_response += bancho_login_perms_packet(5)  # player + supporter

    # TODO: clean it LOL
    user_rank = random.randint(1, 100)  # equal chances!
    packet_response += bancho_user_presence_packet(
        user_id,
        username,
        int(timezone),
        COUNTRY_DICT["RO"],
        5,  # player + supporter
        39.01955903386848,
        125.75276158057767,
        user_rank,
    )
    packet_response += bancho_user_stats_packet(
        user_id, 0, "", "", 0, 0, 0, 0, 100.0, 0, 0, user_rank, 69
    )
    packet_response += bancho_notification_packet("onecho! - because it's that simple!")

    uuid = create_random_string(32)
    USERS[uuid] = user_id

    return uuid, packet_response


@bancho_router.add_endpoint("/", methods=["GET", "POST"])
async def bancho_root_handler(request: HTTPRequest) -> None:
    if request.method == "GET":
        await bancho_get(request)
        return

    await bancho_post(request)


# Bancho HTTP Logic END

# Server Entry Point


async def main() -> int:
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
