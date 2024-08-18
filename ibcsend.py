#!/bin/env python3

import time
import requests
import argparse
import sys

import scrtxxs

from os import path, mkdir
from grpc import RpcError
from datetime import datetime

from mospy import Account, Transaction
from mospy.clients import HTTPClient, GRPCClient

from sentinel_protobuf.ibc.applications.transfer.v1.tx_pb2 import MsgTransfer
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_protobuf.ibc.core.client.v1.client_pb2 import Height

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import TxParams
from sentinel_sdk.utils import search_attribute

from keyrings.cryptfile.cryptfile import CryptFileKeyring
import ecdsa
import hashlib
import bech32
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from Crypto.Hash import RIPEMD160

GRPC = scrtxxs.GRPC
SSL = scrtxxs.SSL
SATOSHI = 1000000
VERSION = 20240818.0129

class IBCSend():
    def __init__(self, keyring_passphrase, wallet_name, seed_phrase = None):
        self.wallet_name = wallet_name
        
        if seed_phrase:
            seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
            bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()
            privkey_obj = ecdsa.SigningKey.from_string(bip44_def_ctx.PrivateKey().Raw().ToBytes(), curve=ecdsa.SECP256k1)
            pubkey  = privkey_obj.get_verifying_key()
            s = hashlib.new("sha256", pubkey.to_string("compressed")).digest()
            r = self.ripemd160(s)
            five_bit_r = bech32.convertbits(r, 8, 5)
            account_address = bech32.bech32_encode("sent", five_bit_r)
            print(account_address)
            self.keyring = self.__keyring(keyring_passphrase)
            self.keyring.set_password("meile-ibc", wallet_name, bip44_def_ctx.PrivateKey().Raw().ToBytes().hex())
        else:
            self.keyring = self.__keyring(keyring_passphrase)
                
        
        private_key = self.keyring.get_password("meile-ibc", self.wallet_name)
        
        self.grpcaddr, self.grpcport = GRPC.split(":")
        
        self.sdk = SDKInstance(self.grpcaddr, int(self.grpcport), secret=private_key, ssl=SSL)
        
        self.logfile = open(path.join(scrtxxs.KeyringDIR, "ibc.log"), "a+")
        now = datetime.now()
        self.logfile.write(f"\n---------------------------{now}---------------------------\n")
    
    def ripemd160(self, contents: bytes) -> bytes:
        """
        Get ripemd160 hash using PyCryptodome.
    
        :param contents: bytes contents.
    
        :return: bytes ripemd160 hash.
        """
        h = RIPEMD160.new()
        h.update(contents)
        return h.digest()
    
    def __keyring(self, keyring_passphrase: str):
        if not path.isdir(scrtxxs.KeyringDIR):
            mkdir(scrtxxs.KeyringDIR)
        
        kr = CryptFileKeyring()
        kr.filename = "keyring.cfg"
        kr.file_path = path.join(scrtxxs.KeyringDIR, kr.filename)
        kr.keyring_key = keyring_passphrase
        return kr 

    def Send(self, recipient: str, amt: int, channel: str):
        # query and set the account parameters
        self.sdk._client.load_account_data(account=self.sdk._account)

        token = Coin(denom="udvpn",
                     amount=str(amt))
        
        ibc_msg = MsgTransfer(
                              source_port="transfer",
                              source_channel="channel-" + channel,
                              sender=self.sdk._account.address,
                              receiver=recipient,
                            )
        
        resp = requests.get("https://rpc.mathnodes.com/status")
        height = int(resp.json()['result']['sync_info']['latest_block_height'])
        print(height)
        timeout_height = Height(
                                  revision_height=0, # I prefer to use the timestamp
                                  revision_number=0 # This can be 0 too to disable it
                                )
        
        ibc_msg.timeout_height.CopyFrom(timeout_height)
        ibc_msg.token.CopyFrom(token)
        ibc_msg.timeout_timestamp = time.time_ns() + 600 * 10 ** 9
        
        fee = Coin(
                    denom="udvpn",
                    amount="20000"
                )
        
        tx = Transaction(
            account=self.sdk._account,
            fee=fee, # Alterntive: tx.fee.CopyFrom(fee)
            gas=150000,
            chain_id="sentinelhub-2"
        )
        
        tx.add_raw_msg(ibc_msg, type_url="/ibc.applications.transfer.v1.MsgTransfer")
        
        
        try:
            tx = self.sdk._client.broadcast_transaction(transaction=tx)
            
        except RpcError as rpc_error:
            details = rpc_error.details()
            print("details", details)
            print("code", rpc_error.code())
            print("debug_error_string", rpc_error.debug_error_string())
            self.logfile.write("[sp]: RPC ERROR. ")
            return False
        
        if tx.get("log", None) is None:
            tx_response = self.sdk.nodes.wait_for_tx(tx["hash"])
            tx_height = tx_response.get("txResponse", {}).get("height", 0) if isinstance(tx_response, dict) else tx_response.tx_response.height
            
            message = f"Succefully sent {amt}udvpn at height: {tx_height} to {recipient}, tx: {tx['hash']}" if tx.get("log", None) is None else tx["log"]
            self.logfile.write(f"[sp]: {message}\n")
            print(tx_response)
            print(tx_height)
            return True
        
        else:
            print("HI")
            print(tx.get("log"))
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"You down with IBC - Meile IBC Send - by freQniK - version: {VERSION}")
    parser.add_argument('--seed', action='store_true', default=False, help='If a seed phrase is present in scrtxxs.py')
    parser.add_argument('--channel', help="channel number of the relayer, Osmosis: 0, Cosmos: 12, Secret: 50, Archway: 92", metavar="channel")
    parser.add_argument('-r', '--receiver', help="address on receiving chain to send to", metavar="address")
    parser.add_argument('-a', '--amount', help="dvpn to ibc send", metavar="dvpn")
    
    args = parser.parse_args()
    
    
    if not args.receiver or not args.amount or not args.channel:
        print("You need to specifiy a recipient address, an amount in dvpn, and a relayer channel no.")
        parser.print_help()
        sys.exit(0)
    
    if args.seed:
        ibc = IBCSend(keyring_passphrase=scrtxxs.HotWalletPW,
                      wallet_name=scrtxxs.WalletName, 
                      seed_phrase=scrtxxs.WalletSeed
                      )
        
    else:
        ibc = IBCSend(keyring_passphrase=scrtxxs.HotWalletPW,
                      wallet_name=scrtxxs.WalletName, 
                      seed_phrase=None
                      )

    
    ibc.Send(args.receiver, int(float(args.amount) * SATOSHI), str(args.channel))
    