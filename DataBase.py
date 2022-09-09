import pymongo
import certifi
from cryptography.fernet import Fernet
from datetime import datetime
from pymongo.errors import OperationFailure
import pandas as pd

class DB_Engine:
    def __init__(self,GV):
        self.cluster= "mongodb+srv://DragoConnect:xnsSP7wL7XPaS2EW@cluster0.v20tw5l.mongodb.net/?retryWrites=true&w=majority"
        #DB INFO
        self.connected=False
        self.failedConnect=False
        self.connection=None
        self.db = None

        #User Info
        self.AllUsers=None
        self.UserInfo=None

        #Previous Game Info
        self.gamedf = None

        #settings
        self.MemoryInfluence = None  # overall memory inpact on prediction board, so if highest start value is 100 the max influence is 50 pnts
        self.PlacedShipMemoryInfluence = None  # Weighted heavier for player placed ships over random
        self.PlayerMemoryInfluence = None  # favor more player placements over all others
        self.key=None
        self.BIMG=None
        self.GameVer=GV

        print(self.dbConnect(self.cluster))

        if self.connected:
            # print(self.connection.list_database_names())
            self.db = self.connection.B_Ship
            self.retrive_Users()
            self.process_prev_games()
            self.retrieve_settings()
            # print(self.db.list_collection_names())

    def dbConnect(self,URL):
        ca = certifi.where()
        try:
            print("Testing Connection Please Wait")
            self.connection = pymongo.MongoClient(URL, tlsCAFile=ca,connectTimeoutMS= 5000,serverSelectionTimeoutMS= 5000)
            try:
                self.connection.server_info()
                self.connected = True
                return "Connection Successfull"
            except OperationFailure as e:
                self.failedConnect=True
                return e
        except Exception as e:
            self.failedConnect = True
            return e

    def retrieve_settings(self):
        settingdb = self.db.B_Ship_Settings
        cursor = settingdb.find({})
        for doc in cursor:
            self.MemoryInfluence = doc["MemoryInfluence"]
            self.PlacedShipMemoryInfluence = doc["PlacedShipMemoryInfluence"]  # Weighted heavier for player placed ships over random
            self.PlayerMemoryInfluence = doc["PlayerMemoryInfluence"]  # favor more player placements over all others
            self.key = doc["Key"]
            self.BIMG = doc["ImgURL"]

    def retrive_Users(self):
        userdb = self.db.B_Ship_Users
        cursor = userdb.find({})
        self.AllUsers = cursor

    def Check_Username(self,username):#making user check to make sure username doesn't already exist
        self.retrive_Users()
        for document in self.AllUsers:
            usr = document["username"]
            if username == usr:
                return True #username does exist
        return False #User name does not exist

    def Password_Check(self,username,password): #used during login
        self.retrive_Users()
        for document in self.AllUsers:
            usr = document["username"]
            if username == usr:
                if self.key==None:
                    try:
                        with open('filekey.key', 'rb') as filekey:
                            key = filekey.read()
                    except:
                        None
                else:
                    key = self.key

                fernet = Fernet(key)

                userpass = document['password']
                decpass = fernet.decrypt(userpass).decode() #decrypt db password

                if password == decpass: #check for match
                    self.UserInfo = USERIDINFO(document['_id'],document['username'],document['password'])
                    return True
                else:
                    return False
        return False

    def retrive_Games(self):
        gamesdb = self.db.B_Ship_Runs
        cursor = gamesdb.find({})
        return cursor

    def process_prev_games(self):
        allgames=self.retrive_Games()
        #transfer to list
        list_allgames = list(allgames)
        self.gamedf = pd.DataFrame(list_allgames)

    def create_game_doc(self,gwinner,placedships,pships,pshiptypeform,pshots,AItype,AIShips,AIshots):
        #user ID
        UserID = self.UserInfo.USERID
        #datetime
        daterun = datetime.now()
        #winner
        winner = gwinner
        #user place their own ships
        placedShips = placedships
        #player ship placement
        playerships= pships
        #player ship placement for each type of ship
        pshiptf = pshiptypeform
        #Player shots taken
        playershots=pshots
        #AI type
        AIType=AItype
        #AI Ship Placements
        AIShipPlace=AIShips
        #AI Shots taken
        AIShots=AIshots
        #number of shots
        if len(pshots)>len(AIshots):
            firedshots = len(pshots)
        else:
            firedshots = len(AIshots)
        ShotsFired=firedshots
        #GameVersion
        GV = self.GameVer

        gameres = {'userID':UserID,'date':daterun,'winner':winner,'userPlacedShips':placedShips,'playershipindx':playerships,'playershotsindx':playershots,
                   'AItype':AItype,'AIShipindx':AIShipPlace,'AIShotindx':AIShots,'ShotsFired':ShotsFired,'GameVersion':GV}

        gamesdb = self.db.B_Ship_Runs
        result = gamesdb.insert_one(gameres)

        gameID = result.inserted_id

        for ship in pshiptf:
            posres = {'GameID':gameID,'UserID':UserID,'row':ship.row,'col':ship.col,'size':ship.size,'orientation':ship.orientation,'indexes':ship.indexes}
            shipPosdb = self.db.B_Ship_Pos
            res = shipPosdb.insert_one(posres)

        self.process_prev_games()
        return

    def generate_key(self):#Used to generate orig key
        key=Fernet.generate_key()

        with open('filekey.key','wb') as filekey:
            filekey.write(key)

    def create_user_doc(self,username,password): #saving new user to DB
        #get key
        if self.key == None:
            try:
                with open('filekey.key', 'rb') as filekey:
                    key = filekey.read()
            except:
                None
        else:
            key = self.key

        fernet = Fernet(key)
        encpassword= fernet.encrypt(password.encode())

        #username, password, RB Player Wins, CB Player Wins, Prob Player Wins, ProbMem PlayerWins, Adv Player Wins, TotalGames

        user1={"username":username,"password":encpassword}

        userdb = self.db.B_Ship_Users
        result = userdb.insert_one(user1)
        return
        #retrieve all data

class USERIDINFO:
    def __init__(self,UserID,username,password):
        self.USERID=UserID
        self.username=username
        self.password=password