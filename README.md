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
- [x] Structured Logging
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
- [x] Server Bot
- [x] Lobby
- [x] User Relationships
- [x] Private Chat
- [x] Public Chat
- [x] Spectator
- [ ] Match
- [x] Channel

Avatar:
- [x] Avatar serving

Commands
- [x] Command framework for chat commands
- [ ] Roulette
- [ ] Blackjack
- [ ] (OPTIONAL) Use NP to calculate the PP of the current map
- [ ] Slots
