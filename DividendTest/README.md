## How to use the script

```
python3 dividend_system.py
```

## Flow
1. Update the users' csv file that contains valid users, and their passwords, viz:
    > NFT_USER_FILE="dividend_30users.csv"

    If you want to pick limited users then use this parameter
    > NFT_USER_COUNT=25
    
    Here, although the csv has 45 users, only top 25 users shall be picked for NFT proposals. 
    If you put larger number than the entries in the `.csv` (e.g. 1000) then all users in the list shall be picked for NFTs.

2. Update dividend account, proposer and voter accounts as per your environment
    > VOTER_1="voterone3"
    > VOTER_2="votertwo3"
    > PROPOSER="proposer3"
    > DIVIDEND_SC="optionsdiv3"
3. This parameter will create number of proposals in each loop-
    > PER_USER_NFT_COUNT=3
4. Accept proposal by voting as '2'. Change it if later you want to vote with value as 1. Here voter1 is voting as '2':
  ``` 
  voter1.vote(2)
  ```

    
