# TCP relay

Relays to different ports based on the behaviour of protocol. 

Asyncio - 0/10, can't even switch between async and object style without monkey-patching. 

py3k

## Usage

```bash
$ nc -klp 8001
$ nc -klp 8002
$ ./tcp_relay --match 127.0.0.1:8001 --other 127.0.0.1:8002 --pattern 0x535348
$ nc localhost 8000
```

```
     _
8001  \
       ? <-> tcp_relay <-> 8000
8002 _/

```

## What is it again?

An implementation of `rinetd` with the ability to have multiple rules for the same port based on the content of protocol

