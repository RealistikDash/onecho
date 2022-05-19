# onecho
A single-file, dependency-less osu! server implementation.

## Rules
This project follows three core rules:
- All code must be in a single Python file.
- No modules may be used outside of the Python standard library (meaning many things must be implemented by us)
- Haveing fun.

## Progress
Current project progress.

Database:
- [ ] Database object which supports adding dicts and lambda searching
- [ ] Database loading from JSON
- [ ] Database saving into JSON
- [ ] Database Indexes
- [ ] Database Ordering

HTTP:
- [ ] Async HTTP Server
- [ ] Host based domain routing
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
