# onecho
# The single-file, dependency-less osu! server implementation.
# Made by:
# - RealistikDash
# - Lenfouriee

from typing import (
    Any,
    Optional,
    Union,
    Callable,
)
import json
import os
import time
import sys

# Config Globals
DEBUG = "debug" in sys.argv

# Logger
class Ansi:
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

def colour_into_console(col: Ansi) -> str:
    return f"\x1b[{col}m"

def _log(content: str, action: str, colour: Ansi = Ansi.WHITE):
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    colour = colour_into_console(colour)
    sys.stdout.write( # This is mess but it forms in really cool log.
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

    __slots__ = ( # speed go brrrrrrr
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

        self._autoincr = 1 # The next available ID.

        self.try_load()
    
    def add_new_index(self, field_name: JsonIndexes) -> None:
        """Populates _index with boilerplate data for index."""

        self._index[field_name] = {}
    
    def init_new_indexes(self) -> None:
        """Adds boilerplate for a new index list. Assumes no data present."""

        assert not self._data, "New indexes may only be initialised if no data is present"

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
            info(f"A database does not exist for {self._directory}. Starting from scratch.")
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
    
    def query(self, lam: Callable[[JsonLike], bool]) -> list[JsonLike]:
        """Iterates over entire db, returning results that match the lambda.
        Does not use indexes.
        """

        return [
            obj for obj in self._data.values()
            if lam(obj)
        ]
    
    def fetch_eq(self, field: JsonIndexes, value: JsonTypes) -> list[JsonLike]:
        """Fetches all results where `field` == `value`. Uses indexes when
        possible. Else is a wrapper around `query`."""

        if field in self._index_fields:
            debug("Fetching using index.")
            val_rows = self._index[field].get(value)

            if not val_rows:
                return []
            return [
                self._data[row_id]
                for row_id in val_rows
            ]
        else:
            debug("Fetching using query.")
            return self.query(
                lambda x: x[field] == value
            )

    def query_limit(self, lam: Callable[[JsonLike], bool], limit: int) -> list[JsonLike]:
        """Like `JSONDatabase.query` but allows you to specify a limit for
        the amount of results."""

        am = 0 # So we dont have to compute len(res)
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

# HTTP Server END
