from engine import Player
from engine import Game
from DataBase import DB_Engine
import ctypes
import time



app_version="2.1.0"

#Pygame Setup
import pygame

pygame.init()
pygame.display.set_caption("BattleShip v"+app_version)

#Screens
startup_screen=False
game_screen=False
Login_screen=False
Create_User_screen=False
Show_Ship_Confirm_screen=False

#Globals
TOP_BUFFER=40
Stack_But_Bott =2 #how many buttons (stacked) will be in the bottom of the screen
BUTTON_HEIGHT = 40
BUTTON_WIDTH=150
TEXTBOX_HEIGHT=40
TEXTBOX_WIDTH=350
SQ_SIZE = 45 #square size on grid
H_MARGIN = SQ_SIZE*4
V_MARGIN = SQ_SIZE
WIDTH=SQ_SIZE*10*2+H_MARGIN #10x10 grid
HEIGHT=SQ_SIZE*10+V_MARGIN+(BUTTON_HEIGHT*Stack_But_Bott+10)+TOP_BUFFER
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
INDENT = 10


HUMAN1 = True
HUMAN2 = False

#colors
GREY = (40,50,60)
LIGHTGREY=(160,160,160)
WHITE = (255,250,250)
GREEN = (50, 200, 150)
BLUE = (50, 150, 200)
ORANGE = (250,140,20)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK =(0,0,0)
COLORS = {"U": GREY, "M":BLUE,"H":ORANGE,"S":RED}

#font
tinyfont = pygame.font.SysFont('Corbel',25)
smallfont = pygame.font.SysFont('Corbel',30)
FinalFont = pygame.font.SysFont('fresansttf',100)

#random Message Storage
MSSG=""
MSSGCount=0
#DRAWING METHODS
#function to draw grid
def draw_grid(left=0,top=0):
    for i in range(100):
        x = left + i % 10 * SQ_SIZE
        y = top + i // 10 * SQ_SIZE
        square = pygame.Rect(x,y,SQ_SIZE,SQ_SIZE)
        pygame.draw.rect(SCREEN,LIGHTGREY,square,width=1)

