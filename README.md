#GoatAuth

goatauth is just a simple way to make a SQL auth system without hurting your mind on

the code is made for dummies not by design but it happens that iam a certifed dummy myself

anyways heres how to use it

```
from GoatAuth.GoatAuth import DB

# first of all initialize the class of course you should know that or its not your time to make a program that need auth

"""
Args:
        hash_credentials (bool): A flag indicating whether to hash passwords using SHA256 before storing them.
        name (str): The name of the database so that you can have more than one authsystem in the same db with different names.
        hwid_lock (bool): A flag indicating whether to use Hardware ID (HWID) locking mechanism.
        user (str): The username of the MySQL database.
        password (str): The password for the MySQL database.
        host (str): The hostname of the MySQL database.
        database (str): The name of the MySQL database.
"""

Auth = DB(HashCredentials=True,HWIDlock=True,Name="",user="",database="",host="",password='')

```
now you created this structure in your database ![dbstructure](https://user-images.githubusercontent.com/113275720/221686970-7fb60536-d572-438e-b99e-eefa8a2ab24e.png)

```
now lets go through each method fast because i have school tommorow

key = Auth.gen_key(subype = "week") # generates regestration key 

#and because this module is full of unsovled bugs  you have this method 

is_valid = Auth.is_valid_key(key) # if true then yes its valid if False then no

#lets pretend that you actually found somone that you scammed out of his 3$ and sold your img to ascii program  this is how you register him

Auth.register(key=key,user="bigtimmy",email="i_sniff_my_balls@gmail.com",password="i_type_the_openeing_bracket_in_a_second_line",HWID="timmysHWID") #dont do like timmy 
#note if you have HWIDlock disabled you dont have to put the HWID arg
```
now that you scammed bigtimmy you need to make him have access to your program dont worry i got you covered

```
Auth.login(username="bigtimmy",password="i_type_the_openeing_bracket_in_a_second_line",HWID="timmysHWID") 
#note if you have HWIDlock disabled you dont have to put the HWID arg
```

now you are a certefied buissness owner you want to gather someinfo about your users so use these methods

```
status = Auth.remove_user(email="i_sniff_my_balls@gmail.com") # True if succssful False if not

retrn = Auth.select_all(table=f"{your_name+tb}") #tb can be userdata or regkeys or keyslog

status  = Auth.remove_expired_subs() #takes no args and returns bool (True = Worked) else error is raised

worked = Auth.reset_password(new_password="i_learned_from_my_mistakes",user_email="i_sniff_my_balls@gmail.com") 
#or 
Auth.reset_password(new_password="i_learned_from_my_mistakes",user_username="bigtimmy")
#both works the same way

Status = Auth.custom_code("your SQL code;")

Auth.remaining_days(user_email = "i_sniff_my_balls@gmail.com") #returns remaining subscription time in days
#or 
Auth.remaining_days(user_username="bigtimmy") #returns remaining subscription time in days
#both works the same way

```



