#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
    __author__ = "Mohammad Shahid Siddiqui"
    __license__ = "GPL"
    __version__ = "1.0.0"
    __email__ = "mssiddiqui.nz@gmail.com"
    __status__ = "Test"
    __copyright__ = "(c) 2021"
    __date__ = "03 Jun 2021"
"""

import json
import sys
import getopt
import inspect
import webbrowser
import time

#from argparse import ArgumentParser
from subprocess import PIPE, Popen, run
from os import chdir, getcwd, path
from datetime import datetime, timedelta, timezone
from pathlib import Path
from re import match
HOME_DIR=f"{Path.home()}".rstrip('/')


# Project Settings
NFT_USER_FILE = "dividend_nft_users.csv"
NFT_USER_COUNT=2
END_POINT = "https://protontestnet.greymass.com"

VOTER_1="voterone"
VOTER_2="votertwo"
PROPOSER="proposer"
WAIT_BEFORE_DIVCOMPUTE_FLAG=True

WALLET_DIR = f"{HOME_DIR}/eosio-wallet"
ACC_PASSWORD_FILE=f"{WALLET_DIR}/proton_ACCOUNT.psw"
#BINARY_DIR = f"{WALLET_DIR}/eos-binaries"
LOG_FILE = f"{HOME_DIR}/dividend-{datetime.now().strftime('%b%d_%H')}.log"

proton = f"/usr/local/bin/cleos -u {END_POINT}"
#CREATE_ACC_FAUCET = "https://monitor.testnet.protonchain.com/#account"
#RAM_RESOURCES_GET = "https://monitor.testnet.protonchain.com/#faucet"
#FILTER="DIV-AUDIT: "

# Contracts
#AIRCLAIM_SC = "freeos3"
#CONFIG_SC = "freeoscfg3"
#CURRENCY_SC = "freeostoken3"
DIVIDEND_SC = "optionsdiv3"
#EOSIO_TOKEN_SC = "eosio.token"

#ACCOUNT_PATTERN = "(^[a-z1-5.]{2,11}[a-z1-5]$)|(^[a-z1-5.]{12}[a-j1-5]$)"
#CREATE_WALLET_CMD = f"{proton} wallet create -n proton_ACCOUNT --file {WALLET_DIR}/proton_ACCOUNT.psw"
#CREATE_KEY_CMD = f"{proton} wallet create_key -n proton_ACCOUNT"
#GET_PVTKEYS_CMD = f"{proton} wallet private_keys -n proton_ACCOUNT --password PASSWORD"
WALLET_UNLOCK = f"{proton} wallet unlock -n proton_ACCOUNT --password PASSWORD"
#WALLET_LOCK = f"{proton} wallet lock -n proton_ACCOUNT"

#BUY_RAM_CMD = f"{proton} push action eosio buyram '[\"PAYER\", \"ACCOUNT\", \"CURRENCY\"]' -p PAYER"
#GET_ALL_ITERATIONS_CMD = f"{proton} get table {CONFIG_SC} {CONFIG_SC} iterations --limit 2000"

#UPDATE_ITERATION = f"{proton} push action {CONFIG_SC} iterupsert '[ITER,\"START\",\"END\",CLAIM,HOLD]'
#STAKED_USER_COUNT_CMD=f"{proton} get scope {AIRCLAIM_SC}  -t users --limit 4999| grep 'scope'"
#OPTIONS_VESTED_CMD=f"{proton} get table {AIRCLAIM_SC} ACCOUNT VEST_PARAM"
#REGUSER_CMD=f"{proton} push action {AIRCLAIM_SC} reguser '[\"ACCOUNT\"]' -p ACCOUNT@active"
#USER_INFO_CMD=f"{proton}  get table {CONFIG_SC} {CONFIG_SC} usersinfo --limit 99999"
#READ_GLOBAL_TABLE_CMD=f"{proton} get table {CONFIG_SC} {CONFIG_SC} parameters"

caller = lambda: inspect.stack()[2][3]
log_file_des=open(f"{LOG_FILE}", "a")

class Executor(object):
    def __init__(self):
        self.set_dir()

    def set_dir(self):
        chdir(WALLET_DIR)
        self.log(f"Changed Working Dir to: {getcwd()}")

    def log(self, message):
        log_file_des.writelines(f"\n{datetime.now()} - {message}")

    def show(self, message, err=None):
        if err:
            err = err.strip()
            message = f"{message} [Error:{err}]"
        self.log(f"{caller()}(): {message}")
        print(f"{caller()}(): {message}")

    def to_clipboard(self, message):
        try:
            run("pbcopy", universal_newlines=True, input=message)
        except Exception as exp:
            print(f"Could not copy to clipboard:'{message}'\n{repr(exp)}")

    def track(self, source, target):
        source=source.strip()
        if not source:
            self.log(f"Source has no message to check. Skipping parsing of '{target}'")
            return False
        target = target.strip()
        if not target:
            self.log(f"Target is empty. Skipping the message parsing")

        for l in source.split('\n'):
            if target in l:
                self.log(f"'{target}' found in the message: {l}")
                return l
        return False

    def locate_message_in_output(self, message, output, error):
        for source in [output, error]:
            found = self.track(source=source, target=message)
            if found:
                return found
        return False

    def run(self, cmd):
        status = -1
        proc_output = proc_err = None
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")
        ignore_list=['Wallet is already unlocked'] #To extend later
        log_file_des.flush()
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
            ans = input("Do you want to continue [Continue/quit]? ") or "C"
            if ans.lower() in ['q', 'quit']:
                self.show(f"Exiting ...\n")
                sys.exit(-1)
            return status, proc_output, proc_err


class User(object):
    def __init__(self, account,
                 user_role,
                 user_type=None,
                 password=None):
        self.account=account
        self.password=password
        self.user_type=user_type
        self.user_role=user_role

        self.exec=Executor()
        self.run=self.exec.run
        self.show=self.exec.show
        self.log=self.exec.log
        self.show(f"Account '{self.account}' instantiated")
        self.load_password()

    def __repr__(self):
        return f"{self.account}:{self.user_type}:{self.user_role}"

    def unlock_wallet(self):
        print(f"Unlocking Wallet: {self.account}")
        cmd=WALLET_UNLOCK.replace("ACCOUNT",self.account).replace("PASSWORD", self.password)
        s,o,e=self.run(cmd)
        self.log(f"{s}:{o}:{e}")
        return s,o,e

    def load_password(self):
        passwd_file=ACC_PASSWORD_FILE.replace('ACCOUNT',self.account)
        try:
            with(open(passwd_file)) as pfile:
                self.password=pfile.readline().strip()
            assert self.password, f"Required: Password for {self.account}"
            self.log(f"Password fetched for account '{self.account}'")
        except Exception as exp:
            self.show(f"Failed in opening file: '{passwd_file}' : {repr(exp)}")
            sys.exit(-1)

    def set_role(self, user_role):
        self.user_role=user_role
        self.log(f"{self.account} : Role is set to {self.user_role}")

class Dividend(User):

    def __init__(self,account, user_role, user_type=None, password=None):
        User.__init__(self, account, user_role, user_type, password)
        self.white_list=dict()
        self.nft_users=dict()

    def set_proposer(self, proposer):
        self.unlock_wallet()
        cmd=f"{proton} push action {DIVIDEND_SC} upsert '\x7b\"role_type\":1, \"role_acct\": \"{proposer.account}\"\x7d' -p {DIVIDEND_SC}@active"
        self.show(f"Setting up the Proposer '{proposer.account}' in Whitelist")
        self.white_list["proposer"] = proposer
        return self.run(cmd=cmd)

    def set_voter(self, voter, role_type):
        self.unlock_wallet()
        voter.user_role=f"{role_type}"
        cmd=f"{proton} push action {DIVIDEND_SC} upsert '\x7b\"role_type\":{role_type}, \"role_acct\": \"{voter.account}\"\x7d' -p {DIVIDEND_SC}@active"
        self.show(f"Setting up the Voter {voter.account} [Role={role_type}] in Whitelist")
        self.white_list[f"voter{role_type}"]=voter
        return self.run(cmd)

    def update_whitelist(self, proposer, voter1, voter2):
        self.set_proposer(proposer=proposer)
        self.set_voter(voter=voter1, role_type=2)
        self.set_voter(voter=voter2, role_type=3)

    def fetch_whitelist(self):
        # Fetch the whitelist from network
        pass

    def get_whitelist(self):
        self.log(f"White List : {self.white_list}")
        return self.white_list

    def dividend_compute(self):
        if WAIT_BEFORE_DIVCOMPUTE_FLAG:
            ans = None
            while (ans not in ['y', 'yes']):
                ans = input("Ready for Dividend compute? [y/N]: ") or 'N'
                print(f"Entered reply: {ans}")


        cmd=f"{proton} push action {self.account} dividcompute '\x7b\x7d' -p {self.account}@active"
        self.show(f"Computing Dividend: {cmd}")
        s,o,e= self.run(cmd)
        self.show(f"{s}:{o}:{e}")
        return s,o,e

    def populate_nft_users(self, source_file=NFT_USER_FILE, limit=NFT_USER_COUNT):
        with open(source_file) as sf:
            for line in sf.readlines():
                if line.startswith("#"):
                    continue
                name, *x = line.split(',')
                self.nft_users[name] = User(name)
                limit -= 1
                if limit <= 0:
                    return self.nft_users

class Voter(User):
    def __init__(self,account, user_role, user_type=None, password=None):
        User.__init__(self, account, user_role, user_type, password)
        self.white_list=dict()

    def vote(self, value):
        cmd=f"{proton} push action {DIVIDEND_SC} proposalvote '\x7b\"voter\":\"{self.account}\",\"vote\":{value}\x7d' -p {self.account}@active"
        self.show(f"Voting for the proposal : {self.account} voting {value}")
        return self.run(cmd)


class Proposer(User):
    def propose_nft(self, nft_account, roi_target_cap, percent, threshold, rates_left=0, locked="false"):
        print(f"Proposal Initiated")
        if (not locked):
            locked = "false"
        else:
            locked=locked.lower()

        threshold = str(threshold)
        if not threshold.endswith("OPTION"):
            updated_threshold = f"{int(threshold)}.0000 OPTION"
            self.show(f"Tweaked the Popposal threshold from: {threshold} -> {updated_threshold} due to inconsistent input")
            threshold=updated_threshold

        cmd=f"{proton} push action {DIVIDEND_SC} proposalnew '\x7b" \
            f"\"proposername\":\"{self.account}\"," \
            f"\"eosaccount\":\"{nft_account}\"," \
            f"\"roi_target_cap\":{roi_target_cap}, " \
            f"\"period_percentage\":\"{percent}\","\
            f"\"threshold\":\"{threshold}\","\
            f"\"rates_left\":{rates_left}," \
            f"\"locked\":{locked}" \
            f"\x7d' -p {self.account}@active"
        s,o,e= self.run(cmd)
        self.show(f"{s}:{o}:{e}")
        return s,o,e

if __name__=='__main__':
    log_file_des.write(f"{datetime.now()} - Script Started!")
    print(f"{datetime.now()} - Script Started [Logs: {log_file_des.name}]")
    nft_user="shahid"
    dividendSC=Dividend(DIVIDEND_SC, DIVIDEND_SC)
    proposer = Proposer(PROPOSER, "Proposer")

    voter1 = Voter(VOTER_1, "Voter-1")
    voter2 = Voter(VOTER_2, "Voter-2")

    dividendSC.update_whitelist(proposer,voter1, voter2)
    print(f"Whitelist: {dividendSC.get_whitelist()}")

    proposer.propose_nft(nft_user, 3, 3.5, "100.0000 OPTION")
    proposer.propose_nft(nft_user, 3, 3.5, 56)


    #Mint NFT for users
    voter1.vote(2)
    voter2.vote(2)

    #Claim for users in iterations
    #ToDo

    #call Dividend Compute
    dividendSC.dividend_compute()

    #Clean Up
    message=f"{datetime.now()} - Script Finished [Logs: {log_file_des.name}]"
    print(message)
    log_file_des.write(message)
    log_file_des.close()