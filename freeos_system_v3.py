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
START_ITERATION_TIME = "2021-05-28T03:00:00" #This time is in UTC. Offset properly from local time zone
ITERATION_INTERVAL = "03:00:00"
MAX_ITERATIONS = 7
EXCHANGE_RATE = "0.00053"
TARGET_RATE = "0.0167"
AUTO_PILOT_MODE=False

# Project Settings
USERS_FILE = "registered_users.csv"
WALLET_DIR = f"{Path.home()}/eosio-wallet"
ACC_PASSWORD_FILE=f"{WALLET_DIR}/proton_ACCOUNT.psw"
BINARY_DIR = f"{WALLET_DIR}/eos-binaries"
LOG_FILE = f"eos-deployment-{datetime.now().strftime('%b%d_%H')}.log" #%H%M%S
END_POINT = "https://protontestnet.greymass.com"
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

# Commands - DO NOT Edit unless command itself has changed
ACCOUNT = "ACCOUNT"
PASSWORD = "PASSWORD"
proton = f"/usr/local/bin/cleos -u {END_POINT}"
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
STAKED_USER_COUNT_CMD=f"{proton} get scope {AIRCLAIM_SC}  -t users --limit 4999| grep 'scope'"
OPTIONS_VESTED_CMD=f"{proton} get table {AIRCLAIM_SC} ACCOUNT VEST_PARAM"
REGUSER_CMD=f"{proton} push action {AIRCLAIM_SC} reguser '[\"ACCOUNT\"]' -p ACCOUNT@active"
USER_INFO_CMD=f"{proton}  get table {CONFIG_SC} {CONFIG_SC} usersinfo --limit 99999"
READ_GLOBAL_TABLE_CMD=f"{proton} get table {CONFIG_SC} {CONFIG_SC} parameters"

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
        self.set_dir()
        update_stake_list()

    def set_dir(self):
        chdir(WALLET_DIR)
        self.log(f"Script Started!\nChanged Dir to: {getcwd()}")

    def log(self, message):
        with open(f"{Path.home()}/{LOG_FILE}", "a") as dfl:
            dfl.writelines(f"\n{datetime.now()} - {message}")

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
        ignore_list=['Wallet is already unlocked']
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
                self.log(f"Exiting ...\n")
                print("Exiting ...")
                sys.exit(-1)
            return status, proc_output, proc_err

