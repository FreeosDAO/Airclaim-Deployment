#!/usr/bin/env python3

"""
    __author__ = "Mohammad Shahid Siddiqui"
    __license__ = "GPL"
    __version__ = "2.0"
    __email__ = "mssiddiqui.nz@gmail.com"
    __status__ = "Test"
    __copyright__ = "(c) 2021"
    __date__ = "27 May 2021"
    This script creates new user and completes its kyc with the contract
"""

import inspect
import json
import sys
import time
import webbrowser

from os import path, chdir
from datetime import datetime
from pathlib import Path
from re import match
from subprocess import Popen, PIPE

AIRCLAIM_SC = "freeos3"
CONFIG_SC = "freeoscfg3"
CURRENCY_SC = "freeostoken3"
DIVIDEND_SC = "optionsdiv3"
EOSIO_TOKEN_SC = "eosio.token"

END_POINT = "https://protontestnet.greymass.com"
proton = f"/usr/local/bin/cleos -u {END_POINT}"
HOME_DIR=Path.home()
WALLET_DIR = f"{HOME_DIR}/eosio-wallet"
USERS_FILE = f"{HOME_DIR}/new_users.csv"
ACCOUNT_PATTERN = "(^[a-z1-5.]{2,11}[a-z1-5]$)|(^[a-z1-5.]{12}[a-j1-5]$)"
CREATE_WALLET_CMD = f"{proton} wallet create -n proton_ACCOUNT --file {WALLET_DIR}/proton_ACCOUNT.psw"
CREATE_KEY_CMD = f"{proton} wallet create_key -n proton_ACCOUNT"
ACC_PASSWORD_FILE=f"{WALLET_DIR}/proton_ACCOUNT.psw"

LOG_FILE = f"freeos_execution-{datetime.now().strftime('%b%d_%H')}.log"
WALLET_UNLOCK = f"{proton} wallet unlock -n proton_ACCOUNT --password PASSWORD"
GET_PVTKEYS_CMD = f"{proton} wallet private_keys -n proton_ACCOUNT --password PASSWORD"

CREATE_ACC_FAUCET_URL = "https://monitor.testnet.protonchain.com/#account"
GET_SYS_RESOURCES_URL = "https://monitor.testnet.protonchain.com/#faucet"

USER_KYC_INFO_CMD=f"{proton}  get table {CONFIG_SC} {CONFIG_SC} usersinfo --limit 99999"
METAL_KYC_CMD=f"{proton} push action {CONFIG_SC} userverify '[\"ACCOUNT\", \"metal.kyc\", true]' -p {CONFIG_SC}@active"
TRULIOO_KYC_CMD=f"{proton} push action {CONFIG_SC} addkyc '[\"ACCOUNT\", \"metal.kyc\", " \
                f"\"trulioo:address,trulioo:lastname,trulioo:firstname,trulioo:birthdate\", KYC_DATE]' -p {CONFIG_SC}"
caller = lambda: inspect.stack()[2][3]

