import mysql.connector as mysql
import hashlib,secrets,dateutil.relativedelta,datetime


class DB:
    def __init__(self,hashCredentials:bool,Name:str,HWIDlock:bool,user:str,password:str,host:str,database:str):

        """
            A class that provides functionality for managing a MySQL database with simple easy methods.

            ...

            Attributes
            ----------
            cnx : mysql.connector.connection_cext.CMySQLConnection
                The connection object for the MySQL database.

            cr : mysql.connector.cursor_cext.CMySQLCursor
                The cursor object for the MySQL database.

            HWIDLOCK : bool
                A flag indicating whether to use Hardware ID (HWID) locking mechanism.

            name : str
                The name of the database so that you can have more than one authsystem in the same db with diffrent names.

            hashPasswords : bool
                A flag indicating whether to hash passwords using SHA256 before storing them.

            ...

            Methods
            -------
            is_valid_key(key:str) -> bool:
                Checks if a registration key is valid.

            hash(key:str) -> str:
                Hashes a key using SHA-256.

            insert_into_logkeys(user:str, email:str, key:str) -> None:
                Inserts the used key into the keys log table with the user info and the using date.

            remove_key(key:str, user:str, email:str) -> bool:
                Removes a registration key and logs its use.

            register(key:str, email:str, username:str, password:str, HWID:str) -> bool:
                Registers a new user with the specified credentials and rem

        """


        try:
            self.cnx = mysql.connect(
                                user=user, 
                                password=password,
                                host=host,
                                database=database)
        except Exception as e:
            raise Exception("ERROR Connecting to database\n" + str(e)) from e
        try:
            self.cr = self.cnx.cursor()
        except Exception as e:
            raise Exception("Error Creating cursor object \n"+ str(e)) from e
        
        try:
            self.HWIDLOCK = bool(HWIDlock)
        except Exception as e:
            raise Exception("Error setting self.HWIDLOCK variable\n"+ str(e)) from e
            
        self.name = Name
        self.hashPasswords =bool(hashCredentials)

        try:
            if self.HWIDLOCK:
                self.cr.execute(f"""
                CREATE TABLE if not exists
                `{self.name}userdata` (
                    `ID` int(11) NOT NULL AUTO_INCREMENT,
                    `username` varchar(255) NOT NULL,
                    `password` varchar(255) NOT NULL,
                    `HWID` varchar(255) NOT NULL,
                    `created` datetime NOT NULL DEFAULT date_format(current_timestamp(), '%Y-%m-%d %H:%i:%s'),
                    `email` varchar(255) NOT NULL,
                    `End_date` datetime DEFAULT NULL,
                    PRIMARY KEY (`ID`)
                ) ENGINE = InnoDB AUTO_INCREMENT = 131 DEFAULT CHARSET = utf8mb3""")
            
            else:
                self.cr.execute(f"""

                CREATE TABLE
                `{self.name}userdata` (
                    `ID` int(11) NOT NULL AUTO_INCREMENT,
                    `username` varchar(255) NOT NULL,
                    `password` varchar(255) NOT NULL,
                    `created` datetime NOT NULL DEFAULT date_format(current_timestamp(), '%Y-%m-%d %H:%i:%s'),
                    `email` varchar(255) NOT NULL,
                    `End_date` datetime DEFAULT NULL,
                    PRIMARY KEY (`ID`)
                ) ENGINE = InnoDB AUTO_INCREMENT = 145 DEFAULT CHARSET = utf8mb3
                """
                                )
        except Exception as e:
            raise Exception(f"Error Creating {self.name} userdata table\n"+str(e)) from e
        
        try:
            self.cr.execute(f"""
            CREATE TABLE if not exists
            `{self.name}regkeys` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `regkey` varchar(255) DEFAULT NULL,
                `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
                `subtype` varchar(255) NOT NULL DEFAULT 'week',
                PRIMARY KEY (`id`)
            ) ENGINE = InnoDB AUTO_INCREMENT = 3901 DEFAULT CHARSET = utf8mb3
            """)
        except Exception as e:
            raise Exception(f"Error creating {self.name}regkeys\n" + str(e)) from e

        self.cr.execute(f"""
        CREATE TABLE if not exists
        `{self.name}keyslog` (
            `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
            `user_email` varchar(255) DEFAULT NULL,
            `user_username` varchar(255) DEFAULT NULL,
            `regkey` varchar(255) DEFAULT NULL,
            `used_at` timestamp NOT NULL DEFAULT current_timestamp(),
            PRIMARY KEY (`id`)
        ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3
        """)

        self.hashingSalt = "U2l0IGRvd24gYW5kIGNyb3NzIHlvdXIgbGVncywgcGxlYXNlIQ==" 
        

    def is_valid_key(self,key:str):
        
        self.cr.execute(f"Select subtype from {self.name}regkeys WHERE regkey = '%s' "%key)
        if self.cr.fetchone() is None:
            return False                                    
        else:
            return True

    def hash(self,key:str):
        KEY= f"{self.hashingSalt}{key}{self.hashingSalt}"
        return hashlib.sha256(KEY.encode('utf-8')).hexdigest()

    def insert_into_logkeys(self,user,email,key):
        self.cr.execute(f"INSERT INTO {self.name}keyslog (user_email,user_username,regkey) VALUES('%s','%s','%s')"%(email,user,key))
        self.cnx.commit()

    def remove_key(self,key:str,user:str,email:str):
        self.cr.execute(f'DELETE FROM {self.name}regkeys WHERE regkey = "%s"'%key)
        self.insert_into_logkeys(user, email, key)
        self.cnx.commit()
        return True
    
    def register(self,key:str,email:str,username:str, password:str,HWID :str = None):
        if self.hashPasswords:
            password = self.hash(password)

        if self.isValidKey(str(key)):

            self.cr.execute(f"Select subtype from {self.name}regkeys WHERE regkey = '%s'"%key)
            results = self.cr.fetchall()
            sub = results[0][0].strip()

            if sub == 'month':
                now = datetime.datetime.now()
                # Add 30 days to the current date
                End_time = now + dateutil.relativedelta.relativedelta(days=31)
            elif sub == 'week':
                now = datetime.datetime.now()
                # Add 7 days to the current date
                End_time = now + dateutil.relativedelta.relativedelta(days=8)
            elif sub == "lifetime":
                now = datetime.datetime.now()
                # Add 5000 days to the current date  {WORKS FINE BUT THE 5000 days thing is stupid NEEDS TO BE MODIFED}
                End_time = now + dateutil.relativedelta.relativedelta(days=5000)
            
            if self.HWIDLOCK:
                self.cr.execute(f"""
                INSERT INTO {self.name}userdata 
                (username, password,HWID,email,End_date) VALUES ('%s','%s','%s','%s','%s')
                """%(username,password,HWID,email,End_time))
            else:
                self.cr.execute(f"""
                INSERT INTO {self.name}userdata 
                (username, password,email,End_date) VALUES ('%s','%s','%s','%s')
                """%(username,password,email,End_time))

            self.remove_key(key,username,email)
        else:
            raise Exception("Key is not valid")
        self.cnx.commit()

    def gen_key(self,subtype:str):
        KEY = str(secrets.token_urlsafe(32)).strip()+"-"+subtype.strip()
        try:
            self.cr.execute(f"INSERT INTO {self.name}regkeys (regkey,subtype) VALUES('%s','%s')"%(KEY,subtype))
            self.cnx.commit()
            return KEY
        except Exception as e:
            raise Exception("Couldnt generate a key\n"+e) from e
    

    def reset_hwid(self,user_email:str,user_password:str,NEW_HWID:str):
        if self.HWIDLOCK == False:
            
            if self.hashPasswords:
                password = self.hash(password)
            self.cr.execute(f"UPDATE {self.name}userdata set HWID = '%s' where email = '%s' and password = '%s'"%(NEW_HWID,user_email,user_password))
            self.cnx.commit()
        
        else:
            raise AttributeError("you MUST enable HWIDlock to use this function")
        
    
    def login(self,username:str,password:str,HWID:str = None):
        if self.hashPasswords:
            username = self.hash(username)
            password = self.hash(password)
            
            
        if self.HWIDLOCK:
            self.cr.execute(f"SELECT * FROM {self.name}userdata WHERE username = '%s' AND password = '%s' and HWID = '%s'"%(username, password,str(HWID))) 
            try:
                results = self.cr.fetchall()
                if results[0][1] == username and results[0][2] == password and results[0][3] == str(HWID):
                    return True
                else:   
                    return False
            except IndexError:
                return False
        else:
            self.cr.execute(f"SELECT * FROM {self.name}userdata WHERE username = '%s' AND password = '%s'"%(username, password)) 
            results = self.cr.fetchall()

            try:
                    results = self.cr.fetchall()
                    if results[0][1] == username and results[0][2] == password:
                        return True
                    else:   
                        return False
                    
                    
            except IndexError:
                return False

        

    def remove_user(self,email:str):
        try:
            self.cr.execute(f"""
            delete from {self.name}userdata where email = "%s"
            """%email)
            return "Success"
        except Exception as e:
            raise e from e
    
    def select_all(self,table):
        self.cr.execute(f"select * from %s"%table)
        return self.cr.fetchall()

    def custom_code(self,code):
        try:
            self.cr.execute(code)
            return True 
        except Exception as e:
            raise e from e

    
    def remove_expired_subs(self):
        self.cr.execute(f"DELETE FROM {self.name}userdata WHERE End_date < CURDATE()")


    def reset_password(self,new_password:str,user_email:str = None,user_username:str = None) :
        password = hash(new_password)
        if user_email != None:
            self.cr.execute(f"UPDATE {self.name}userdata set password = '%s' where email = '%s'"%(password,user_email))
            return True
        
        elif user_username != None:
            self.cr.execute(f"UPDATE {self.name}userdata set password = '%s' where username = '%s'"%(password,user_email))
            return True
            
    
    def remaining_days(self,user_email:str = None,user_username:str = None):
        if user_email != None:
            self.cr.execute(f"select  DATEDIFF(end_date, CURDATE()) from  userdata  where email='%s'"%(user_email))
            return self.cr.fetchone()
        
        elif user_username != None:
            self.cr.execute(f"select  DATEDIFF(end_date, CURDATE()) from  userdata  where username='%s'"%(user_username))
            return self.cr.fetchone()
