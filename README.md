# IBCSend

A Sentinel IBC Transactor

This will send a user specified amount of DVPN to a recipient address on the proper receiving chain.

# Install

* requires requests

* requires sentinel-sdk

Install dependencies:

```shell
pip install requests sentinel-sdk
```

# Configure

Edit the **scrtsxx.py** file with the appropriate values. You need to edit:

* WalletName - name of the wallet for the appropriate seed in the keyring

* HotWalletPW - password for the keyring

* WalletSeed - if adding a new wallet to the keyring, please specify the seed phrase here

# Running:

You can and always should run:

```shell
python3 ibcsend.py --help
```

Which shows

```shell
(ibc) freQniK>python3 ibcsend.py -h
usage: ibcsend.py [-h] [--seed] [--osmosis] [--channel channel] [--balance] [-r address] [-a dvpn]

You down with IBC - Meile IBC Send - by freQniK - version: 20240830.0136

options:
  -h, --help            show this help message and exit
  --seed                If a seed phrase is present in scrtxxs.py
  --osmosis             Autosend to Osmosis address on same private key
  --channel channel     channel number of the relayer, Osmosis: 0, Cosmos: 12, Secret: 50, Archway: 92
  --balance             Get DVPN Balance of wallet
  -r address, --receiver address
                        address on receiving chain to send to
  -a dvpn, --amount dvpn

```

If you are using a new wallet that wasn't added the the keyring, edit **scrtxxs.py** with your seedphrase and use the **--seed** flag when running ibcsend.py. The **--seed** flag is in addition to other flags and will conduct an ibc transfer with your given flags on the wallet of the provided seedphrase. 



Once your wallet is added the keyring you can issue an ibcsend directly to your osmosis account on the same wallet, e.g.

```shell
python3 ibcsend.py --osmosis -a 1337
```

You can check your wallet balance (dvpn) by issuing

```shell
python3 ibcsend.py --balance
```

When changing wallets that are already stored in the keyring, you just need to edit **WalletName** in the **scrtxxs.py** file to run any command with ibcsend.



# Keyring & Logfile:

The keyring and transaction logfile is stored in

OS X:

```shell
/Users/username/.meile-ibc
```

Linux

```shell
/home/username/.meile-ibc
```

Logfile in the above directory

```shell
ibc.log
```

# Donations

Because we are working on a small grant with no VC funding, any additional contributions to our developer team is more than certainly welcomed. It will help fund future releases.

## BTC (Bitcoin)

```
bc1qtvc9l3cr9u4qg6uwe6pvv7jufvsnn0xxpdyftl
```

![BTC](file:///home/bubonic/git/MathNodes/MultiPay/img/BTC.png?msec=1723963048122)

## DVPN (Sentinel)

```
sent12v8ghhg98e2n0chyje3su4uqlsg75sh4lwcyww
```

![dvpn](file:///home/bubonic/git/MathNodes/MultiPay/img/DVPN.png?msec=1723963048122)

## XMR (Monero)

```
87qHJPU5dZGWaWzuoC3My5SgoQSuxh4sHSv1FXRZrQ9XZHWnfC33EX1NLv5HujpVhbPbbF9RcXXD94byT18HonAQ75b9dyR
```

![xmr](file:///home/bubonic/git/MathNodes/MultiPay/img/XMR.png?msec=1723963048123)

## ARRR (Pirate Chain)

```
zs1gn457262c52z5xa666k77zafqmke0hd60qvc38dk48w9fx378h4zjs5rrwnl0x8qazj4q3x4svz
```

![ARRR](file:///home/bubonic/git/MathNodes/MultiPay/img/ARRR.png?msec=1723963048122)