class FreeOsUser(object):
    def __init__(self, account, password=None, user_type=None):
        self.account=account
        self.password=password
        self.user_type=user_type
        self.account_public_keys=list()
        self.verified_state=None
        self.user_registration_info=None

    def validate_name_str(self):
        check = match(ACCOUNT_PATTERN, self.account)
        if not check:
            print(f"Account '{self.account}' in not in valid format. Exiting ...")
            sys.exit(-1)
        return check

    def set_dir(self):
        chdir(WALLET_DIR)

    def log(self, message):
        with open(f"{Path.home()}/{LOG_FILE}", "a") as dfl:
            dfl.writelines(f"\n{datetime.now()} - {message}")

    def run(self, cmd):
        status = -1
        proc_output = proc_err = None
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")
        if 'password' in cmd:
            print(f"{time_stamp}{caller()}(): {' '.join(cmd.split(' ')[:-1]) + ' *****'}")
        else:
            print(f"{time_stamp}{caller()}(): {cmd}")
        try:
            self.log(f"{caller()}(): {cmd}")
            proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            status = proc.returncode
            proc_output, proc_err = proc.communicate()
            proc_output = proc_output.strip()
            proc_err = proc_err.strip()
            if not status:
                if (not proc_output) or proc_err:
                    status = -1
                else:
                    status = 0
            self.log(f"{caller()}(): status:{status}: output: {proc_output} {proc_err}")
            if 'push action' in cmd:
                print(f"{caller()}(): status:{status}: output: {proc_output}: {proc_err}")
            return status, proc_output, proc_err
        except Exception as exp:
            self.show(str(exp))
            ans = input("Do you want to continue (press 'C' to continue, 'q' to quit) [Continue/quit]? " or "C")
            if ans.lower() in ['q', 'quit']:
                self.log(f"Exiting ...\n")
                print("Exiting ...")
                sys.exit(-1)
            return status, proc_output, proc_err

    def show(self, message, err=None):
        if err:
            err = err.strip()
            message = f"{message} [Error:{err}]"
        self.log(f"{caller()}(): {message}")
        print(f"{caller()}(): {message}")

    def check_existing_wallet(self):
        exists = False
        checked_files=list()
        for wfile in [f"proton_{self.account}.psw", f"proton_{self.account}.wallet"]:
            if path.exists(f"{WALLET_DIR}/{wfile}"):
                exists = True
                checked_files.append(f"{WALLET_DIR}/{wfile}")
        if exists:
            self.show(f"Wallet already present: {self.account} ({checked_files})")
        return exists

    def load_password(self):
        passwd_file=ACC_PASSWORD_FILE.replace('ACCOUNT',self.account)
        try:
            with(open(passwd_file)) as pfile:
                self.password=pfile.readline().strip()
            self.log(f"Password fetched for account '{self.account}'")
        except Exception as exp:
            self.show(f"Failed in opening file: '{passwd_file}' : {repr(exp)}")
            if(input(f"Could not find file: '{passwd_file}'. Do you want to continue for next step? "
                     "[Press 'ENTER' to continue] or [quit]").lower() in ['q','quit']):
                sys.exit(-1)

    def unlock_wallet(self):
        if not self.password:
            self.load_password()
        cmd=WALLET_UNLOCK.replace("ACCOUNT",self.account).replace("PASSWORD", self.password)
        s,o,e=self.run(cmd)
        return s,o,e

    def fetch_public_keys(self):
        s,o,e = self.fetch_keys()
        keys=[]
        for k in o.split("\""):
            if "EOS" in k:
                keys.append(k.strip())
        return self.account, keys

    def fetch_keys(self):
        cmd=GET_PVTKEYS_CMD.replace("ACCOUNT", self.account).replace("PASSWORD", self.password)
        return self.run(cmd)

    def create_key(self):
        cmd=CREATE_KEY_CMD.replace("ACCOUNT", self.account)
        return self.run(cmd=cmd)

    def create_wallet(self):
        if not self.validate_name_str():
            sys.exit(-1)
        cmd=CREATE_WALLET_CMD.replace("ACCOUNT", self.account)
        return self.run(cmd=cmd)

    def create(self):
        if not self.validate_name_str():
            print(f"Invalid Name String: {self.account}")
            sys.exit(-1)
        if self.check_existing_wallet():
            self.load_password()
            return self
        self.create_wallet()
        self.load_password()
        self.create_key()
        self.create_key()


    def register_on_network(self):
        if not self.account_public_keys:
            self.account_public_keys=self.fetch_public_keys()[1]
        ans= None
        while not (ans in ['y','yes']):
            print(f"Account '{self.account}' : Public Keys = {self.account_public_keys}")
            ans=input(f"Have you created the account on the network: {CREATE_ACC_FAUCET_URL}? [yes/NO]: ").lower()
            if (ans in ['y','yes']):
                return True
            else:
                self.show(f"Enter the account name, and keys in the browser, and press 'Create' button")
                webbrowser.open(CREATE_ACC_FAUCET_URL)
            return self.register_on_network()

    def is_verified(self):
        return self.verified_state

    def verify_kyc_user(self, user, verification):
        if user.is_verified():
            return user.is_verified()

        user.verified_state=verification

        if verification in ['d','v']:
            s,o,e=self.run(METAL_KYC_CMD.replace("ACCOUNT", user.account))
            self.show(f"{s}:{o}{e}")
        if verification == 'v':
            s,o,e=self.run(TRULIOO_KYC_CMD.replace("ACCOUNT", user.account).replace("KYC_DATE",str(int(time.time()))))
            self.show(f"{s}:{o}{e}")
        user.verified_state=self.fetch_user_registration_info()
        return user.verified_state

    def get_kyc_verified(self):
        if self.user_type in [None, 'e']:
            return
        if self.user_type in ['d','v']:
            s,o,e=self.run(METAL_KYC_CMD.replace("ACCOUNT", self.account))
            self.show(f"{s}:{o}{e}")
        if self.user_type in ['v']:
            s,o,e=self.run(TRULIOO_KYC_CMD.replace("ACCOUNT", self.account).replace("KYC_DATE",str(int(time.time()))))
            self.show(f"{s}:{o}{e}")

    def fetch_kyc_verification_details(self):
        if not self.user_registration_info:
            return self.fetch_user_registration_info()
        return self.user_registration_info

    def fetch_user_registration_info(self):
        cmd=USER_KYC_INFO_CMD
        s,o,e=self.run(cmd)
        users = json.loads(o)["rows"]
        for user in users:
            if self.account == user["acc"]:
                self.user_registration_info=dict(user)
        print(f"{self.account} KYC = {self.user_registration_info}")
        return self.user_registration_info

    def insert_user_record(self, user):
        if user:
            message=f"{user.account},{user.user_type},{user.password}\n"
            with (open(USERS_FILE,"a")) as usf:
                usf.write(message)
            self.show(f"Record Updated: {message}")
        else:
            print(f"Empty User: {user}")

def multiple_users():
    #Modify below properties and run the script.
    users={"e3qmsseomss": "e",
           "v3qctorvezs": "v",
           "d3qpodrdes": "d"}
    freeos_conf=FreeOsUser(account=CONFIG_SC)
    freeos_conf.unlock_wallet()
    for user_name, user_kyc_type in users.items():
        euser=FreeOsUser(account=user_name, user_type=user_kyc_type)
        euser.create()
        euser.register_on_network()
        euser.get_kyc_verified()
        kyc=euser.fetch_kyc_verification_details()
        freeos_conf.insert_user_record(euser)
        print(f"{user_name}:{kyc}")


def single_user():
    #Modify below properties for one user and run the script.
    user_name="vavianvivase"
    user_kyc_type='v'

    freeos_conf=FreeOsUser(account=CONFIG_SC)
    freeos_conf.unlock_wallet()

    euser=FreeOsUser(account=user_name, user_type=user_kyc_type)
    euser.create()
    euser.register_on_network()
    euser.get_kyc_verified()
    kyc=euser.fetch_kyc_verification_details()
    freeos_conf.insert_user_record(euser)
    print(f"{user_name}:{kyc}")

if __name__=='__main__':
    print(f"Uncomment one of the lines as per the usecase:")
    #single_user()
    multiple_users()
    print(f"Script complete.")
