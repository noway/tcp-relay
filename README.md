# TCP relay

Relays to different ports based on the behaviour of protocol. 

Asyncio - 0/10, can't even switch between async and object style without monkey-patching. 

py3k

## Usage

```bash
$ nc -klp 8001
$ nc -klp 8002
$ ./tcp_relay
$ nc localhost 8000
```

```
     _
8001  \
       ? <-> tcp_relay <-> 8000
8002 _/

```