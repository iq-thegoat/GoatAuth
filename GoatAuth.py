import mysql.connector as mysql
import hashlib,secrets,dateutil.relativedelta,datetime

class DB:
    def __init__(self,user:str,password:str,host:str,database:str,HashCredentials:bool):
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
            self.HashPasswords =bool(HashCredentials)
        except Exception as e:
            raise Exception(e) from e 
        try:
            self.cr.execute("""
            CREATE TABLE if not exists
            `userdata` (
                `ID` int(11) NOT NULL AUTO_INCREMENT,
                `username` varchar(255) NOT NULL,
                `password` varchar(255) NOT NULL,
                `HWID` varchar(255) NOT NULL,
                `created` datetime NOT NULL DEFAULT date_format(current_timestamp(), '%Y-%m-%d %H:%i:%s'),
                `email` varchar(255) NOT NULL,
                `End_date` datetime DEFAULT NULL,
                PRIMARY KEY (`ID`)
            ) ENGINE = InnoDB AUTO_INCREMENT = 131 DEFAULT CHARSET = utf8mb3""")
        except Exception as e:
            raise Exception("Error Creating userdata table\n"+str(e)) from e
        
        try:
            self.cr.execute("""
            CREATE TABLE if not exists
            `regkeys` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `regkey` varchar(255) DEFAULT NULL,
                `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
                `subtype` varchar(255) NOT NULL DEFAULT 'week',
                PRIMARY KEY (`id`)
            ) ENGINE = InnoDB AUTO_INCREMENT = 3901 DEFAULT CHARSET = utf8mb3
            """)
        except Exception as e:
            raise Exception("Error creating regkeys\n" + str(e)) from e

        try:
            self.cr.execute("""
            CREATE TABLE if not exists
            `keyslog` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `user_email` varchar(255) DEFAULT NULL,
                `user_username` varchar(255) DEFAULT NULL,
                `regkey` varchar(255) DEFAULT NULL,
                `used_at` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`)
            ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3
            """)
        except Exception as e:
            raise Exception(e) from e
        self.HashingSalt = "U2l0IGRvd24gYW5kIGNyb3NzIHlvdXIgbGVncywgcGxlYXNlIQ==" 
    
    def isValidKey(self,key:str):
        
        self.cr.execute("Select subtype from regkeys WHERE regkey = '%s' "%key)
        if self.cr.fetchone() is None:
            return False                                    
        else:
            return True

    def Hash(self,key:str):
        KEY= f"{self.HashingSalt}{key}{self.HashingSalt}"
        return hashlib.sha256(KEY.encode('utf-8')).hexdigest()

    def insert_into_logkeys(self,user,email,key):
        self.cr.execute("INSERT INTO keyslog(user_email,user_username,regkey) VALUES('%s','%s','%s')"%(email,user,key))
        self.cnx.commit()

    def remove_key(self,key:str,user:str,email:str):
        try:
            self.cr.execute('DELETE FROM regkeys WHERE regkey = "%s"'%key)
            return True
        except Exception as e:
            raise Exception(e) from e
        self.insert_into_logkeys(user, email, key)
        self.cnx.commit()

    def insert(self,key:str,email:str,username:str, password:str,HWID:str):
        if self.HashPasswords:
            username = self.Hash(username)
            password = self.Hash(password)
        if self.isValidKey(str(key)):
            self.cr.execute("Select subtype from regkeys WHERE regkey = '%s'"%key)
            results = self.cr.fetchall()
            sub = results[0][0].strip()
            if sub == 'month':
                now = datetime.datetime.now()
                # Add 30 days to the current date
                End_time = now + dateutil.relativedelta.relativedelta(days=31)
            elif sub == 'week':
                now = datetime.datetime.now()
                # Add 30 days to the current date
                End_time = now + dateutil.relativedelta.relativedelta(days=8)
            elif sub == "lifetime":
                now = datetime.datetime.now()
                # Add 30 days to the current date
                End_time = now + dateutil.relativedelta.relativedelta(days=5000)
            self.cr.execute("""
            INSERT INTO userdata 
            (username, password,HWID,email,End_date) VALUES ('%s','%s','%s','%s','%s')
            """%(username,password,HWID,email,End_time))
            try:
                self.remove_key(key,username,email)
            except Exception as e:
                raise Exception(e) from e
        else:
            raise Exception("Key is not valid")
        self.cnx.commit()

    def GenKey(self,subtype:str):
        KEY = str(secrets.token_urlsafe(32)).strip()+"-"+subtype.strip()
        try:
            self.cr.execute("INSERT INTO regkeys (regkey,subtype) VALUES('%s','%s')"%(KEY,subtype))
            self.cnx.commit()
            return KEY
        except Exception as e:
            print(e)

    def resethwid(self,email:str,password:str,HWID:str):
        try:
            if self.HashPasswords:
                password = self.Hash(password)
            self.cr.execute("UPDATE userdata set HWID = '%s' where email = '%s' and password = '%s'"%(HWID,email,password))
            self.cnx.commit()
        except Exception as e:
            raise Exception(e) from e
    
    def login(self,username:str,password:str,HWID:str):
        if self.HashPasswords:
            username = self.Hash(username)
            password = self.Hash(password)
        self.cr.execute(f"SELECT * FROM userdata WHERE username = '%s' AND password = '%s' and HWID = '%s'"%(username, password,str(HWID))) 
        results = self.cr.fetchall()
        try:
            if results[0][1] == username and results[0][2] == password and results[0][3] == str(HWID):
                return True
            else:   
                return False
        except IndexError:
            return False
