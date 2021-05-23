#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    __author__ = "Mohammad Shahid Siddiqui"
    __license__ = "GPL"
    __version__ = "2.0"
    __email__ = "mssiddiqui.nz@gmail.com"
    __status__ = "Test"
    __copyright__ = "(c) 2021"
    __date__ = "23 May 2021"
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

# Iteration Settings
START_ITERATION_TIME = "2021-05-23T08:00:00" #This time is in UTC. Offset properly from local time zone
ITERATION_INTERVAL = "04:00:00"
MAX_ITERATIONS = 7
EXCHANGE_RATE = "0.00053"
TARGET_RATE = "0.0167"

# Project Settings
USERS_FILE = "registered_users.csv"
WALLET_DIR = f"{Path.home()}/eosio-wallet"
BINARY_DIR = f"{Path.home()}/eos-binaries"
LOG_FILE = f"eos-deployment-{datetime.now().strftime('%b%d_%H')}.log" #%H%M%S
#LOG_FILE = f"eos-deployment.log"
END_POINT = "https://protontestnet.greymass.com"
proton = f"/usr/local/bin/cleos -u {END_POINT}"
CREATE_ACC_FAUCET = "https://monitor.testnet.protonchain.com/#account"
RAM_RESOURCES_GET = "https://monitor.testnet.protonchain.com/#faucet"

# Contracts
AIRCLAIM_SC = "freeosd"
CONFIG_SC = "freeoscfgd"
CURRENCY_SC = "freeostokend"
DIVIDEND_SC = "freeosdiv"
EOSIO_TOKEN_SC = "eosio.token"

CURRENCY_OPTION_VAL = "350000000000000.0000 OPTION"
CURRENCY_AIRKEY_VAL = "1000000 AIRKEY"
CURRENCY_FREEOS_VAL = "350000000000000.0000 FREEOS"
XPR_TO_BUY_RAM = "25000.0000 XPR"

# Commands - DO NOT Edit
ACCOUNT = "ACCOUNT"
PASSWORD = "PASSWORD"
ACCOUNT_PATTERN = "(^[a-z1-5.]{2,11}[a-z1-5]$)|(^[a-z1-5.]{12}[a-j1-5]$)"
CREATE_WALLET_CMD = f"{proton} wallet create -n proton_ACCOUNT --file {WALLET_DIR}/proton_ACCOUNT.psw"
CREATE_KEY_CMD = f"{proton} wallet create_key -n proton_ACCOUNT"
GET_PVTKEYS_CMD = f"{proton} wallet private_keys -n proton_ACCOUNT --password PASSWORD"
WALLET_UNLOCK = f"{proton} wallet unlock -n proton_ACCOUNT --password PASSWORD"
WALLET_LOCK = f"{proton} wallet lock -n proton_ACCOUNT"
DEPLOY_CONTRACT = f"{proton} set contract ACCOUNT {BINARY_DIR}/SC_DIR -p ACCOUNT"
CREATE_CURRENCY = f"{proton} push action ACCOUNT create '[\"ACCOUNT\", \"CURRENCY\"]' -p ACCOUNT"
BUY_RAM_CMD = f"{proton} push action eosio buyram '[\"PAYER\", \"ACCOUNT\", \"CURRENCY\"]' -p PAYER"
GET_ALL_ITERATIONS_CMD = f"{proton} get table {CONFIG_SC} {CONFIG_SC} iterations --limit 2000"
TRANSFER_TOKEN_PERM_CMD = f"{proton} push action {CONFIG_SC} transfadd '[\"TO_ACCOUNT\"]' -p {CONFIG_SC}"
EXCHANGE_CMD = f"{proton} push action {CONFIG_SC} currentrate '[EXCHANGE]' -p {CONFIG_SC}@active"
TARGET_RATE_CMD = f"{proton} push action {CONFIG_SC} targetrate '[EXCHANGE]' -p {CONFIG_SC}@active"
UPDATE_ITERATION = f"{proton} push action {CONFIG_SC} iterupsert '[ITER,\"START\",\"END\",CLAIM,HOLD]' -p {CONFIG_SC}"
USER_STAKE_CMD=f"{proton} push action {EOSIO_TOKEN_SC} transfer " \
               f"'[\"ACCOUNT\", \"{AIRCLAIM_SC}\",\"STAKE\", \"freeos stake\"]'  -p ACCOUNT@active"
STAKE_UPSERT = f"{proton} push action {CONFIG_SC} stakeupsert 'STAKE' -p {CONFIG_SC}@active"
OPTIONS_VESTED_CMD=f"{proton} get table {AIRCLAIM_SC} ACCOUNT VEST_PARAM"
REGUSER_CMD=f"{proton} push action {AIRCLAIM_SC} reguser '[\"ACCOUNT\"]' -p ACCOUNT@active"

ExecutionSummary=""

