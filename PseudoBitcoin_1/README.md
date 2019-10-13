## Prerequisites
- python 3.x
- python module:
    - time
    - hashlib
    - json
    

## How to use my pseudo bitcoin
- create a blockchainwith a coinbaseTX ( reward to { ADDRESS } ) inside the genesis block.
    ```
    python PseudoBitcoin.py createblockchain –address { ADDRESS }
    ```
- get balance of { ADDRESS }
    ```
    python PseudoBitcoin.py getbalance -address { ADDRESS }
    ```
- Append new block containing one UTXO transaction inside
    ```
    python PseudoBitcoin.py send –from { ADDR_1 } –to { ADDR_2 } –amount { AMOUNT }
    ```
- print the whole blockchain
    ```
    python PseudoBitcoin.py printchain
    ```
- print the block [ height ] in the blockchain <br>
( Notice that height starts from 0 )
    ```
    python PseudoBitcoin.py printblock -height { HEIGHT }
    ```
- clear the database
    ```
    python PseudoBitcoin.py clear
    ```
## The functionalities I've implemented

- Prototype
    - [x] Block 
    - [x] Blockchain
    - [x] Proof of Work
- Persistence
    - [x] Database
    - [x] Client
- Transaction (basic)
    - [x] UTXO
    - [ ] Account model
- Address
    - [ ] Sign & Verify
- Transaction (advanced)
    - [ ] Mining reward
    - [ ] Merkletree
- Network
    - [ ] P2P
    - [ ] Server-Client
- Other Features
