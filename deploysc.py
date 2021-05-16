#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__author__ = "Mohammad Shahid Siddiqui"
__license__ = "GPL"
__version__ = "1.0.2"
__email__ = "mssiddiqui.nz@gmail.com"
__status__ = "Test"
__copyright__ = "(c) 2021"
__date__ = "16 May 2021"
"""

import json
import sys
import getopt
import inspect
from argparse import ArgumentParser
from subprocess import PIPE, Popen
from os import chdir, getcwd, path
from datetime import datetime, time, timedelta
from pathlib import Path
from re import match

#Iterations
START_ITERATION_TIME="2021-05-17T01:00:00"
ITERATION_INTERVAL="00:15:00"
MAX_ITERATIONS=8
EXCHANGE_RATE="0.00053"
TARGET_RATE="0.0167"

#Contracts
AIRCLAIM_SC="freeos2"
CONFIG_SC="freeoscfg2"
DIVIDEND_SC="optionsdiv2"
CURRENCY_SC="freeostoken2"

#Global Settings
WALLET_DIR = f"{Path.home()}/eosio-wallet"
BINARY_DIR=f"{Path.home()}/eos-binaries"
LOG_FILE="eos-deployment.log"
END_POINT="https://protontestnet.greymass.com"
CREATE_ACC_FAUCET="https://monitor.testnet.protonchain.com/#account"
RAM_RESOURCES_GET="https://monitor.testnet.protonchain.com/#faucet"

proton=f"/usr/local/bin/cleos -u {END_POINT}"
CURRENCY_OPTION_VAL="350000000000000.0000 OPTION"
CURRENCY_AIRKEY_VAL="1000000 AIRKEY"
CURRENCY_FREEOS_VAL="350000000000000.0000 FREEOS"
XPR_TO_BUY_RAM="25000.0000 XPR"

#Commands - DO NOT Edit
ACCOUNT="ACCOUNT"
PASSWORD="PASSWORD"
ACCOUNT_PATTERN="(^[a-z1-5.]{2,11}[a-z1-5]$)|(^[a-z1-5.]{12}[a-j1-5]$)"
CREATE_WALLET_CMD=f"{proton} wallet create -n proton_ACCOUNT --file {WALLET_DIR}/proton_ACCOUNT.psw"
CREATE_KEY_CMD=f"{proton} wallet create_key -n proton_ACCOUNT"
GET_PVTKEYS_CMD=f"{proton} wallet private_keys -n proton_ACCOUNT --password PASSWORD"
WALLET_UNLOCK=f"{proton} wallet unlock -n proton_ACCOUNT --password PASSWORD"
WALLET_LOCK=f"{proton} wallet lock -n proton_ACCOUNT"
DEPLOY_CONTRACT=f"{proton} set contract ACCOUNT {BINARY_DIR}/SC_DIR -p ACCOUNT"
CREATE_CURRENCY=f"{proton} push action ACCOUNT create '[\"ACCOUNT\", \"CURRENCY\"]' -p ACCOUNT"
BUY_RAM_CMD=f"{proton} push action eosio buyram '[\"PAYER\", \"ACCOUNT\", \"CURRENCY\"]' -p PAYER"
GET_ALL_ITERATIONS_CMD=f"{proton} get table {CONFIG_SC} {CONFIG_SC} iterations --limit 1000"
TRANSFER_TOKEN_PERM_CMD=f"{proton} push action {CONFIG_SC} transfadd '[\"TO_ACCOUNT\"]' -p {CONFIG_SC}"
EXCHANGE_CMD=f"{proton} push action {CONFIG_SC} currentrate '[EXCHANGE]' -p {CONFIG_SC}@active"
TARGET_RATE_CMD=f"{proton} push action {CONFIG_SC} targetrate '[EXCHANGE]' -p {CONFIG_SC}@active"
UPDATE_ITERATION=f"{proton} push action {CONFIG_SC} iterupsert '[ITER, \"START\", \"END\", CLAIM, HOLD]' -p {CONFIG_SC}"
STAKE_UPSERT=f"{proton} push action {CONFIG_SC} stakeupsert 'STAKE' -p {CONFIG_SC}@active"

GLOBAL_PARAMS={
    "masterswitch" : "1",
    "failsafefreq" : "5",
    "altverifyacc" : CONFIG_SC,
    "unstakesnum" : "4",
    "vestpercent" : "50"
}
STAKE_UPSERT_LIST=[[0,0,0,0,0,10,0,0,0,0,0],
                   [5,0,0,0,10,20,0,0,0,0,0],
                   [10,0,0,0,20,30,0,0,0,0,0],
                   [20,0,0,0,30,50,0,10,0,0,0],
                   [30,0,0,0,50,80,0,20,0,0,0],
                   [40,0,0,0,80,130,0,30,0,0,0],
                   [50,0,0,0,130,210,0,50,0,0,0],
                   [60,0,0,0,210,340,0,80,0,0,0],
                   [70,0,0,0,340,550,0,130,0,0,0],
                   [80,0,0,0,550,890,0,210,0,0,0],
                   [90,0,0,0,890,1440,0,340,0,0,0],
                   [100,0,0,0,1440,2330,0,550,0,0,0]]
ITERATIONS_TOKENS_ISSUED={1: [100,0],
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
ITERATIONS_TOKENS_DEFAULT=ITERATIONS_TOKENS_ISSUED[25]
abi_map = {AIRCLAIM_SC:"freeos",
        CONFIG_SC:"freeosconfig",
        CURRENCY_SC:"eosio.token",
        DIVIDEND_SC:"dividenda"}

caller = lambda: inspect.stack()[2][3]

class DeployContract(object):
    def __init__(self,
                 airclaim_contract=None,
                 config_contract=None,
                 currency_contract=None,
                 dividend_contract=None):

        self.airclaimsc=airclaim_contract
        self.configsc=config_contract
        self.currencysc=currency_contract
        self.dividendsc=dividend_contract

        self.iterations=dict()
        self.set_dir()
        self.prompt()
        self.evaluate_iterations()

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
            print("\nPlease update the configurations.\nExiting ...\n")
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
        return self.run(cmd)

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
            created = input("\nHave you registered with these keys? [yes/No] ")
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

    def update_iteration(self, num, start_time, end_time, claim, holding):
        cmd = UPDATE_ITERATION.replace("ITER", str(num))\
            .replace("START", start_time).replace("END",end_time)\
            .replace("CLAIM", str(claim)).replace("HOLD", str(holding))
        self.log(f"Updating Iteration #{num}:\n{cmd}")
        return self.run(cmd)

    def set_iteration(self, iter_num):
        start_time, end_time, claim, holding = self.get_iteration_params(iter_num)
        return self.update_iteration(iter_num, start_time, end_time, claim, holding)

    def set_all_iterations(self):
        for iter_num in self.iterations:
            self.set_iteration(iter_num=iter_num)

    def get_iteration_params(self, num):
        return self.iterations[num]

    def evaluate_iterations(self):
        iter_start=iter_end=START_ITERATION_TIME
        count = 0
        self.log(f"Starting with: {iter_end}")
        offset_end = 0
        for iter_num in range(1,MAX_ITERATIONS+1):
            if iter_num in ITERATIONS_TOKENS_ISSUED:
                tokens=ITERATIONS_TOKENS_ISSUED.get(iter_num)
            else:
                tokens=ITERATIONS_TOKENS_DEFAULT
            iter_start = iter_end
            offset_end, iter_end = self.add_time_to_date(iter_start)
            self.iterations[iter_num]=[iter_start, offset_end, tokens[0], tokens[1]]
            self.log(f"After Iteration: {iter_num}: {self.iterations[iter_num]}\n")
        self.log(f"{json.dumps(self.iterations, indent=4)}")
        return self

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
        self.log(f"Evaluated next iteration time: {next_iter_time} [Interval: {ITERATION_INTERVAL}]")
        next_iter_time = next_iter_time.strftime("%Y-%m-%dT%H:%M:%S")
        return end_time, next_iter_time

    def set_current_exchange_rate(self, current_rate=EXCHANGE_RATE):
        return self.run(EXCHANGE_CMD.replace("EXCHANGE", current_rate))

    def set_target_rate(self, target_rate=TARGET_RATE):
        return self.run(TARGET_RATE_CMD.replace("EXCHANGE", target_rate))

    def get_exchange_rate(self):
        cmd=f"{proton} get table {CONFIG_SC} {CONFIG_SC} exchangerate"
        s,o,e=self.run(cmd)
        print(s,o,e)
        return s,o,e

    def get_current_iteration(self):
        s, o, e = self.run(GET_ALL_ITERATIONS_CMD)
        self.log(f"Get current iteration: {GET_ALL_ITERATIONS_CMD}: {s}:{o} {e}")
        stats = json.loads(o)
        self.current_iteration = int(stats["rows"][-1]["iteration_number"])
        self.log(f"Current Iteration: {self.current_iteration}")
        return self.current_iteration

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
            if 'version =' in line:
                version=line.split("=")[-1].strip()
        self.show(f"Contract: '{account} is deployed with version: {version}'")
        return version


def options():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"FhDIVv",
                                   ["help","iteration","deployment","validate","version","field"])
    except getopt.GetoptError as err:
        print("Errr: ", repr(err))
        sys.exit(2)
    iteration=deployment=validate=version=field=None
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print (f"Usage:\n\npython3 {sys.argv[0]} "
                   f"[-F | --field] "
                   f"[-I | --iteration] "
                   f"[-D | --deployment ] "
                   f"[-V | --validate ] "
                   f"[-v | --version] "
                   f"[-h | --help]\n")
            sys.exit(0)
        elif opt in ["-I", "--iteration"]:
            iteration = True
        elif opt in ["-V", "--validate"]:
            validate = True
        elif opt in ["-v", "--version"]:
            version=True
        elif opt in ["-D", "--deployment"]:
            deployment=True
        elif opt in ["-F", "--field"]:
            field=True
    return (iteration, deployment, validate, version, field)


def deploy_airclaim():
    iteration, deployment, validate, version, field = options()
    target_contracts=[AIRCLAIM_SC, CONFIG_SC, CURRENCY_SC, DIVIDEND_SC]
    deploySC=DeployContract()

    #Deployment Section
    if(deployment):
        print("Deployment started!")
        for account in target_contracts:
            deploySC.create_account(account)

        for account in target_contracts:
            deploySC.faucet_register(account)

        for account in target_contracts:
            deploySC.deploy_contract(account,f"{BINARY_DIR}/{abi_map.get(account)}")

        #Configuration Section
        deploySC.create_currency(AIRCLAIM_SC, CURRENCY_OPTION_VAL)
        deploySC.verify_create_currency(AIRCLAIM_SC,CURRENCY_OPTION_VAL)

        deploySC.create_currency(AIRCLAIM_SC, CURRENCY_AIRKEY_VAL)
        deploySC.issue_currency(AIRCLAIM_SC, "1000 AIRKEY", "First issue")
        deploySC.verify_create_currency(AIRCLAIM_SC,CURRENCY_AIRKEY_VAL)

        deploySC.create_currency(AIRCLAIM_SC,CURRENCY_FREEOS_VAL)
        deploySC.verify_create_currency(AIRCLAIM_SC,CURRENCY_FREEOS_VAL)

    #Iterations Section
    if (iteration):
        print("Updating Iterations")
        deploySC.show_iterations()
        deploySC.set_global_params()
        deploySC.set_all_iterations()
        deploySC.update_stake_requirements()
        deploySC.set_current_exchange_rate()
        deploySC.set_target_rate()
        deploySC.get_exchange_rate()
        deploySC.set_permission_transfer_token()

    if(validate):
        print("Validating the current state")
        deploySC.show_iterations()
        deploySC.get_exchange_rate()
        deploySC.read_permission_transfer_token()
        deploySC.read_statistics_table()

    if (version):
        print ("Checking version of contracts")
        for account in target_contracts:
            deploySC.get_version(account)

    if (field):
        print(f"Executing user actions in the field")

if __name__=='__main__':
    deploy_airclaim()
    print("Execution complete!\n")


