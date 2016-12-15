# In-memory storage with TTL in python

Simple storage with TTL. It implements disctionary API. Can be used for testing puproses or PoC

## Usage
`Storage(ttl=60, cleanup_interval=120, purge_callback=lambda dict_of_expired: do_anything(dict_of_expired))`
