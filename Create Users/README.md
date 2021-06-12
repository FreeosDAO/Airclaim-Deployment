## How to run

```
python3 freeos_users.py
```

The script has two modes - 
> Single User : Just create one user and perform the KYC as per parameter. 
Locate the line #278 and modify `user_name` and its target kyc type `user_kyc_type` for possible values `e`, `d`, and `v`. Now run the script as mentioned above.

```
def single_user():
    #Modify below properties for one user and run the script.
    user_name="vavianvivase"
    user_kyc_type='v'
```

> Multi User : Update the dictionary for users and their kyc types

```
def multiple_users():
   users={
        "e11111e11141":"e",
        "e11111e11142":"e",
```
## Steps
Uncomment the line as per requirement and run the script-

```
if __name__=='__main__':
    print(f"Un/comment one of the lines as per the use case (Single or Multi):")
    #single_user()
    #multiple_users()
```   

The script will generate two files per user (password file and wallet respectively):
```
proton_<username>.psw
proton_<username>.wallet
```
The default browser shall be opened for reCapcha steps at the proton testnet. Enter the details as dumped on the console.

### ToDo - merge the two modes so that based on list provided the users are created
