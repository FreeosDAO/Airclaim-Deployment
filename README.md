# Airclaim-Deployment
Smart Contracts deployment - AirClaim, Dividend, FreeOS Config

## Usage
```
$ python3 freeos_system_v7.py -h
Usage:

python3 freeos_system_v7.py
	[-s | --simulation]
	[-I | --iteration]
	[-D | --deployment]
	[-V | --validate ]
	[-v | --version]
	[-h | --help]
```

# Modes
## simulation
> User claim and unvest simulation 

## iteration
> Create the iterations including future iterations and configure the start/end times

## deployment
> Deploy Airclaim and Dividend contracts

## validate
> Extract the deployment state and show the contract parameters, then exit. (No changes made to the system).

## version
> Contract versions and exit

# Changing configurations

```
# Iteration Settings
START_ITERATION_TIME = "2021-06-10T05:00:00" --> This time is in UTC. Offset properly from local time zone
ITERATION_INTERVAL = "03:00:00" --> This is the current active iteration interval
AUTO_PILOT_MODE=False --> False means script will prompt at each iteration to confirm before moving next iteration. True means will continue
USERS_FILE = "qa3_registered_new_users.csv" --> Users that will participate in Claim and Unvest in each iterations
START_ITER_NUM=100 --> In User Claim Simulation it is to control the iteration, make it active and start from that
```
## Execute

`$ python3 ./deploysc.py -F -I -D -V`

Below confirmation promt appears to ensure that input values are correct and right contracts are configured. 
> Default behaviour is capitalized when ENTER is pressed.


```
Please confirm the configuration before continue: 
	Blockchain end point = https://protontestnet.greymass.com
	AirClaim Contract Name = freeos3
	FreeOS Config Contract Name = freeoscfg3
	Dividend Contract Name = optionsdiv3
	Tokens Contract Name = freeostoken3

	Airclaim Iteration Start Time = 2021-06-10T05:00:00
	Iteration Interval = 03:00:00
	Total Iterations = 7
	Exchange Rate = 0.00053
	Target Rate = 0.0167
	Default Vesting Percent = 50
	Auto Pilot Mode = OFF
Are these configurations correct? [Y/n]:
```

Logs are generated in `$HOME/eos-deployment.log` file.

## User Claim Simulation
This function (line #1215) needs special configurations and arguments. It controls the good and bad times, and how long the iterations should run.
The values in the variable `current_rates` controls this. Modify it for a particular simulation-
```
current_rates=[500,0.0167, 0.011, 0.0018, 0.0167, ...
```

Below line doubles the planned parameters in the above variable. So, if the items in `current_rates` are 50, effecively 100 rates are provided for 100 iterations, when below line executes-
```
current_rates.extend(current_rates)
```



