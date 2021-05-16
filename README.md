# Airclaim-Deployment
Smart Contracts deployment - AirClaim, Dividend, FreeOS Config

## Usage
```
$ python3 ./deploysc.py -h
Usage:

python3 ./deploysc.py [-F | --field] [-I | --iteration] [-D | --deployment ] [-V | --validate ] [-v | --version] [-h | --help]
```



`$ python3 ./deploysc.py -F -I -D -V`

```
Please confirm the configuration before continue: 
	Blockchain end point = https://protontestnet.greymass.com
	AirClaim Contract Name = freeos2
	FreeOS Config Contract Name = freeoscfg2
	Dividend Contract Name = optionsdiv2
	Tokens Contract Name = freeostoken2

	Airclaim Iteration Start Time = 2021-05-17T01:00:00
	Iteration Interval = 00:15:00
	Total Iterations = 8
	Exchange Rate = 0.00053
	Target Rate = 0.0167
	Default Vesting Percent = 50

Are these configurations correct? [Y/n]: 
```

Logs are generated in `$HOME/eos-deployment.log` file.



