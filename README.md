# onecho
A single-file, dependency-less osu! server stack implementation.

## Rules
This project follows four core rules:
- All code must be in a single Python file.
- No modules may be used outside of the Python standard library (meaning many things must be implemented by us)
- No `re` (regex) or `sqlite3` library allowed to make the game funnier.
- Haveing fun.

## Progress
Current project progress.

Logger:
- [x] Coloured logging
- [x] Logging of INFO, WARNING, ERROR.
- [x] Optional debug logging

Database:
- [x] Read and write CSV format.
- [x] Support for multiple tables.
- [x] Object serialisation.
- [x] Automatic synchroniation

HTTP:
- [x] Async HTTP Server
- [x] Host based domain routing
- [x] Async HTTP Client

Packets:
- [x] Binary Writer
- [x] Binary Reader
- [x] Builder API for writer
- [x] Packet registration router
- [x] Packet registration decorator

Bancho:
- [x] User Login
- [x] User Logout
- [x] User Actions
- [ ] Server Bot
- [ ] Lobby
- [ ] User Relationships
- [ ] Private Chat
- [ ] Public Chat
- [ ] Spectator
- [ ] Match
- [x] Channel

Avatar:
- [x] Avatar serving
