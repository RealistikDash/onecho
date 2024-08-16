# onecho
A single-file, dependency-less osu! server implementation.

## Rules
This project follows four core rules:
- All code must be in a single Python file.
- No modules may be used outside of the Python standard library (meaning many things must be implemented by us)
- No `re` (regex) library allowed to make the game funnier.
- Haveing fun.

## Progress
Current project progress.

Logger:
- [x] Coloured logging
- [x] Logging of INFO, WARNING, ERROR.
- [x] Optional debug logging

Database:
- [x] Database object which supports adding dicts and lambda searching
- [ ] Support removing rows.
- [x] Database loading from JSON
- [x] Database saving into JSON
- [x] Database Indexes
- [ ] Database Ordering

HTTP:
- [x] Async HTTP Server
- [x] Host based domain routing
- [ ] Async HTTP Client

Packets:
- [ ] Binary Writer
- [ ] Binary Reader
- [ ] Builder API for writer
- [ ] Packet registration router
- [ ] Packet registration decorator

Bancho:
- [ ] User Login
- [ ] User Actions
- [ ] Private Chat
- [ ] Public Chat
- [ ] Spectator
- [ ] Channel