def draw_grid_shots(player, left=0,top=0, search = False):
    for i in range(100):
        x = left + i % 10 * SQ_SIZE
        y = top + i // 10 * SQ_SIZE
        if search:
            x += SQ_SIZE//2
            y += SQ_SIZE//2
            if player.search[i]!="U":
                pygame.draw.circle(SCREEN, COLORS[player.search[i]],(x,y),radius=SQ_SIZE//4)

#draw ship onto the position grid
def draw_ships(player,left=0,top=0,reveal_death=False,opponent=None):
    if reveal_death:
        for ship in player.ships:
            sunk = True
            for i in ship.indexes:
                if opponent.search[i] == "U":
                    sunk = False
                    break
            if sunk:
                x = left + ship.col * SQ_SIZE + INDENT
                y = top + ship.row * SQ_SIZE+ INDENT
                if ship.orientation == "h":
                    width = ship.size * SQ_SIZE - 2*INDENT
                    height = SQ_SIZE - 2*INDENT
                else:
                    width = SQ_SIZE - 2*INDENT
                    height = ship.size * SQ_SIZE - 2*INDENT
                rectangle = pygame.Rect(x,y,width,height)
                pygame.draw.rect(SCREEN,GREEN,rectangle,border_radius=15)
    else:
        for ship in player.ships:
            x = left + ship.col * SQ_SIZE + INDENT
            y = top + ship.row * SQ_SIZE+ INDENT
            if ship.orientation == "h":
                width = ship.size * SQ_SIZE - 2*INDENT
                height = SQ_SIZE - 2*INDENT
            else:
                width = SQ_SIZE - 2*INDENT
                height = ship.size * SQ_SIZE - 2*INDENT
            rectangle = pygame.Rect(x,y,width,height)
            pygame.draw.rect(SCREEN,GREEN,rectangle,border_radius=15)

#draw temp ships on grid during setup
def draw_TEMP_ships(left=0,top=0):
    global MousePos
    global ship_size_list
    global ship_orientation
    if len(ship_size_list)>0:
        ship_size = ship_size_list[0]
        col,row = MousePos if MousePos is not None else [0,0]

        x = left + col * SQ_SIZE + INDENT
        y = top + row * SQ_SIZE+ INDENT
        if ship_orientation == "h":
            width = ship_size * SQ_SIZE - 2*INDENT
            height = SQ_SIZE - 2*INDENT
        else:
            width = SQ_SIZE - 2*INDENT
            height = ship_size * SQ_SIZE - 2*INDENT
        rectangle = pygame.Rect(x,y,width,height)
        pygame.draw.rect(SCREEN,YELLOW,rectangle,border_radius=15)
    else:
        global Bool_Ship_Setup
        Bool_Ship_Setup = not Bool_Ship_Setup

def draw_Prob_Heat_Map(left=0,top=0):
    if playerAI.probability_board != None:
        playerAI_HeatMap = playerAI.probability_board
        fin_max = max(playerAI_HeatMap, key=playerAI_HeatMap.get)
        fin_min = min(playerAI_HeatMap, key=playerAI_HeatMap.get)
        mx_val =playerAI_HeatMap[fin_max]
        mn_val = playerAI_HeatMap[fin_min]
        x_data=[]
        y_data=[]
       # print(board_array)
        data_colors=[]
        for i in range(100):
            value = playerAI_HeatMap[i]
            perc = 0
            if value !=0:
                #perc = (value/mx_val)*100
                perc = (value / mx_val)

            HeatColor=GREY
            # red = int(102 * perc)
            # green = int(51+255*perc)
            # if green>255:green=255
            # blue = int(102*perc)
            red = int(255 * perc)
            green = int(153*perc)
            blue = int(51*perc)
            HeatColor = (red,green,blue)
            # if perc>20:
            #     HeatColor=BLUE
            # if perc>40:
            #     HeatColor=RED
            # if perc>60:
            #     HeatColor=ORANGE
            # if perc>80:
            #     HeatColor=YELLOW
            # if perc>90:
            #     HeatColor=WHITE



            x = left + i % 10 * SQ_SIZE
            y = top + i // 10 * SQ_SIZE
            square = pygame.Rect(x,y,SQ_SIZE,SQ_SIZE)
            pygame.draw.rect(SCREEN,HeatColor,square)


def draw_prob_heat_vals(left=0,top=0):
    if playerAI.probability_board != None:
        for i in range(100):
            playerAI_HeatMap = playerAI.probability_board
            fin_max = max(playerAI_HeatMap, key=playerAI_HeatMap.get)
            fin_min = min(playerAI_HeatMap, key=playerAI_HeatMap.get)
            mx_val =playerAI_HeatMap[fin_max]

            value = playerAI_HeatMap[i]
            perc = 0
            if value !=0:
                perc = (value/mx_val)*100
            x = left + i % 10 * SQ_SIZE
            y = top + i // 10 * SQ_SIZE
            # if perc > 80:
            #     perc_txt = tinyfont.render(str(value), True, BLACK)
            # else:
            perc_txt = tinyfont.render(str(value), True, WHITE)
            perc_TRC = perc_txt.get_rect()
            x += SQ_SIZE // 2
            y += SQ_SIZE // 2
            perc_TRC.center = (x, y)
            SCREEN.blit(perc_txt, perc_TRC)

#CLASSES
#Create Button Class RefreshButton
class Button:
    def __init__(self,text,width,height,pos,elevation,deftocall):
        #Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text
        self.text_surf = smallfont.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

        #def call
        self.def_Call = deftocall

    def draw(self):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(SCREEN,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(SCREEN,self.top_color, self.top_rect,border_radius = 12)
        SCREEN.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    result = self.def_Call()
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'

#class for text input fields
class TextBox:
    def __init__(self,width,height,pos,elevation,textLen,password=False,showpass=False):
        #Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'

        #text
        self.userText = ""
        self.passwordtxt=""
        self.text_surf = smallfont.render(self.userText,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

        #def extra
        self.text_len = textLen
        self.password = password
        self.showpass = showpass
    def ClearText(self):
        self.userText=""
        self.passwordtxt=""

    def AddLetter(self,char,Add=True):
        if Add:
            if len(self.userText)<self.text_len:
                if self.password:
                    self.passwordtxt+=char
                    if self.showpass:
                        self.userText = self.passwordtxt
                    else:
                        self.userText=""
                        for i in range(len(self.passwordtxt)):
                            self.userText += '*'
                else:
                    self.userText+=char
        else:#remove
            self.userText=self.userText[:-1]
            self.passwordtxt=self.passwordtxt[:-1]


    def draw(self):
        #drawTXT
        if self.password:
            if self.showpass:
                self.userText = self.passwordtxt
            else:
                self.userText = ""
                for i in range(len(self.passwordtxt)):
                    self.userText += '*'
        self.text_surf = smallfont.render(self.userText,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(SCREEN,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(SCREEN,self.top_color, self.top_rect,border_radius = 12)
        SCREEN.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
        else:
            self.dynamic_elecation = self.elevation
            if self.pressed:
                self.top_color='#8299B0'
            else:
                self.top_color = '#475F77'
            if pygame.mouse.get_pressed()[0]:
                self.pressed=False

#Create Button Class RefreshButton
class ToggleButton:
    def __init__(self,text,width,height,pos,elevation,deftocall):
        #Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = '#475F77'

        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = '#354B5E'
        #text
        self.text_surf = smallfont.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

        #def call
        self.def_Call = deftocall

        #waituntilnextclick
        self.waittime = time.time()

    def draw(self):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(SCREEN,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(SCREEN,self.top_color, self.top_rect,border_radius = 12)
        SCREEN.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            #self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                if (time.time()-self.waittime)>0.5:
                    self.waittime = time.time()
                    if self.pressed:
                        self.dynamic_elecation = 0
                        self.pressed = False
                        self.top_color = '#475F77'  # Grey
                    elif not self.pressed:
                        self.dynamic_elecation = 0
                        self.pressed = True
                        result = self.def_Call()
                        self.top_color = '#169e1c'  # Green
        else:
            self.dynamic_elecation = self.elevation
            if self.pressed == True:
                self.dynamic_elecation = self.elevation
                self.top_color = '#169e1c'  # Green
            else:
                self.dynamic_elecation = self.elevation
                self.top_color = '#475F77'  # Grey



#CREATE GAME
#Make Game
AI_INDX=0
AI_LIST=None
AI_Meth=None
AI_Active=None
def MakeGame():
    global AI_Meth
    global AI_LIST
    global AI_INDX
    global AI_Active
    global DB_Con
    game = Game(player1, playerAI,HUMAN1,HUMAN2,DB_Con,AI_INDX)
    if DB_Con!=None: game.DB=DB_Con
    AI_LIST = ["RANDOM", "BASIC", "PROBABILITY", "PROB+Memory","ADVANCE"]
    AI_Meth = [game.basic_ai_random, game.basic_ai_v3, game.probability_ai, game.probability_ai,game.advance_ai]
    if DB_Con==None:
        AI_Active = [True, True, True, False, False]
    else:
        if DB_Con.failedConnect:
            AI_Active=[True,True,True,False,False]
        else:
            AI_Active = [True, True, True, True, False]
    return game

#randomize Ships
def RefreshShips(setup=False):
    global player1
    player1 = Player()
    global playerAI
    playerAI = Player()
    global game
    game = MakeGame()
    global ship_size_list
    ship_size_list=[]
    global Setup_Ships_Last
    if setup:
        Setup_Ships()
    else:
        Setup_Ships_Last = False
    global showShips
    if not showShips:
        global shipsShown
        global Ship_Agree_Show
        shipsShown = False
        Ship_Agree_Show = False


#CHECK DB
DB_Con=None #DB connection
TestCon=False
def Check_DB():
    SCREEN.fill(GREY)
    # image
    # image = pygame.image.load("BShipIMG.jpg")
    # SCREEN.blit(image, ((WIDTH / 2) - 320, HEIGHT - 453))

    # Text
    text = "Checking Connection To Database, Please Wait..."
    textbox = smallfont.render(text, True, WHITE, GREY)
    ttTRC = textbox.get_rect()
    ttTRC.center = ((WIDTH / 2) - 10, (HEIGHT/2))
    SCREEN.blit(textbox, ttTRC)
    pygame.display.flip()
    pygame.time.wait(50)

    Result=""
    global app_version
    global DB_Con
    DB_Con=DB_Engine(GV=app_version)
    if DB_Con!=None:
        if DB_Con.connected:
            SCREEN.fill(GREY)
            # image
            # image = pygame.image.load("BShipIMG.jpg")
            # SCREEN.blit(image, ((WIDTH / 2) - 320, HEIGHT - 453))

            # Text
            text = "Connection To Database Successful, Loading Login"
            textbox = smallfont.render(text, True, WHITE, GREY)
            ttTRC = textbox.get_rect()
            ttTRC.center = ((WIDTH / 2) - 10, (HEIGHT/2))
            SCREEN.blit(textbox, ttTRC)
            pygame.display.flip()
            pygame.time.wait(500)

            Screen_Select(Login=True)

#Screens to show
def Screen_Select(gameScreen=False,ShowShips=False,Login=False,startup=False,createuser=False):
    global game_screen
    global Login_screen
    global Show_Ship_Confirm_Screen
    global startup_screen
    global Create_User_screen
    game_screen = gameScreen
    Login_screen = Login
    Show_Ship_Confirm_Screen = ShowShips
    startup_screen=startup
    Create_User_screen=createuser
    if startup:
        Check_DB()

Screen_Select(startup=True)#default login

#define our game
player1 = Player()
playerAI = Player()
game = MakeGame()

#Button Methods
showShips = False
shipsShown=False
Ship_Agree_Show=False
def ShowShips():
    global shipsShown
    global Ship_Agree_Show
    if not shipsShown:
        #prompt to show
        Screen_Select(ShowShips=True)
    global showShips
    if Ship_Agree_Show:
        showShips = not showShips

def ShowShips_Confirm():
    global shipsShown
    global Ship_Agree_Show
    shipsShown=True
    Ship_Agree_Show=True
    Screen_Select(gameScreen=True)
    ShowShips()

def ShowShips_Deny():
    Screen_Select(gameScreen=True)

def StopGame():
    global animating
    animating = False

GameStarted=False
def StartGame():
    global GameStarted
    global AI_INDX
    global game
    global looplim
    global toggle
    toggle=False #reset endscreen
    looplim=0
    GameStarted = True
    if AI_INDX == 2 and len(playerAI.shotstaken) < 1:  # probability
        game.player1_turn=False
        AI = AI_Meth[AI_INDX]
        AI(initalize=True)
        game.player1_turn = True
    elif AI_INDX == 3 and len(playerAI.shotstaken) < 1:  # probability
        game.player1_turn=False
        AI = AI_Meth[AI_INDX]
        AI(initalize=True,MemMode=True)
        game.player1_turn = True
    if len(playerAI.shotstaken) == 0 and AIShipSetup:  # if new game and AI setupship then setup ship
        game.PlayerShotsMakeMemBoards()

def Restart():
    global GameStarted
    global Game_Turns
    global B_Heat_Map
    global Bool_Ship_Setup
    global showShips
    global Setup_Ships_Last
    Game_Turns=1
    GameStarted=False
    B_Heat_Map = False
    INFO.pressed=False
    Bool_Ship_Setup=False
    showShips=False
    RefreshShips(setup=Setup_Ships_Last)
    global shipsShown
    global Ship_Agree_Show
    shipsShown=False
    Ship_Agree_Show=False

def Sel_AI():
    global AI_INDX
    global AI_LIST
    global game
    AI_INDX+=1
    if AI_INDX >= len(AI_LIST):
        AI_INDX = 0
    active = False
    while not active:
        active=AI_Active[AI_INDX]
        if not active:AI_INDX+=1
        if AI_INDX>=len(AI_LIST):
            AI_INDX=0
    game.AIType = AI_INDX

Bool_Ship_Setup=False
MousePos = None
ship_size_list=[]
ship_orientation="h"
Setup_Ships_Last=False
def Setup_Ships():
    global Bool_Ship_Setup
    global Setup_Ships_Last
    Bool_Ship_Setup= not Bool_Ship_Setup
    Setup_Ships_Last=True
    # Go through player list of ships
    player1.ships=[] #clear ships
    global ship_size_list
    ship_size_list = player1.ship_sizes.copy()

B_Heat_Map=False
def Show_AI_Info():
    global B_Heat_Map
    B_Heat_Map=not B_Heat_Map

def Login():
    #login to server via DB:
    UsernameExist = DB_Con.Check_Username(Username.userText)
    if UsernameExist: #if user exists
        #check user Passcode
        PasswordCheck = DB_Con.Password_Check(Username.userText,Password.passwordtxt)
        if PasswordCheck:
           #successfull login
            #switch to game if successfull
            Screen_Select(gameScreen=True)
        else:
            #password failed
            Mbox("Error","Incorrect Password",0)
            print("wrong password")
    else:
        #No user found
        Mbox("Error", "User Not Found", 0)
        print("User not found")
    return

def GoToCreateUser():
    Password.ClearText()
    Confirm_Pass.ClearText()
    Screen_Select(createuser=True)

def ShowPass():
    Password.showpass=not Password.showpass
    Confirm_Pass.showpass=not Confirm_Pass.showpass

def BackLogin():
    Password.ClearText()
    Confirm_Pass.ClearText()
    Password.showpass = False
    Confirm_Pass.showpass = False
    Screen_Select(Login=True)

def SaveNewUser():
    global DB_Con
    #save new user to DB
    UsernameExist= DB_Con.Check_Username(Username.userText)
    if not UsernameExist:
        #do passwords match?
        pass1 = Password.passwordtxt
        pass2 = Confirm_Pass.passwordtxt
        if pass1 == pass2 and len(pass1)>0:
            #save new user
            DB_Con.create_user_doc(Username.userText,Password.passwordtxt)
            #go back to login
            Password.ClearText()
            Confirm_Pass.ClearText()
            Password.showpass = False
            Confirm_Pass.showpass = False
            Screen_Select(Login=True)
        else:
            #passwords do not match
            Mbox("Error","Passwords Do Not Match",0)
            return
    else:
        #username already in Use
        Mbox("Error", "Username Already Taken", 0)
        return

def PlayGuest():
    #Login as Guest to DB
    PasswordCheck = DB_Con.Password_Check("Guest", "")
    if PasswordCheck:
        # successfull login
        # switch to game if successfull
        Screen_Select(gameScreen=True)
    else:
        # password failed
        print("wrong password")

AIShipSetup=False
def AISetupShips():
    global game
    global AIShipSetup
    game.AISetupShip=not game.AISetupShip
    AIShipSetup = not AIShipSetup
    return

# Buttons
#GameModeButtons
BUTTON_OFFSET=15
RandBut = Button('Randomize', BUTTON_WIDTH, BUTTON_HEIGHT, (15+BUTTON_WIDTH,(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,RefreshShips)

ManShip =  Button('Setup Ships', BUTTON_WIDTH, BUTTON_HEIGHT, (15+BUTTON_WIDTH,(HEIGHT-(BUTTON_HEIGHT*1+10))), 5,Setup_Ships)

StartBut = Button('Start', BUTTON_WIDTH, BUTTON_HEIGHT, (5,(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,StartGame)

QuitBut = Button('Quit', BUTTON_WIDTH, BUTTON_HEIGHT, (5,(HEIGHT-(BUTTON_HEIGHT*1+10))), 5,StopGame)

ShowEnemy = Button('Show Ship', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH-(BUTTON_WIDTH*3)),(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,ShowShips)

#INFO = Button('AI Info', BUTTON_WIDTH-50, BUTTON_HEIGHT, ((WIDTH-(BUTTON_WIDTH)+15),(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,Show_AI_Info)

AI_Select = Button('Change AI', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH-(BUTTON_WIDTH*2)+10),(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,Sel_AI)

StartOverBut = Button('Restart', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH/2)-75, 20), 5,Restart)

#ShowShipButtons
ShipShowYes= Button('Yes', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH/2)-175, 200), 5,ShowShips_Confirm)
ShipShowNo= Button('No', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH/2)+75, 200), 5,ShowShips_Deny)

#Text Fields
Username = TextBox(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, (150, 200), 5,textLen=20,password=False)
Password = TextBox(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, (150+(TEXTBOX_WIDTH)+50, 200), 5,textLen=20,password=True)
Confirm_Pass = TextBox(TEXTBOX_WIDTH, TEXTBOX_HEIGHT, (150+(TEXTBOX_WIDTH)+50, 300), 5,textLen=20,password=True)

#Toggle Button in Gamemode
AIShipTog = ToggleButton('AI Ship Placement', BUTTON_WIDTH+75, BUTTON_HEIGHT, ((WIDTH/2)-150, (HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,AISetupShips)
INFO = ToggleButton('AI Info', BUTTON_WIDTH-50, BUTTON_HEIGHT, ((WIDTH-(BUTTON_WIDTH)+15),(HEIGHT-(BUTTON_HEIGHT*2+TOP_BUFFER))), 5,Show_AI_Info)

#LoginScreen Buttons
LoginBTN = Button('Login', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH/2)-100, 300), 5,Login)
GuestBTN = Button('Play As Guest', BUTTON_WIDTH+50, BUTTON_HEIGHT, ((WIDTH/2)-125, 450), 5,PlayGuest)
CreateUserBTN = Button('Create User', (BUTTON_WIDTH+10), BUTTON_HEIGHT, ((WIDTH/2)-105, 375), 5,GoToCreateUser)
ShowPassBTN=Button('Show Pass', BUTTON_WIDTH, BUTTON_HEIGHT, ((WIDTH)-(BUTTON_WIDTH+10), 250), 5,ShowPass)
SaveBTN=Button('Save User', BUTTON_WIDTH, BUTTON_HEIGHT, (((WIDTH/2)-100), 400), 5,SaveNewUser)
BackBTN=Button('Back', BUTTON_WIDTH, BUTTON_HEIGHT, (((WIDTH/2)-100), 450), 5,BackLogin)

#Message box
def Mbox(title,text,style):
    ###  Styles:
    ##  0 : OK
    ##  1 : OK | Cancel
    ##  2 : Abort | Retry | Ignore
    ##  3 : Yes | No | Cancel
    ##  4 : Yes | No
    ##  5 : Retry | Cancel
    ##  6 : Cancel | Try Again | Continue
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


#pygame main loop
animating = True
pausing = False
toggle = False
looplim = 0
while animating:
    #track user interaction
    for event in pygame.event.get():
        #user closes pygame
        if event.type == pygame.QUIT:
            animating=False

        M_offset = 40 #mouse offset
        if Bool_Ship_Setup and len(ship_size_list)>0:
            x,y = pygame.mouse.get_pos()
            y = y-M_offset #offset for some reason I need this to fit in squares
            if x< SQ_SIZE*10 and y< (10*SQ_SIZE)+TOP_BUFFER:
                row = y // SQ_SIZE
                col = x // SQ_SIZE
                if row<0: row=0
                if row>9:row=9
                index = row * 10 + col
                if ship_orientation=='h':
                    end_of_ship_index = index+ship_size_list[0]
                    n_row = end_of_ship_index//10
                    if n_row!=row:
                        trow=n_row*10
                        dif = end_of_ship_index-trow
                        col = col-dif
                else:
                    end_of_ship_index = index+(ship_size_list[0]*10)
                    if end_of_ship_index>99:
                        dif = (end_of_ship_index%100)//10
                        row = row-dif

                MousePos= col,row

        #user clicks on mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.type != pygame.MOUSEWHEEL:
                x,y = pygame.mouse.get_pos()
                y = y-M_offset #offset for some reason I need this to fit in squares
                if GameStarted: #game has started
                    if not game.over: #game isnt over
                        if game.player1_turn and x> WIDTH-SQ_SIZE*10 and y< (SQ_SIZE)*10+TOP_BUFFER: #player Turn check board
                            row = y // SQ_SIZE
                            col = (x-((WIDTH-H_MARGIN)//2+H_MARGIN)) // SQ_SIZE
                            index = row * 10 + col
                            if index not in player1.shotstaken and row<10 and col <10:
                                game.make_move(index)

                        elif not game.player1_turn and x< SQ_SIZE*10 and y< (10*SQ_SIZE)+TOP_BUFFER: #AI turn check board
                            row = y // SQ_SIZE
                            col = x // SQ_SIZE
                            index = row * 10 + col
                            if index not in playerAI.shotstaken and row<10 and col <10:
                                game.make_move(index)

                if Bool_Ship_Setup and MousePos != None:
                    if x < SQ_SIZE * 10 and y < (10 * SQ_SIZE) + TOP_BUFFER:
                        col, row = MousePos
                        #call to place ship
                        cur_num_ship = len(player1.ships)
                        player1.place_ships([ship_size_list[0]],row=row,col=col,orientation=ship_orientation)
                        if len(player1.ships)>cur_num_ship: #ship was placed
                            ship_size_list.pop(0)#remove ship

        #user presses key
        if event.type == pygame.KEYDOWN:

         #add rotate key during placement
            if event.key == pygame.K_r and Bool_Ship_Setup:
                if ship_orientation=="v":
                    ship_orientation="h"
                else:
                    ship_orientation="v"
                #ship_orientation = "h" if ship_orientation == "v" else ship_orientation="v"

         #escape key exit game
            if event.key == pygame.K_ESCAPE:
                animating=False

         #spacebar pause game
            if event.key == pygame.K_SPACE:
                if not Login_screen and not Create_User_screen:
                    pausing = not pausing

        #return key restarts game
            if event.key == pygame.K_RETURN:
                if not Login_screen and not Create_User_screen:
                    Restart()

        if Login_screen:
            if Username.pressed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        Username.AddLetter("",Add=False)
                    elif event.key == pygame.K_TAB:
                        Username.pressed=False
                        Password.pressed=True
                    elif event.key == pygame.K_RETURN:
                        active = False
                    else:
                        Username.AddLetter(event.unicode,Add=True)
            if Password.pressed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        Password.AddLetter("",Add=False)
                    elif event.key == pygame.K_TAB:
                        active = False
                    elif event.key == pygame.K_RETURN:
                        Login()
                    else:
                        Password.AddLetter(event.unicode,Add=True)

        if Create_User_screen:
            if Confirm_Pass.pressed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        Confirm_Pass.AddLetter("", Add=False)
                    elif event.key == pygame.K_TAB:
                        active = False
                    elif event.key == pygame.K_RETURN:
                        SaveNewUser()
                    else:
                        Confirm_Pass.AddLetter(event.unicode, Add=True)

            if Password.pressed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        Password.AddLetter("", Add=False)
                    elif event.key == pygame.K_TAB:
                        Password.pressed = False
                        Confirm_Pass.pressed = True
                    elif event.key == pygame.K_RETURN:
                        active = False
                    else:
                        Password.AddLetter(event.unicode, Add=True)

            if Username.pressed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        Username.AddLetter("", Add=False)
                    elif event.key == pygame.K_TAB:
                        Username.pressed = False
                        Password.pressed = True
                    elif event.key == pygame.K_RETURN:
                        active = False
                    else:
                        Username.AddLetter(event.unicode, Add=True)

    #execution of screen display
    if not pausing:

        #draw background
        SCREEN.fill(GREY)
        if startup_screen:
            if DB_Con.failedConnect:
                SCREEN.fill(GREY)
                # image
                # image = pygame.image.load("BShipIMG.jpg")
                # SCREEN.blit(image, ((WIDTH / 2) - 320, HEIGHT - 453))

                # Text
                text = "Failed Connection To Database, Loading Base Game"
                textbox = smallfont.render(text, True, WHITE, GREY)
                ttTRC = textbox.get_rect()
                ttTRC.center = ((WIDTH / 2) - 10, (HEIGHT / 2))
                SCREEN.blit(textbox, ttTRC)
                pygame.display.flip()

                looplim+=1
                pygame.time.wait(10)
                if looplim>=300:
                    Screen_Select(gameScreen=True)

            #if DB connection success allow for all game modes & login user

            #if db connection not successful only allow first 3 game modes

        elif Login_screen:
            #textwindow
            text = "Please Type In Your Username And Password Below:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((WIDTH / 2) - 10, 50)
            SCREEN.blit(textbox, ttTRC)

            text = "Username:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = (225, 180)
            SCREEN.blit(textbox, ttTRC)

            text = "Password:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((225+(TEXTBOX_WIDTH)+50), 180)
            SCREEN.blit(textbox, ttTRC)

            #text Fields
            Username.draw()
            Password.draw()
            #buttons
            LoginBTN.draw()
            CreateUserBTN.draw()
            GuestBTN.draw()
            pygame.time.wait(10)

        elif Create_User_screen:
            #textwindow
            text = "Create Your Username And Password Below:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((WIDTH / 2) - 10, 50)
            SCREEN.blit(textbox, ttTRC)

            text = "Username:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = (225, 180)
            SCREEN.blit(textbox, ttTRC)

            text = "Password:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((225+(TEXTBOX_WIDTH)+50), 180)
            SCREEN.blit(textbox, ttTRC)

            text = "Confirm Password:"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((225+(TEXTBOX_WIDTH)+100), 280)
            SCREEN.blit(textbox, ttTRC)

            #text Fields
            Username.draw()
            Password.draw()
            Confirm_Pass.draw()
            #buttons
            ShowPassBTN.draw()
            SaveBTN.draw()
            BackBTN.draw()
            pygame.time.wait(10)

        elif Show_Ship_Confirm_Screen:
            #Text Prompt
            turn_title=tinyfont.render('Showing Enemy Ships Will Result In This Game Not Being Saved Due To Cheating',True,WHITE,GREY)
            ttTRC=turn_title.get_rect()
            ttTRC.center = ((WIDTH/2)-10, 20+100)
            SCREEN.blit(turn_title,ttTRC)

            text = "Do You Want To Show Enemy Ships?"
            textbox = smallfont.render(text,True,WHITE,GREY)
            ttTRC=textbox.get_rect()
            ttTRC.center = ((WIDTH / 2) - 10, 50)
            SCREEN.blit(textbox, ttTRC)

            #Buttons
            ShipShowYes.draw()
            ShipShowNo.draw()
            pygame.time.wait(10)

        elif game_screen:
            #draw Buttons
            if not GameStarted:
                RandBut.draw()
                if not Bool_Ship_Setup:
                    StartBut.draw()
                    ManShip.draw()
                    AI_Select.draw()
                    AIShipTog.draw()
            if AI_INDX == 2 or AI_INDX==3:
                INFO.draw()
            QuitBut.draw()
            ShowEnemy.draw()

            #draw position grid
            draw_grid(left = 0, top=TOP_BUFFER) #Player Board AI Search

            #draw search grid
            draw_grid(left=(WIDTH-H_MARGIN)//2+H_MARGIN,top=TOP_BUFFER) #AI Board Player Search

            #draw heat map
            if (AI_INDX == 2 and B_Heat_Map) or (AI_INDX == 3 and B_Heat_Map):
                draw_Prob_Heat_Map(left=0,top=TOP_BUFFER)

            #draw ships onto position grid
            draw_ships(player1,left = 0, top=TOP_BUFFER)
            if showShips:
                draw_ships(playerAI,left=(WIDTH-H_MARGIN)//2+H_MARGIN,top=TOP_BUFFER)
            else:
                if game.over:
                    draw_ships(playerAI, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN, top=TOP_BUFFER)  # show ships game over
                else:
                    draw_ships(playerAI, left=(WIDTH - H_MARGIN) // 2 + H_MARGIN, top=TOP_BUFFER,reveal_death=True,opponent=player1)

            #draw heat map values
            #draw heat map
            if (AI_INDX==2 and B_Heat_Map) or (AI_INDX==3 and B_Heat_Map):
                draw_prob_heat_vals(left=0,top=TOP_BUFFER)


            #draw Temp Ships during setup
            if Bool_Ship_Setup:
                draw_TEMP_ships(left = 0, top=TOP_BUFFER)

            #draw shot markers
            draw_grid_shots(playerAI,search=True, left = 0, top=TOP_BUFFER)
            draw_grid_shots(player1, search=True, left=(WIDTH-H_MARGIN)//2+H_MARGIN,top=TOP_BUFFER)

            #computer moves
            if not game.over and game.computer_turn and GameStarted:
                AI = AI_Meth[AI_INDX]
                if AI_INDX == 2 and len(playerAI.shotstaken)<1:  # probability
                    AI(initalize=True)
                    AI() #Play AI

                elif AI_INDX==3 and len(playerAI.shotstaken)<1:# prob + Mem and setup
                    AI(initalize=True,MemMode=True)
                    AI( MemMode=True)

                elif AI_INDX==3 and len(playerAI.shotstaken)>0: #play Mem mode
                    AI(MemMode=True)

                else:
                    AI() #normal Play AI

            #draw Text
            turn_title=smallfont.render('Player Board',True,WHITE,GREY)
            ttTRC=turn_title.get_rect()
            ttTRC.center = (((ttTRC.width/2)+ 10), TOP_BUFFER/2)
            SCREEN.blit(turn_title,ttTRC)

            turn_title=smallfont.render('Opponent Board',True,WHITE,GREY)
            ttTRC=turn_title.get_rect()
            ttTRC.center = ((WIDTH/2)+((ttTRC.width/2)+ 90), TOP_BUFFER/2)
            SCREEN.blit(turn_title,ttTRC)

            turn_title=smallfont.render('Shots Taken:',True,WHITE,GREY)
            ttTRC=turn_title.get_rect()
            ttTRC.center = ((WIDTH/2)-10, TOP_BUFFER+100)
            SCREEN.blit(turn_title,ttTRC)

            cur_turn = smallfont.render(str(len(player1.shotstaken)),True,WHITE,GREY)
            ctTTRC=cur_turn.get_rect()
            ctTTRC.center = (((WIDTH/2)-10)+(turn_title.get_width()/2+10), TOP_BUFFER+100)
            SCREEN.blit(cur_turn,ctTTRC)

            AI_Title = smallfont.render("AI Type:",True,WHITE,GREY)
            aitTTRC=AI_Title.get_rect()
            AIWIDTH=(BUTTON_WIDTH*3)-(AI_Title.get_width()/2)
            aitTTRC.center=((WIDTH-AIWIDTH),(HEIGHT-(BUTTON_HEIGHT*1-5)))
            SCREEN.blit(AI_Title,aitTTRC)

            AI_NAME=smallfont.render(AI_LIST[AI_INDX],True,WHITE,GREY)
            ainTTRC=AI_NAME.get_rect()
            ainTTRC.center=((WIDTH - AIWIDTH+((AI_NAME.get_width()/2)+50)),(HEIGHT-(BUTTON_HEIGHT*1-5)))
            SCREEN.blit(AI_NAME,ainTTRC)

            #cheating Check
            game.cheating=Ship_Agree_Show

            #game over message
            if game.over:
                if not toggle:
                    text = "Player "+str(game.result)+" wins!"
                    textbox = FinalFont.render(text,False,GREY,WHITE)
                    SCREEN.blit(textbox,((WIDTH//2-240),(HEIGHT//2-50)))
                looplim+=1
                pygame.time.wait(10)
                if looplim>=150:
                    looplim=0
                    toggle = not toggle
                StartOverBut.draw()
        #update
        #pygame.time.wait(250)
        pygame.display.flip()
