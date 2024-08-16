# onecho
# The single-file, dependency-less osu! server implementation.
# Made by:
# - RealistikDash
# - Lenfouriee
from __future__ import annotations

import asyncio
import http
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
STATUS_CODE = {c.value: c.phrase for c in http.HTTPStatus}


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
    ["username", "action_id"],
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


async def main() -> int:
    server = AsyncHTTPServer(address="127.0.0.1", port=2137)
    router = Router("127.0.0.1:2137")

    @router.add_endpoint("/")
    async def index(request: HTTPRequest) -> None:
        await request.send_response(
            status_code=200,
            body=b"Hello, world!",
        )

    server.add_router(router)

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
