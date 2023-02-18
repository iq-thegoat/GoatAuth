from GoatAuth import DB

# Initialize the authentication module by providing the credentials to your MySQL database and a boolean indicating if you want to hash the user passwords.
# Example:
database = auth.DB(user='myuser', password='mypassword', host='localhost', database='mydatabase', HashCredentials=True)

# Use the insert() method to add a new user to the database.
# Example:
database.insert(key='mykey', email='johndoe@example.com', username='johndoe', password='mypassword', HWID='123456789')

# Use the isValidKey() method to check if a registration key is valid.
# Example:
if database.isValidKey(key='mykey'):
    print('Valid Key')
else:
    print('Invalid Key')

# Use the GenKey() method to generate a new registration key.
# Example:
key = database.GenKey(subtype='month')

# Use the login method to check if the these credintals are in the database 
# Example:
result = database.login(username="user_username",password="user_password",HWID="user_HWID")

if result:
  #Do somthing

else:
  #print("Wrong Credintals")
  
 #reset HWID
 databse.resethwid(email="userEmail",password="user_password",HWID="newHWID")
 