class User(object):
    def __init__(self, account=None, password=None, user_type='e'):
        self.account = account
        self.password = password
        self.user_type = user_type

        self.user_registration_info=dict()
        self.current_iteration = 0
        self.currencies = dict()

        self.executor=Executor()
        self.log=self.executor.log
        self.show=self.executor.show
        self.run=self.executor.run
        self.locate_message_in_output=self.executor.locate_message_in_output

        self.load_password()
        self.unlock_wallet()

    def __repr__(self):
        return f"{self.account} [{self.user_type}]"

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
        self.show(f"{s},{o},{e}")

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

    def fetch_user_registration_info(self):
        cmd=USER_INFO_CMD
        s,o,e=self.run(cmd)
        users = json.loads(o)["rows"]
        for user in users:
            if self.account == user.get("acc"):
                self.user_registration_info=dict(user)

    def is_registered(self):
        if self.user_registration_info:
            return True
        return False


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
            self.show(f"{repr(exp)}: Could not read stake requirements.")
        finally:
            return req

    def count_user_staked(self):
        cmd=STAKED_USER_COUNT_CMD
        s,o,e = self.run(cmd)
        num_users = len(o.split('\n'))
        self.show(f"Total number of users staked = {num_users}")
        return num_users

    def stake(self, currency = "XPR"):
        total_staked=self.count_user_staked()
        self.show(f"Count of users already staked = {total_staked} [Current Iteration = #{self.get_live_iteration()}]")
        stake_currency_required_val=self.get_planned_stake_req(total_staked +1,self.user_type)
            #f"{self.get_planned_stake_req(total_staked +1,self.user_type)}.0000 {currency}"
        self.show(f"Stake Requirement for: '{self.account}' = {stake_currency_required_val}.0000 {currency} "
                  f"[user type = {self.user_type}, "
                  f"Already staked users: #{total_staked}, "
                  f"Current Iteration: #{self.get_live_iteration()}]")
        #stake_currency_required_val, unit=stake_currency_required.split(' ')
        stake_currency_actual_val=self.get_currency_balance(currency=currency)
        #stake_currency_actual_val=stake_currency_actual

        if float(stake_currency_required_val) > float(stake_currency_actual_val):
            message = f"Error: Possibly Insufficient Fund for Staking required: " \
                      f"{stake_currency_actual_val} vs the required {stake_currency_required_val} {currency}"
            self.show(message)

        cmd=USER_STAKE_CMD.replace("ACCOUNT", self.account). \
            replace("STAKE", f"{stake_currency_required_val}.0000 {currency}")
        s,o,e = self.run(cmd)
        print(s,o,e)
        return s,o,e



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

    def cancel_unstake(self):
        cmd=f"{proton} push action freeosd unstakecncl '[\"{self.account}\"]' -p {self.account}"
        return self.run(cmd)

    def reverify(self):
        cmd=f"{proton} push action {AIRCLAIM_SC} reverify '[\"{self.account}\"]' -p {self.account}"
        return self.run(cmd)

    def unvest(self):
        cmd=f"{proton} push action {AIRCLAIM_SC} unvest '[\"{self.account}\"]' -p {self.account}"
        return self.run(cmd)

    def is_unvested(self, iter):
        pass

    def setup_cron(self):
        SETUP_CRON_CMD=f"{proton} push transaction HELP NEEDED"

    def cron_tick(self):
        self.unlock_wallet()
        CRON_TICK_CMD=f"{proton} push action cron process '[\"ACCOUNT\", \"5\"]' -p ACCOUNT"
        cmd = CRON_TICK_CMD.replace(ACCOUNT, self.account)
        return self.run(cmd)

    def claim(self):
        CLAIM_CMD=f"{proton} push action {AIRCLAIM_SC} claim '[\"ACCOUNT\"]' -p ACCOUNT@active"
        cmd=CLAIM_CMD.replace(ACCOUNT, self.account)
        s,o,e =  self.run(cmd)
        self.show(f"{caller()}(): {s}:{o}:{e}")
        return s,o,e

    def get_options_vested(self):
        cmd=OPTIONS_VESTED_CMD.replace(ACCOUNT, self.account).replace('VEST_PARAM','vestaccounts')
        s,o,e = self.run(cmd)
        self.log(f"{caller()}(): {s}:{o}:{e}")
        value=0
        try:
            value = json.loads(o)["rows"][-1]["balance"]
        except Exception as exp:
            print(f"{caller()}: {o}")
        self.show(f"{caller()}(): Vested OPTION(s) ={value}")
        return value

    def get_options_account(self):
        cmd=OPTIONS_VESTED_CMD.replace(ACCOUNT, self.account).replace('VEST_PARAM','accounts')
        s,o,e = self.run(cmd)
        self.log(f"{caller()}(): {s}:{o}:{e}")
        value=0
        try:
            value = json.loads(o)["rows"][-1]["balance"]
        except Exception as exp:
            print(f"{caller()}: {o}")

        # value = json.loads(o)["rows"][-1]["balance"]
        self.show(f"{caller()}(): Liquid OPTION(s) ={value}")
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
        self.global_params=dict()

        self.claimed_users_count=0
        self.claim_events=0
        self.unvest_percent=0
        self.unvest_percent_iteration=0
        self.failsafe_counter=0

        self.current_freeos_rate = 0
        self.target_freeos_rate = TARGET_RATE

        self.executor=Executor()
        self.run=self.executor.run
        self.log=self.executor.log
        self.show=self.executor.show
        self.locate_message_in_output=self.executor.locate_message_in_output
        self.failsafe_history=list()
        self.initialise()

    def initialise(self):
        self.prompt()
        self.evaluate_iterations()
        self.get_exchange_rate()
        self.get_current_iteration()
        self.load_virtual_global_params()

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
                f"\tDefault Vesting Percent = {GLOBAL_PARAMS['vestpercent']}\n" \
                f"\tAuto Pilot Mode = {['OFF','ON'][bool(AUTO_PILOT_MODE)]}"
        print(message)
        confirm = input("Are these configurations correct? [Y/n]: ") or "y"
        if 'y' != confirm.lower():
            print("\nPlease update the configurations and run with flag options (provide -h for more options)."
                  "\nExiting ...\n")
            sys.exit(0)

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

    def validate_account_pattern(self, account):
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
        if not self.validate_account_pattern(account):
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
        self.show(f"{caller()}: Creating account: {account}")
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

    def load_virtual_global_params(self):
        s,o,e = self.run(READ_GLOBAL_TABLE_CMD)
        self.show(f"Global Params:{o}{e}")
        if 'rows' in json.loads(o):
            vals = json.loads(o)["rows"]
            for val in vals:
                paramname=val["paramname"]
                value=val["value"]
                self.global_params[paramname]=value
        else:
            self.show(f"Could not fetch the Global Parameters")

    def set_global_params(self):
        for k,v in GLOBAL_PARAMS.items():
            self.set_global_param(k,CONFIG_SC, v)

    def verify_global_params(self):
        self.load_virtual_global_params()
        self.log(f"Config:{GLOBAL_PARAMS}\nFetched from Network:{self.global_params}")
        for k,v in self.global_params.items():
            assert v==GLOBAL_PARAMS[k], f"Global Param not set properly:{k} vs {GLOBAL_PARAMS[k]}"
        self.show(f"Global parameters are configured correctly.")
        return True

    def set_global_param(self, parameter, account, flag):
        self.unlock(account)
        cmd=f"{proton} push action {account} paramupsert '[\"global\", \"{parameter}\", \"{flag}\"]' -p {account}"
        return self.run(cmd)

    #Bubble of Change for nearby iterations for start/end times
    def move_to_next_iteration_live(self, target_iter = None,
                                    iter_interval = ITERATION_INTERVAL):
        if target_iter:
            next_iter_num = target_iter
        else:
            self.get_current_iteration()
            next_iter_num = int(self.current_iteration["iteration_number"]) + 1

        if not AUTO_PILOT_MODE:
            while (input(f"Ready to configure next iteration #{next_iter_num}? [y/N]").lower() not in ['y', 'yes']):
                time.sleep(2)

        curr_time = datetime.now(timezone.utc)
        prev_iter_end_time = curr_time - timedelta(seconds=1)
        next_start_time=f"{curr_time.replace(microsecond=0).isoformat().split('+')[0]}"
        prev_end_time,next_end_time=self.add_time_to_date(start_time=next_start_time, time_string=iter_interval)

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
        self.set_current_exchange_rate(self.get_defined_exchange_rate_for_next_iter(iter_num=iter_num))
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
        self.show(f"Initially 'planned' iterations:\n{json.dumps(self.iterations, indent=4)}")

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

    def get_defined_exchange_rate_for_next_iter(self, iter_num):
        if len(exchange_rates) < iter_num +1:
            exchange_value = exchange_rates[-1]
        else:
            exchange_value = exchange_rates[iter_num +1]
        self.show(f"{caller()}(): Iteration #{iter_num}: extracted exchange rate = {exchange_value}")
        return exchange_value

    def set_current_exchange_rate(self, current_rate=EXCHANGE_RATE):
        self.unlock(CONFIG_SC)
        return self.run(EXCHANGE_CMD.replace("EXCHANGE", f"{current_rate}"))

    def set_target_rate(self, target_rate=TARGET_RATE):
        self.unlock(CONFIG_SC)
        return self.run(TARGET_RATE_CMD.replace("EXCHANGE", f"{target_rate}"))

    def get_exchange_rate(self):
        cmd=f"{proton} get table {CONFIG_SC} {CONFIG_SC} exchangerate"
        s,o,e=self.run(cmd)
        try:
            rates = (json.loads(o))["rows"][0]
            self.current_freeos_rate = float(rates["currentprice"])
            self.target_freeos_rate = float(rates["targetprice"])
        except Exception as exp:
            self.show(f"{caller}(): {repr(exp)}\nCould not fetch the currency and exchange rates [{s}]{o}:Error {e}")
        finally:
            return s,o,e

    def get_current_iteration(self):
        self.get_max_configured_iterations()
        out = self.get_version(DIVIDEND_SC)
        current_iteration_num_dividend = int(out.split(' ')[-1])
        self.log(f"Actual current iteration: {current_iteration_num_dividend} [Dividend version: {out}]")
        if current_iteration_num_dividend == 0:
            self.show(f"No iteration is currently active.")
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
        self.show(f"Max Iterations Setup in network:\n{json.dumps(end_iteration, indent=4)}")
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
        s,o,e = self.run(cmd)
        stats=dict()
        try:
            stats = json.loads(o)["rows"][0]

            self.claimed_users_count=int(stats["usercount"])
            self.claim_events=int(stats["claimevents"])
            self.unvest_percent=int(stats["unvestpercent"])
            self.unvest_percent_iteration=int(stats["unvestpercentiteration"])
            self.failsafe_counter=int(stats["failsafecounter"])

            self.log(f"Counters Fetched: {o}")
        except Exception as exp:
            self.show(f"{caller()}(): Could not read the statistics : {o}{e}")
        finally:
            return stats


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

    def is_good_time(self):
        self.get_exchange_rate()
        flag = not (self.current_freeos_rate < float(TARGET_RATE))
        self.log(f"Good Time = {flag} :: Current Rate:{self.current_freeos_rate} vs Floor Rate: {TARGET_RATE}")
        return flag

    def fetch_liquid_vest_unvest_allocation_rate(self):
        vest_rate = unvest_rate = 0.00
        self.read_statistics_table()

        if self.is_good_time():
            liquid_rate = 1.00
            if self.unvest_percent > 13:
                unvest_rate = 0.21
            else:
                unvest_fib = [1,2,3,5,8,13,21]
                unvest_rate = 0.01 * unvest_fib[
                    unvest_fib.index(self.unvest_percent) +1]
        else:
            if self.failsafe_counter == 0:
                if self.unvest_percent == 0:
                    unvest_rate = 0.15
            vest_rate = 1.0 - (1.0 * self.current_freeos_rate)/float(TARGET_RATE)
            if vest_rate >0.90:
                vest_rate=0.90
            liquid_rate=1.00 - vest_rate

        liquid_rate = float("{:.4f}".format(liquid_rate))
        vest_rate = float("{:.4f}".format(vest_rate))
        unvest_rate = float("{:.4f}".format(unvest_rate))

        self.show(f"Vest Stats :: Good Time = {self.is_good_time()}, Liquid = {liquid_rate}, "
                  f"Vested = {vest_rate}, Unvested = {unvest_rate}")
        return liquid_rate, vest_rate, unvest_rate