GLOBAL_PARAMS = {
    "masterswitch": "1",
    "failsafefreq": "5",
    "altverifyacc": CONFIG_SC,
    "unstakesnum": "4",
    "vestpercent": "50"
}
STAKE_UPSERT_LIST = [[0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
                     [5, 0, 0, 0, 10, 20, 0, 0, 0, 0, 0],
                     [10, 0, 0, 0, 20, 30, 0, 0, 0, 0, 0],
                     [20, 0, 0, 0, 30, 50, 0, 10, 0, 0, 0],
                     [30, 0, 0, 0, 50, 80, 0, 20, 0, 0, 0],
                     [40, 0, 0, 0, 80, 130, 0, 30, 0, 0, 0],
                     [50, 0, 0, 0, 130, 210, 0, 50, 0, 0, 0],
                     [60, 0, 0, 0, 210, 340, 0, 80, 0, 0, 0],
                     [70, 0, 0, 0, 340, 550, 0, 130, 0, 0, 0],
                     [80, 0, 0, 0, 550, 890, 0, 210, 0, 0, 0],
                     [90, 0, 0, 0, 890, 1440, 0, 340, 0, 0, 0],
                     [100, 0, 0, 0, 1440, 2330, 0, 550, 0, 0, 0]]
ITERATIONS_TOKENS_ISSUED = {1: [100, 0],
                            2: [125, 0],
                            3: [150, 0],
                            4: [175, 0],
                            5: [200, 275],
                            6: [225, 375],
                            7: [250, 488],
                            8: [275, 613],
                            9: [300, 750],
                            10: [325, 900],
                            11: [350, 1063],
                            12: [375, 1238],
                            13: [400, 1425],
                            14: [425, 1625],
                            15: [450, 1838],
                            16: [475, 2063],
                            17: [500, 2300],
                            18: [525, 2550],
                            19: [550, 2813],
                            20: [575, 3088],
                            21: [600, 3375],
                            22: [625, 3675],
                            23: [650, 3988],
                            24: [675, 4313],
                            25: [700, 4650]}
ITERATIONS_TOKENS_DEFAULT = ITERATIONS_TOKENS_ISSUED[25]
OK_sign=f"\u2713"
abi_map = {AIRCLAIM_SC: "freeos",
           CONFIG_SC: "freeosconfig",
           CURRENCY_SC: "eosio.token",
           DIVIDEND_SC: "dividenda"}
caller = lambda: inspect.stack()[2][3]
exchange_rates = [0.0001,0.0150,0.0200,0.0150,0.0003,
                  0.0100,0.0117,0.0184,0.0167,0.0003,
                  0.0167,0.0006,0.0008,0.0010,0.0011,
                  0.0013,0.0015,0.0016,0.0018,0.0020,
                  0.0021,0.0200,0.0200,0.0200,0.0200,
                  0.0066,0.0077,0.0088,0.0100,0.0111,
                  0.0122,0.0200,0.0144,0.0144,0.0144,
                  0.0144,0.0144,0.0144,0.0211,0.0211,
                  0.0211,0.0211,0.0211,0.0211,0.0211,0.0211]

USER_STAKE_XPR_REQS=dict()
STAKE_GROUPS=[
    [20, 10, 0],
    [30, 20, 0],
    [50, 30, 10],
    [80, 50, 20],
    [130, 80, 30],
    [210, 130, 50],
    [340, 210, 80],
    [550, 340, 130],
    [890, 550, 210],
    [1440, 890, 340],
    [2330, 1440, 550]
]
def update_stake_list():
    values = [iter(range(10,110))]*10
    from itertools import zip_longest
    *x, =(zip_longest(*values, fillvalue='99999'))
    #print(x)
    i = 10
    for v in x:
        j = v[0] // 10
        #print (f"Range[{i}] j={j}: {v}")
        if j > len(STAKE_GROUPS) -1:
            break
        USER_STAKE_XPR_REQS.update(dict.fromkeys(list(v),{
            'e':STAKE_GROUPS[j][0],
            'd':STAKE_GROUPS[j][1],
            'v':STAKE_GROUPS[j][2],
        }))
        i += 1
    #print(USER_STAKE_XPR_REQS[11])
    for i in range(10):
        if i <5:
            USER_STAKE_XPR_REQS[i]={
                'e': 10,
                'd': 0,
                'v': 0
            }
        else:
            USER_STAKE_XPR_REQS[i]={
                'e': 20,
                'd': 10,
                'v': 0
            }
    #print(json.dumps(USER_STAKE_XPR_REQS, indent=4))
    return USER_STAKE_XPR_REQS

class Executor(object):
    def __init__(self):
        update_stake_list()

    def set_dir(self):
        chdir(WALLET_DIR)
        self.log(f"Script Started!\nChanged Dir to: {getcwd()}")

    def log(self, message):
        with open(f"{Path.home()}/{LOG_FILE}", "a") as dfl:
            dfl.writelines(f"\n{datetime.now()}::{message}")

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
                return True
        return False

    def run(self, cmd):
        status = -1
        proc_output = proc_err = None
        if 'password' in cmd:
            print(f"{caller()}(): {' '.join(cmd.split(' ')[:-1]) + ' *****'}")
        else:
            print(f"{caller()}(): {cmd}")
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
            return status, proc_output, proc_err
        except Exception as exp:
            self.show(str(exp))
            ans = input("Do you want to continue (press 'C' to continue, 'q' to quit) [Continue/quit]? " or "C")
            if ans.lower() in ['q', 'quit']:
                self.log(f"Exiting ...\n")
                print("Exiting ...")
                sys.exit(-1)
            return status, proc_output, proc_err

class User(object):
    def __init__(self, account=None, password=None, user_type='e'):
        self.account=account
        self.password=password
        self.user_type=user_type

        self.registered_on=None
        self.current_iteration= 0
        self.currencies = dict()

        self.executor=Executor()
        self.log=self.executor.log
        self.show=self.executor.show
        self.run=self.executor.run

        self.set_dir()
        self.load_password()
        self.unlock_wallet()

    def __repr__(self):
        return f"User:{self.account} [verification mode={self.user_type}]"

    def load_password(self):
        passwd_file=f"proton_{self.account}.psw"
        try:
            with(open(passwd_file)) as pfile:
                self.password=pfile.readline().strip()
            self.log(f"Password fetched for account '{self.account}'")
        except Exception as exp:
            self.show(f"Opening file '{passwd_file}' failed: {repr(exp)}")
            if(input(f"Opening '{passwd_file}' failed. Do you want to continue for next step? "
                     "[to continue, Press Enter] or [quit]").lower()=='quit'):
                sys.exit(-1)

    def set_dir(self):
        chdir(WALLET_DIR)
        self.log(f"Changed current directory to: {getcwd()}")

    def unlock_wallet(self):
        flag = False
        cmd=WALLET_UNLOCK.replace(ACCOUNT,self.account).replace(PASSWORD, self.password)
        s,o,e=self.run(cmd)
        if self.executor.track(e,'Wallet is already unlocked'):
            flag=True
        return flag

    def fetch_pvt_key(self, account=None, password=None):
        if not account:
            account = self.account
        if not password:
            password = self.password
        cmd=GET_PVTKEYS_CMD.replace(ACCOUNT, account).replace(PASSWORD, password)
        return self.run(cmd)

    def locate_message_in_output(self, message, output, error):
        lines = output.split('\n') + error.split('\n')
        for line in lines:
            if message in line:
                return True
        return False

    def get_live_iteration(self):
        cmd = f"{proton} push action {DIVIDEND_SC} version '[]' -p {self.account}@active"
        s,o,e = self.run(cmd)
        for line in e.split('\n')+o.split('\n'):
            if 'ersion =' in line:
                self.current_iteration = int(line.split(' ')[-1])
        return self.current_iteration

    def reguser(self):
        s,o,e=self.run(REGUSER_CMD.replace(ACCOUNT, self.account))
        #If errors= Error 3090003: Provided keys, permissions, and delays do not satisfy declared authorizations'
        #or 'transaction declares authority '{"actor":"xfreeos1","permission":"active"}', but does not have signatures
        # for it'
        # means the account is not yet created with network
        print(s,o,e)

        #Addmore messages as per new erros identified
        messages=['do not satisfy declared authorizations']
        unregistered=False
        keys=[]
        for message in messages:
            if self.locate_message_in_output(message,o,e):
                unregistered = True
                self.log(f"Please create a valid account for '{self.account}' at network {CREATE_ACC_FAUCET}")
                s,o,e = self.fetch_pvt_key(self.account)
                for k in o.split("\""):
                    if "EOS" in k:
                        keys.append(k.strip())
                print(f"{self.account} : Keys = {keys}")
                break
        if self.locate_message_in_output('freeos is not in a claim period', o,e):
            self.show(f"Iteration is not in the correct state. Exiting ...")
            sys.exit(-1)

        if unregistered:
            ans= None
            while not (ans in ['y','yes']):
                print(f"{self.account} : Keys = {keys}")
                self.executor.to_clipboard(CREATE_ACC_FAUCET)
                ans=input(f"Have you created account on network: {CREATE_ACC_FAUCET}? [yes/No]: ").lower()
                if ans in ['y','yes']:
                    return self.reguser()
                webbrowser.open(CREATE_ACC_FAUCET)
                time.sleep(5)
        return s,o,e

    def is_registered_in_network(self):
        pass

    # def get_stake_requirement(self):
    #     pass
    #     STAKE_REQ_CMD=f"{proton} get table {CONFIG_SC} {CONFIG_SC} stakes"
    #     print(self.run(STAKE_REQ_CMD))

    def is_already_staked(self):
        pass

    def get_planned_stake_req(self, user_num, user_type):
        req = 9999
        try:
            assert (user_type in ['e', 'd', 'v']), f"Error: User type not known:{user_type}"
            if user_num in USER_STAKE_XPR_REQS.keys():
                req = USER_STAKE_XPR_REQS[user_num][user_type]
            else:
                req = USER_STAKE_XPR_REQS[100][user_type]
            self.show(f"Stake Requirement for user #{user_num} (type={user_type}) = {req}.0000 XPR")
        except Exception as exp:
            self.show(f"{repr(exp)}\nError: User type not known:{user_type}")
        finally:
            return req

    def count_user_staked(self):
        STAKED_USER_COUNT_CMD=f"{proton} get scope {AIRCLAIM_SC}  -t users --limit 4000| grep 'scope'"
        cmd=STAKED_USER_COUNT_CMD
        s,o,e = self.run(cmd)
        users = len(o.split('\n'))
        self.show(f"Total number of users staked = {users}")
        return users

    def stake(self, iter=None):
        total_staked=self.count_user_staked()
        self.show(f"Already staked users count = {total_staked} [Current Iteration = #{self.get_live_iteration()}]")
        stake_currency_required=f"{self.get_planned_stake_req(total_staked +1,self.user_type)}.0000 XPR"
        self.show(f"Stake Requirement: {self.account} "
                  f"[user type = {self.user_type}] = {stake_currency_required} "
                  f"[Already staked: {total_staked}]"
                  f"[Current Iteration = #{self.get_live_iteration()}]")
        stake_currency_required_val,unit=stake_currency_required.split(' ')
        stake_currency_actual=self.get_currency_balance(unit)
        stake_currency_actual_val=stake_currency_actual

        if float(stake_currency_required_val) > float(stake_currency_actual_val):
            message = f"Error: Possibly Insufficient Fund for Staking required: " \
                      f"{stake_currency_actual} vs {stake_currency_required}"
            self.log(message)
            print(message)

        cmd=USER_STAKE_CMD.replace("ACCOUNT", self.account). \
            replace("STAKE", stake_currency_required)
        s,o,e = self.run(cmd)
        print(s,o,e)
        return s,o,e

    def cancel_stake(self):
        pass

    def get_currency_balance(self, currency, contract=AIRCLAIM_SC):
        CURRENCY_BAL=f"{proton} get currency balance CONTRACT ACCOUNT CURRENCY"
        cmd=CURRENCY_BAL.replace(ACCOUNT,self.account) \
            .replace('CURRENCY', currency) \
            .replace('CONTRACT',contract)
        s,o,e = self.run(cmd)
        self.currencies[currency] = '0.0000'
        if o:
            for cur_line in o.split('\n'):
                self.currencies[currency]=cur_line.split(' ')[0]
        self.log(f"Account '{self.account}' : Currencies :{self.currencies}")
        return self.currencies[currency]

    def verify_unstake_tick_stake(self, iter):
        pass

    def is_claimed(self, iter):
        pass

    def unvest(self):
        pass

    def is_unvested(self, iter):
        pass

    def setup_cron(self):
        SETUP_CRON_CMD=f"{proton} push transaction HELP NEEDED"

    def cron_tick(self):
        CRON_TICK_CMD=f"{proton} push action cron process '[\"ACCOUNT\", \"5\"]' -p ACCOUNT"
        cmd = CRON_TICK_CMD.replace(ACCOUNT, self.account)
        return self.run(cmd)

    def claim(self):
        CLAIM_CMD=f"{proton} push action {AIRCLAIM_SC} claim '[\"ACCOUNT\"]' -p ACCOUNT@active"
        cmd=CLAIM_CMD.replace(ACCOUNT, self.account)
        s,o,e =  self.run(cmd)
        self.show(f"{caller()}(): {s}:{o}:{e}")

    def get_options_vested(self):
        cmd=OPTIONS_VESTED_CMD.replace(ACCOUNT, self.account).replace('VEST_PARAM','vestaccounts')
        s,o,e = self.run(cmd)
        self.log(f"{caller()}(): {s}:{o}:{e}")
        value = json.loads(o)["rows"][-1]["balance"]
        self.show(f"{caller()}(): Vested OPTIONs ={value}")
        return value

    def get_options_account(self):
        cmd=OPTIONS_VESTED_CMD.replace(ACCOUNT, self.account).replace('VEST_PARAM','accounts')
        s,o,e = self.run(cmd)
        self.log(f"{caller()}(): {s}:{o}:{e}")
        value = json.loads(o)["rows"][-1]["balance"]
        self.show(f"{caller()}(): Vested OPTIONs ={value}")
        return value

    def convert_vested_options_to_options(self):
        pass

    def iter_zero_check(self):
        pass

    def reregister(self):
        pass

    def verify_reregister(self):
        pass

    def mint_options(self):
        #ToDO check if account is in Minter whitelist for minting first
        pass

    def is_minter(self):
        # ToDO : Checks if it is in minter whitelist
        pass

    def is_burner(self):
        pass

    def burn_options(self):
        pass

class FreeOsContract(object):
    def __init__(self,
                 airclaim_contract=AIRCLAIM_SC,
                 config_contract=CONFIG_SC,
                 currency_contract=CURRENCY_SC,
                 dividend_contract=DIVIDEND_SC):

        self.airclaimsc=airclaim_contract
        self.configsc=config_contract
        self.currencysc=currency_contract
        self.dividendsc=dividend_contract

        self.current_iteration=dict()
        self.all_iterations=dict() # Actual deployed iterations
        self.iterations=dict() #Proposed Iterations
        self.executor=Executor()
        self.run=self.executor.run

        self.set_dir()
        self.prompt() #Uncomment in Production
        self.evaluate_iterations()
        self.get_current_iteration()

    def set_dir(self):
        chdir(WALLET_DIR)
        self.log(f"Script Started!\nChanged Dir to: {getcwd()}")

    def log(self, message):
        with open(f"{Path.home()}/{LOG_FILE}", "a") as dfl:
            dfl.writelines(f"\n{datetime.now()}::{message}")

    def prompt(self):
        print(f"Please confirm the configuration before continue: ")
        message=f"\tBlockchain end point = {END_POINT}\n" \
                f"\tAirClaim Contract Name = {AIRCLAIM_SC}\n" \
                f"\tFreeOS Config Contract Name = {CONFIG_SC}\n" \
                f"\tDividend Contract Name = {DIVIDEND_SC}\n" \
                f"\tTokens Contract Name = {CURRENCY_SC}\n\n" \
                f"\tAirclaim Iteration Start Time = {START_ITERATION_TIME}\n" \
                f"\tIteration Interval = {ITERATION_INTERVAL}\n" \
                f"\tTotal Iterations = {MAX_ITERATIONS}\n" \
                f"\tExchange Rate = {EXCHANGE_RATE}\n" \
                f"\tTarget Rate = {TARGET_RATE}\n" \
                f"\tDefault Vesting Percent = {GLOBAL_PARAMS['vestpercent']}\n"
        print(message)
        confirm = input("Are these configurations correct? [Y/n]: ") or "y"
        if 'y' != confirm.lower():
            print("\nPlease update the configurations and run with flag options (provide -h for more options)."
                  "\nExiting ...\n")
            sys.exit(0)

    def show(self, message, err=None):
        if err:
            err=err.strip()
            message = f"{message} [Error:{err}]"
        self.log(f"{caller()}(): {message}")
        print(f"{caller()}(): {message}")

    def verify(self, output, error, pattern=None):
        message = "executed transaction"
        false_errors=["Already unlocked", "executed transaction", " version = "]
        if pattern:
            false_errors.append(pattern)

        error_msgs =["assertion failure with message","eosio_assert_message assertion failure",
                     "Failed with error", "Exception"]
        for line in output.split("\n") + error.split("\n"):
            for ferr in false_errors:
                if ferr in line:
                    break
            for err in error_msgs:
                if err in line:
                    message=err
                    if ' version = ' in line:
                        message=line.split('=')[-1].strip()

        for err in error_msgs:
            if message in err:
                raise RuntimeError(error)
        return message

    def run2(self, cmd):
        status = -1
        proc_output = proc_err = None
        if 'password' in cmd:
            print(f"{caller()}(): {' '.join(cmd.split(' ')[:-1]) + ' *****'}")
        else:
            print(f"{caller()}(): {cmd}")
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
            self.verify(proc_output, proc_err)
            return status, proc_output, proc_err
        except Exception as exp:
            print (str(exp))
            self.log(str(exp))
            ans = input("\nError(s) occured. Do you want to continue (C) or quit (Q) (ENTER to continue)? " or "C")
            if "q" == ans.lower():
                self.log(f"Exiting ...\n")
                print("Exiting ...")
                sys.exit(-1)
            return status, proc_output, proc_err

    def validate_account(self, account):
        result = match(ACCOUNT_PATTERN, account)
        if result:
            self.show(f"{caller()}: Account name valid: {account}")
        else:
            self.show(f"{caller()}: Account name invalid: {account}. Exiting ...")
        assert result, f"Account name invalid: {account}."
        return result

    def check_existing_wallet(self, account):
        exists = False
        checked_files=list()
        for wfile in [f"proton_{account}.psw", f"proton_{account}.wallet"]:
            if path.exists(f"{WALLET_DIR}/{wfile}"):
                exists = True
                checked_files.append(f"{WALLET_DIR}/{wfile}")
        if exists:
            self.show(f"Wallet already present: {account} ({checked_files})")
        return exists

    def create_wallet(self,account):
        if not self.validate_account(account):
            sys.exit(-1)
        cmd=CREATE_WALLET_CMD.replace(ACCOUNT, account)
        return self.run(cmd=cmd)

    def create_key(self, account):
        cmd=CREATE_KEY_CMD.replace(ACCOUNT, account)
        return self.run(cmd=cmd)

    def fetch_pvt_key(self, account, password=None):
        if not password:
            password = self.get_password(account=account)
        cmd=GET_PVTKEYS_CMD.replace(ACCOUNT, account).replace(PASSWORD, password)
        return self.run(cmd)

    def get_password(self, account):
        password=None
        try:
            with open(f"{WALLET_DIR}/proton_{account}.psw") as psw:
                password = psw.readline().strip('\n')
        except Exception as exp:
            print(f"Error: {exp} : Account {account}")
        finally:
            return password

    def unlock(self, account, password=None):
        if not password:
            password = self.get_password(account=account)
        cmd = WALLET_UNLOCK.replace(ACCOUNT, account).replace(PASSWORD, password)
        self.show(f"Unlocking wallet for '{account}'")
        s,o,e = self.run(cmd)
        return s,o,e

    def create_account(self, account):
        if self.check_existing_wallet(account):
            return self
        print(f"{caller()}: Creating account: {account}")
        self.create_wallet(account)
        self.create_key(account)
        self.create_key(account)
        self.show(f"Account created: {account}\nWallet:{WALLET_DIR}/proton_{account}")

    def buy_ram(self, payeraccount, toaccount, currency):
        cmd=BUY_RAM_CMD.replace("PAYER", payeraccount).replace("ACCOUNT", toaccount).replace("CURRENCY", currency)
        return self.run(cmd)

    def faucet_register(self,account):
        self.unlock(account)
        s,o,e = self.fetch_pvt_key(account)
        keys=[]
        for k in o.split("\""):
            if "EOS" in k:
                keys.append(k.strip())
        print(f"{account} : {keys}")
        print (f"Use the above public keys for the account \'{account}\' and register at:\n{CREATE_ACC_FAUCET}\n")
        flag = False
        while (not flag):
            created = input("\nHave you registered with these keys? [yes/No]: ")
            if created.strip().lower() in ['y', 'yes']:
                flag = True
            else:
                print(f"Register on chain -> '{account}' : {keys}")
        self.show(f"Account '{account}' registered at Faucet")
        return self

    def faucet_ram(self, account):
        flag = False
        print(f"Get the currency to buy SYS & RAM Resources for '{account}' from {RAM_RESOURCES_GET}")
        while(not flag):
            ram_flag = input("Have yor purchased the resources? [yes/No] ")
            if ram_flag.strip().lower() in ['y', 'yes']:
                flag = True
        self.log(f"{account} has got resources for contract deployment")
        return self

    def deploy_contract(self, contract, binary_dir):
        self.unlock(contract)
        self.faucet_ram(contract)
        self.buy_ram(contract,contract,XPR_TO_BUY_RAM)
        cmd=f"{proton} set contract {contract} {binary_dir} -p {contract}"
        s,o,e=self.run(cmd)
        if f'account {contract} has insufficient ram' in e:
            print(e)
        return s,o,e

    def create_currency(self, account, currency):
        vals = currency.split(" ")
        assert vals[1] in ["OPTION", "FREEOS", "AIRKEY"], f"Invalid Currency: {vals[1]}"
        self.unlock(account)
        cmd=CREATE_CURRENCY.replace(ACCOUNT, account).replace("CURRENCY", currency)
        return self.run(cmd)

    def issue_currency(self, account, currency, memo):
        vals =currency.split(" ")
        assert vals[1] in ["OPTION", "FREEOS","AIRKEY"], f"Invalid Currency: {vals[1]}"
        self.unlock(account)
        cmd=f"{proton} push action {account} issue '[\"{account}\", \"{currency}\", \"{memo}\"]' -p {account}"
        s,o,e, = self.run(cmd)
        print (s,o,e)
        return (s,o,e)

    def verify_create_currency(self, account, currency):
        vals =currency.split(" ")
        assert vals[1] in ["OPTION", "FREEOS", "AIRKEY"], f"Invalid Currency: {vals[1]}"
        cmd=f"{proton} get table ACCOUNT CURRENCY stat".replace(ACCOUNT, account).replace("CURRENCY", vals[1])
        return self.run(cmd)

    def set_global_params(self):
        for k,v in GLOBAL_PARAMS.items():
            self.set_global_param(k,CONFIG_SC, v)

    def set_global_param(self, parameter, account, flag):
        self.unlock(account)
        cmd=f"{proton} push action {account} paramupsert '[\"global\", \"{parameter}\", \"{flag}\"]' -p {account}"
        return self.run(cmd)

    #Bubble of Change for nearby iterations for start/end times
    def move_to_next_iteration_live(self, target_iter = None, iter_interval = ITERATION_INTERVAL):
        curr_time = datetime.now(timezone.utc)
        prev_iter_end_time = curr_time - timedelta(seconds=1)
        next_start_time=f"{curr_time.replace(microsecond=0).isoformat().split('+')[0]}"
        prev_end_time,next_end_time=self.add_time_to_date(start_time=next_start_time, time_string=iter_interval)

        if target_iter:
            next_iter_num = target_iter
        else:
            self.get_current_iteration()
            next_iter_num = int(self.current_iteration["iteration_number"]) + 1

        self.show(f"{caller()}():Changing the 'Live' iteration #{next_iter_num}: "
                  f"Iteration Starts at: {next_start_time} -> {next_end_time}\n"
                  f"Previous Iteration End time:{prev_end_time}\t{OK_sign}")

        if next_iter_num > 1:
            self.show(f"{caller()}() Calling Reset Previous Iteration #{next_iter_num -1} end time:{prev_end_time}")
            self.log(f"Old Dictionary: Iter #{next_iter_num -1} -> {self.iterations[next_iter_num -1]}")
            self.reset_iteration_time(iter_num=next_iter_num -1,
                                      end_time=prev_iter_end_time.replace(microsecond=0).isoformat().split('+')[0])

        s,e, claim, holding = self.get_iteration_params(next_iter_num)

        self.log(f"Old Dictionary: Iter #{next_iter_num} -> {self.iterations[next_iter_num]}")
        self.log(f"Setting Next Iteration: #{next_iter_num}->"
                 f"[{next_start_time},{next_end_time},{claim},{holding}]")

        return self.update_iteration(iter_num=next_iter_num,
                                     start_time=next_start_time,
                                     end_time=prev_end_time,
                                     claim=claim,
                                     holding=holding)

    def reset_iteration_time(self, iter_num=None, start_time=None, end_time=None):
        self.show(f"{caller()}(): Resetting Iteration :# {iter_num} [{start_time} -> {end_time}]")
        if not (start_time or end_time):
            self.log(f"No date input for changing iteration:{self.current_iteration['iteration_number']} ")
            return

        if not start_time:
            start_time = self.current_iteration["start"]
        if not end_time:
            end_time = self.current_iteration["end"]
        if not iter_num:
            self.get_current_iteration()
            iter_num = int(self.current_iteration["iteration_number"])

        if not iter_num > 0:
            self.show(f"Error : Resetting iteration #{0} not allowed.")
            return

        claim=self.current_iteration["claim_amount"]
        tokens=self.current_iteration["tokens_required"]

        self.show(f"Modifying Previous Iteration :#{iter_num} -> "
                  f"['{start_time}', '{end_time}', {claim}, {tokens}]")
        return self.update_iteration(iter_num=iter_num,
                                     start_time=start_time,
                                     end_time=end_time,
                                     claim=claim,
                                     holding=tokens)

    def update_iteration(self, iter_num, start_time, end_time, claim, holding):
        assert iter_num and start_time and end_time, f"{caller}(): NULL input(s) in updating iteration"

        cmd = UPDATE_ITERATION.replace("ITER", str(iter_num)) \
            .replace("START", start_time).replace("END",end_time) \
            .replace("CLAIM", str(claim)).replace("HOLD", str(holding))
        self.show(f"\n\n******* Updating Iteration #{iter_num} *********\n{cmd}")
        s,o,e = self.run(cmd)

        self.get_current_iteration()
        self.log(f"Updating Iteration dictionary entries for #{iter_num}: "
                 f"{self.iterations[iter_num]} -> '[{start_time},{end_time},{claim},{holding}]'")
        self.iterations[iter_num]=[start_time, end_time,claim, holding]
        self.set_current_exchange_rate(self.get_defined_exchange_rate(iter_num=iter_num))
        return s,o,e

    def set_iteration(self, iter_num):
        start_time, end_time, claim, holding = self.get_iteration_params(iter_num)
        s,o,e = self.update_iteration(iter_num, start_time, end_time, claim, holding)
        if iter_num == 1:
            self.set_current_exchange_rate()
        return s,o,e

    def fetch_configured_iteration(self, iter_num):
        #COMMAND FAILS - DEAD TABLE?
        FETCH_ITER_DETAILS_CMD=f"{proton} push action {CONFIG_SC} getiter '[{iter_num}]' -p {CONFIG_SC}@active"
        print(self.run(FETCH_ITER_DETAILS_CMD))

    def set_all_iterations(self):
        for iter_num in self.iterations:
            self.set_iteration(iter_num=iter_num)

    def get_iteration_params(self, iter_num):
        if not iter_num in self.iterations:
            self.log(f"{caller()}(): Iteration #{iter_num} is not configured. Evaluating for this iteration.")
            if iter_num in ITERATIONS_TOKENS_ISSUED:
                tokens=ITERATIONS_TOKENS_ISSUED.get(iter_num)
            else:
                tokens=ITERATIONS_TOKENS_DEFAULT
            self.iterations[iter_num]=["", "", tokens[0], tokens[1]]
        return self.iterations[iter_num]

    def evaluate_iterations(self, max_iterations = MAX_ITERATIONS):
        self.show(f"{caller()}(): Evaluating Iterations for the possible parameter values.")
        iter_end = START_ITERATION_TIME
        #count = 0
        #self.log(f"Starting with: {iter_end}")
        offset_end = 0
        actual_max_iter_configured = self.get_max_configured_iterations()
        max_iterations = max(max_iterations, actual_max_iter_configured +1)
        self.show(f"Considering iterations for up to: {max_iterations} iterations")

        for iter_num in range(1, max_iterations+1):
            if iter_num in ITERATIONS_TOKENS_ISSUED:
                tokens=ITERATIONS_TOKENS_ISSUED.get(iter_num)
            else:
                tokens=ITERATIONS_TOKENS_DEFAULT
            iter_start = iter_end
            offset_end, iter_end = self.add_time_to_date(iter_start)
            self.iterations[iter_num]=[iter_start, offset_end, tokens[0], tokens[1]]
            self.log(f"After Iteration: {iter_num}: {self.iterations[iter_num]}\n")

        self.log(f"Evaluated Iteration Parameters:\n{json.dumps(self.iterations, indent=4)}")
        return self.iterations

    def show_iterations(self):
        self.show(f"{json.dumps(self.iterations, indent=4)}")

    def add_time_to_date(self, start_time, time_string = ITERATION_INTERVAL):
        delta_time=datetime.strptime(time_string,"%H:%M:%S")
        if type(start_time) is str:
            start_time = datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S")
        end_time = start_time + timedelta(hours=delta_time.hour,
                                          minutes=delta_time.minute,
                                          seconds=delta_time.second -1)
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        next_iter_time=start_time + timedelta(hours=delta_time.hour,
                                              minutes=delta_time.minute,
                                              seconds=delta_time.second)
        self.log(f"Evaluated next iteration time: {start_time} -> {next_iter_time} [Interval: {ITERATION_INTERVAL}]")
        next_iter_time = next_iter_time.strftime("%Y-%m-%dT%H:%M:%S")
        return end_time, next_iter_time

    def get_defined_exchange_rate(self, iter_num):
        if len(exchange_rates) < iter_num +1:
            exchange_value = exchange_rates[-1]
        else:
            exchange_value = exchange_rates[iter_num +1]
        self.show(f"{caller()}(): Iteration #{iter_num}: extracted exchange rate = {exchange_value}")
        return exchange_value

    def set_current_exchange_rate(self, current_rate=EXCHANGE_RATE):
        return self.run(EXCHANGE_CMD.replace("EXCHANGE", f"{current_rate}"))

    def set_target_rate(self, target_rate=TARGET_RATE):
        return self.run(TARGET_RATE_CMD.replace("EXCHANGE", f"{target_rate}"))

    def get_exchange_rate(self):
        cmd=f"{proton} get table {CONFIG_SC} {CONFIG_SC} exchangerate"
        s,o,e=self.run(cmd)
        print(s,o,e)
        return s,o,e

    def get_current_iteration(self):
        self.get_max_configured_iterations()
        out = self.get_version(DIVIDEND_SC)
        current_iteration_num_dividend = int(out.split(' ')[-1])
        self.log(f"Actual current iteration: {current_iteration_num_dividend} [Dividend version: {out}]")
        for iter_val in self.all_iterations["rows"]:
            if iter_val["iteration_number"] == current_iteration_num_dividend:
                self.current_iteration = iter_val
                self.show(f"Currently active iteration: {self.current_iteration}")
        if "iteration_number" in self.current_iteration:
            return self.current_iteration["iteration_number"]
        return current_iteration_num_dividend

    def get_max_configured_iterations(self):
        s, o, e = self.run(GET_ALL_ITERATIONS_CMD)
        self.log(f"Get current iteration: {GET_ALL_ITERATIONS_CMD}: {s}:{o} {e}")
        self.all_iterations = json.loads(o)
        end_iteration = self.all_iterations["rows"][-1]
        self.show(f"Max Iterations Setup in network: {end_iteration}")
        return end_iteration["iteration_number"]

    def update_stake_requirements(self):
        for stake in STAKE_UPSERT_LIST:
            cmd=STAKE_UPSERT.replace("STAKE", str(stake))
            print(f"Stake: {cmd}")
            s,o,e = self.run(cmd)
            print(f"Added: {s}{o}{e}")
        return self

    def set_permission_transfer_token(self):
        for account in [AIRCLAIM_SC, DIVIDEND_SC]:
            cmd=TRANSFER_TOKEN_PERM_CMD.replace("TO_ACCOUNT", account)
            s,o,e=self.run(cmd)
            self.log(f"{s}{o}{e}")
        return self

    def read_permission_transfer_token(self):
        cmd=f"{proton} get table {CONFIG_SC} {CONFIG_SC} transferers"
        return self.run(cmd)

    def read_statistics_table(self):
        cmd=f"{proton} get table {AIRCLAIM_SC} {AIRCLAIM_SC} statistics"
        return self.run(cmd)

    def get_version(self, account):
        version=None
        self.unlock(account)
        cmd=f"{proton} push action {account} version '[]' -p {account}@active"
        s,o,e=self.run(cmd)
        for line in e.split('\n')+o.split('\n'):
            if 'ersion =' in line:
                version=line.split("=")[-1].strip()
        self.show(f"Contract: '{account} is deployed with version: {version}'")
        return version

def populate_users(users_file):
    all_users = dict()
    with open(users_file) as usf:
        for val in usf.readlines():
            vals = val.split(",")
            psw=None
            if len(vals) == 3:
                user, utype, psw = vals
            else:
                user, utype = vals
            #print (f"{utype}, {user}, {psw}")
            user=user.strip()
            psw=psw.strip()
            utype=utype.strip()
            all_users[user]=User(account=user, password=psw,user_type=utype)
    print(f"Total Participating Users [Count={len(all_users)}]: \n{all_users.keys()}")
    return all_users

def options():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"shDIVv",
                                   ["help","iteration","deployment","validate","version","simulation"])
    except getopt.GetoptError as err:
        print("Errr: ", repr(err))
        sys.exit(2)
    iteration=deployment=validate=version=simulation=None
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print (f"Usage:\n\npython3 {sys.argv[0]}\n"
                   f"\t[-s | --simulation]\n"
                   f"\t[-I | --iteration]\n"
                   f"\t[-D | --deployment]\n"
                   f"\t[-V | --validate ]\n"
                   f"\t[-v | --version]\n"
                   f"\t[-h | --help]\n")
            sys.exit(0)
        elif opt in ["-I", "--iteration"]:
            iteration = True
        elif opt in ["-V", "--validate"]:
            validate = True
        elif opt in ["-v", "--version"]:
            version=True
        elif opt in ["-D", "--deployment"]:
            deployment=True
        elif opt in ["-s", "--simulation"]:
            simulation=True
    if not (iteration or deployment or validate or version or simulation):
        print(f"Please run the script with -h flag for required flags."
              f"\nThe Program will parse and exit.")
    return (iteration, deployment, validate, version, simulation)

