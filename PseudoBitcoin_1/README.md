## Prerequisites
- python 3.x
- python module:
    - time
    - hashlib
    - json
    

## How to use my pseudo bitcoin
- add a new block with transtion "blablabla"
    ```
    python PseudoBitcoin.py addblock transaction { "blablabla" }
    ```
- print the whole blockchain
    ```
    python PseudoBitcoin.py printchain
    ```
- print the block [ height ] in the blockchain <br>
( Notice that height starts from 0 )
    ```
    python PseudoBitcoin.py printblock height { height }
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
    - [ ] UTXO
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
