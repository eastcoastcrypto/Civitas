# Linearize
Construct a linear, no-fork, best version of the Civitas blockchain. The scripts
run using Python 3 but are compatible with Python 2.

## Step 0: Install Civitas

https://github.com/eastcoastcrypto/Civitas

The `linearize-hashes` and `linearize-allrpc` scripts requires a connection, local or remote, to a
JSON-RPC server. Running `civitasd` or `civitas-qt -server` will be sufficient.

## Step 1: Download hash list

    $ ./linearize-hashes.py linearize.cfg > hashlist.txt

Required configuration file settings for linearize-hashes:
* RPC: `rpcuser`, `rpcpassword`

Optional config file setting for linearize-hashes:
* RPC: `host`  (Default: `127.0.0.1`)
* RPC: `port`  (Default: `28843`)
* Blockchain: `min_height`, `max_height`
* `rev_hash_bytes`: If true, the written block hash list will be
byte-reversed. (In other words, the hash returned by getblockhash will have its
bytes reversed.) False by default. Intended for generation of
standalone hash lists but safe to use with linearize-allrpc.py, which will output
the same data no matter which byte format is chosen.

## Step 2: Copy local block data

    $ ./linearize-allrpc.py linearize.cfg

Required configuration file settings:
* `output_file`: The file that will contain the final blockchain.

Optional config file setting for linearize-allrpc:
* `debug_output`: Some printouts may not always be desired. If true, such output
will be printed.
* `hashlist`: text file containing list of block hashes created by
linearize-hashes.py.
* `netmagic`: Network magic number. (default is '63434956', mainnet)
* `rev_hash_bytes`: If true, the block hash list written by linearize-hashes.py
will be byte-reversed when read by linearize-allrpc.py. See the linearize-hashes
entry for more information.