def simulate_airclaim():
    iteration, deployment, validate, version, simulation = options()
    target_contracts=[AIRCLAIM_SC, CONFIG_SC, CURRENCY_SC, DIVIDEND_SC]
    freeos = FreeOsContract()

    #Deployment Section
    if (deployment):
        print("Deployment started!")
        for account in target_contracts:
            freeos.create_account(account)

        for account in target_contracts:
            freeos.faucet_register(account)

        for account in target_contracts:
            freeos.deploy_contract(account,f"{BINARY_DIR}/{abi_map.get(account)}")

        #Configuration Section
        freeos.create_currency(AIRCLAIM_SC, CURRENCY_OPTION_VAL)
        freeos.verify_create_currency(AIRCLAIM_SC,CURRENCY_OPTION_VAL)

        freeos.create_currency(AIRCLAIM_SC, CURRENCY_AIRKEY_VAL)
        freeos.issue_currency(AIRCLAIM_SC, "1000 AIRKEY", "First issue")
        freeos.verify_create_currency(AIRCLAIM_SC,CURRENCY_AIRKEY_VAL)

        freeos.create_currency(AIRCLAIM_SC,CURRENCY_FREEOS_VAL)
        freeos.verify_create_currency(AIRCLAIM_SC,CURRENCY_FREEOS_VAL)

    #Iterations Section
    if (iteration):
        print("Updating Iterations")
        freeos.show_iterations()
        freeos.set_global_params()
        freeos.set_all_iterations()
        freeos.update_stake_requirements()
        freeos.set_current_exchange_rate()
        freeos.set_target_rate()
        freeos.get_exchange_rate()
        freeos.set_permission_transfer_token()

    if (validate):
        print("Validating the current state")
        freeos.show_iterations()
        freeos.get_exchange_rate()
        freeos.read_permission_transfer_token()
        freeos.read_statistics_table()

    if (version):
        print ("Checking version of contracts")
        for account in target_contracts:
            freeos.get_version(account)

    if (simulation):
        print(f"Executing user actions in the field")
        freeos.show(f"FreeOS Simulation Started!")
        freeos.unlock(CONFIG_SC)
        freeos.unlock(AIRCLAIM_SC)

        freeos.set_iteration(iter_num=1)
        freeos.move_to_next_iteration_live(target_iter=1)
        print(freeos.current_iteration)

        users_list = populate_users(users_file=USERS_FILE)
        while True:
            for user in users_list:
                active_user=users_list[user]
                freeos.show(f"User '{active_user}' is executing actions")
                active_user.reguser()
                active_user.stake()
                active_user.claim()
            freeos.move_to_next_iteration_live()

if __name__=='__main__':
    simulate_airclaim()