def populate_users(users_file):
    all_users = dict()
    with open(f"{WALLET_DIR}/{users_file}") as usf:
        for val in usf.readlines():
            vals = val.split(",")
            if len(vals) == 3:
                user, utype, psw = vals
            else:
                user, utype = vals
                psw=None
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
        print("****** Validating the current state ******")
        freeos.show_iterations()
        freeos.get_exchange_rate()
        freeos.read_permission_transfer_token()
        freeos.read_statistics_table()
        freeos.verify_global_params()

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
                freeos.show(f"User: '{active_user}' is executing actions")
                active_user.reguser()
                active_user.stake()
                active_user.claim()
            freeos.move_to_next_iteration_live()
def save_log(fd,message):
    message=f"{datetime.now()} - {message.strip()}\n"
    return fd.write(message)

def user_claim_simulation():
    START_ITER_NUM=24
    log_file=f"vest.log"
    vfd=open(log_file, "a")
    save_log(vfd, f"\n")
    current_rates=[0.011, 0.0018, 0.0167,
                   0.21, 0.22, 0.202, 1.019, 10.5, 1110.01, 977.01, 0.003,
                   0.001, 0, 0.0009, 0.0081,
                   0.21, 0.00167, 0.016666666, 20.01,
                   0.0013, 0, 0.0029, 0.0081,0.0001, 0, 0.0009, 0.0081,0.0091, 0.0009, 0.00081]
    print(f"Logs: {log_file}, Users:{USERS_FILE}")
    save_log(vfd, f"Logs: {log_file}, Users:{USERS_FILE}")
    users_list = populate_users(users_file=USERS_FILE)
    participating_users=[]

    freeos = FreeOsContract()
    freeos.show(f"Freeos Vest & Unvest Simulation Started!")
    freeos.unlock(CONFIG_SC)
    freeos.unlock(AIRCLAIM_SC)
    freeos.set_iteration(iter_num=START_ITER_NUM)
    freeos.move_to_next_iteration_live(target_iter=START_ITER_NUM)

    for user in users_list:
        active_user=users_list[user]
        save_log(vfd, f"Skipping ******* User: '{active_user}' is executing actions\n")
        participating_users.append(active_user)
        active_user.reverify()
        active_user.reguser()
        active_user.stake()
        active_user.cancel_unstake()

    freeos.show( f"Users and Iteration Initialisation DONE")
    input("READY FOR ACTUAL EVALUATION? ")

    for i in range( len(current_rates)):
        good_time=bool(1.0*current_rates[i]/float(TARGET_RATE) >=1)
        iter_num=START_ITER_NUM+i
        freeos.show( f"Iter[{iter_num}] -(logically) Is GoodTime={good_time}: Rate={current_rates[i]},")
        freeos.unlock(CONFIG_SC)
        freeos.unlock(AIRCLAIM_SC)
        freeos.move_to_next_iteration_live(target_iter=iter_num)
        freeos.set_current_exchange_rate(current_rate=f"{current_rates[i]}")
        freeos.get_exchange_rate()
        stats = freeos.read_statistics_table()
        freeos.show( f"[Iter #{iter_num}] Stats read: {stats}")

        liquid_rate, vest_rate, unvest_rate = freeos.fetch_liquid_vest_unvest_allocation_rate()
        freeos.show(f"[Iter #{iter_num}] Rates: (Live) Liquid={liquid_rate}, Vest={vest_rate}, Unvest{unvest_rate}")

        for auser in participating_users:
            auser.unlock_wallet()
            freeos.show(f"[Iter #{iter_num}] Proceesing for user: {auser}")
            vested=auser.get_options_vested()
            liquid=auser.get_options_account()
            freeos.show(f"{auser.account}: Before claim: vested={vested}, liquid={liquid}")
            s,o,e=auser.claim()
            freeos.show( f"{auser.account}: Claimed:{s},{o},{e}")
            s,o,e=auser.claim()
            freeos.show(f"{auser.account}: ReClaimed:{s},{o},{e}")
            vested=auser.get_options_vested()
            liquid=auser.get_options_account()
            freeos.show(f"{auser.account}: After claim: vested={vested}, liquid={liquid}")
            s,o,e=auser.unvest()
            freeos.show(f"{auser.account}: Unvest:{s},{o},{e}")
            s,o,e=auser.unvest()
            freeos.show( f"{auser.account}: Second Unvest:{s},{o},{e}")
            vested=auser.get_options_vested()
            liquid=auser.get_options_account()
            freeos.show(f"{auser.account}: After unvest(), vested={vested}, liquid={liquid}")

        #message=f"Iter:{iter_num}- Evaluated:{liquid_rate}, {vest_rate}, {unvest_rate}"

    # freeos = FreeOsContract()
    # freeos.show(f"Freeos Vest & Unvest Simulation Started!")
    # freeos.unlock(CONFIG_SC)
    # freeos.unlock(AIRCLAIM_SC)
    #
    # freeos.set_iteration(iter_num=START_ITER_NUM)
    # freeos.move_to_next_iteration_live(target_iter=1)
    # #freeos.get_exchange_rate()
    # #freeos.read_statistics_table()
    # #freeos.set_current_exchange_rate(current_rate="0.00001")
    # liquid_rate, vest_rate, unvest_rate = freeos.fetch_liquid_vest_unvest_allocation_rate()


if __name__=='__main__':
    #simulate_airclaim()
    user_claim_simulation()
    print("Execution complete")