import random
import pandas as pd


class Ship:
    def __init__(self,size,row=None,col=None,orientation=None):
        self.row = random.randrange(0,9) if row is None else row
        self.col = random.randrange(0,9) if col is None else col
        self.size = size
        self.orientation = random.choice(["h","v"]) if orientation is None else orientation
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        start_index = self.row *10 +self.col
        if self.orientation == "h":
            return [start_index + i for i in range(self.size)]
        elif self.orientation == "v":
            return [start_index + i*10 for i in range(self.size)]

class Player:
    def __init__(self):
        self.ships = []
        self.search = ["U" for i in range(100)] #"U" stands for unknown
        self.ship_sizes=[5,4,3,3,2]
        self.place_ships(sizes=self.ship_sizes)
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]
        self.shotstaken=[]
        self.last_success_hit_index=0
        self.probability_board=None
        self.PlayerPlacedShips=False

    def save_ship_locations(self):
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]

    def place_ships(self,sizes,row=None,col=None,orientation=None):
        for size in sizes:
            placed = False #ship placed
            while not placed:

                #create new ship
                if row is None:
                    ship = Ship(size)
                    self.PlayerPlacedShips = False
                else:
                    ship = Ship(size=size,row=row,col=col,orientation=orientation)
                    self.PlayerPlacedShips = True

                #check if placement possible
                possible = True
                for i in ship.indexes:
                    #indexes must be less then 100 since we are 0 - 99
                    if i>=100:
                        possible=False
                        break

                    #check if ship goes over edge of board
                    new_row = i // 10
                    new_col = i % 10
                    if new_row != ship.row and new_col != ship.col:
                        possible=False
                        break

                    #check if ship is ontop of another ship
                    for other_ship in self.ships:
                        if i in other_ship.indexes:
                            possible=False
                            break
                #place ship
                if possible:
                    self.ships.append(ship)
                    self.save_ship_locations()
                    placed=True
                if not possible and row is not None:
                    placed=True

    def show_ships(self):
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        for row in range(11):
            print(" ".join(indexes[(row-1)*10:row*10]))

class Game:
    def __init__(self,play1,playAI,human1,human2,DB,AI_INDX):
        self.human1 = human1
        self.human2 = human2
        self.player1 = play1
        self.playerAI = playAI
        self.AIType=AI_INDX
        self.player1_turn=True
        self.computer_turn = True if not self.human1 else False
        self.over = False
        self.result = None
        self.DB=DB
        self.cheating=False

        #prob+Mem setting
        try:
            self.MemoryInfluence= self.DB.MemoryInfluence #overall memory inpact on prediction board, so if highest start value is 100 the max influence is 50 pnts
            self.PlacedShipMemoryInfluence = self.DB.PlacedShipMemoryInfluence #Weighted heavier for player placed ships over random
            self.PlayerMemoryInfluence = self.DB.PlayerMemoryInfluence # favor more player placements over all others
        except:
            self.MemoryInfluence=.5 #overall memory inpact on prediction board, so if highest start value is 100 the max influence is 50 pnts
            self.PlacedShipMemoryInfluence = .75 #Weighted heavier for player placed ships over random
            self.PlayerMemoryInfluence = .65 # favor more player placements over all others

        self.playerMemMap={}
        self.opMemMap= {}
        self.maxinfluenceval=0


    def make_move(self,i):
        player = self.player1 if self.player1_turn else self.playerAI
        opponent = self.playerAI if self.player1_turn else self.player1

        player.shotstaken.append(i)
        #set miss 'M' or hit 'H'
        if i in opponent.indexes:
            player.search[i] = "H"
            player.last_success_hit_index = i

            #Check if ship sunk 'S'
            for ship in opponent.ships:
                sunk = True
                for i in ship.indexes:
                    if player.search[i] == "U":
                        sunk = False
                        break
                if sunk:
                    for i in ship.indexes:
                        player.search[i]="S"

        else:
            player.search[i] = "M"


        #check for game over
        game_over = True
        for i in opponent.indexes:
            if player.search[i] == "U":
                game_over=False
                break

        self.over = game_over
        self.result = "1" if self.player1_turn else "AI"

        #if game over save game data
        if game_over:
            self.save_game()

        #change team
        self.player1_turn = not self.player1_turn

        #switch between humand and computer
        if self.human1 and not self.human2 or not self.human1 and self.human2:
            self.computer_turn = not self.computer_turn

    def save_game(self):
        if not self.cheating and self.DB!=None and self.DB.connected:
            db = self.DB
            winner = None
            if self.result=="1":
                winner=0 #Player
            else:
                winner=1 #AI
            gwinner = winner
            placedShips = self.player1.PlayerPlacedShips
            pships = self.player1.indexes
            pSHIPpos = self.player1.ships
            pshots = self.player1.shotstaken
            AItype = self.AIType
            AIShips = self.playerAI.indexes
            AIshots = self.playerAI.shotstaken
            db.create_game_doc(gwinner,placedShips,pships,pSHIPpos,pshots,AItype,AIShips,AIshots)

    def random_ai(self):
        player = self.player1 if self.player1_turn else self.playerAI
        search = player.search #self.player1.search if self.player1_turn else self.playerAI.search
        unknown = [i for i, square in enumerate(search) if square =="U"]
        unknown = list(filter((player.shotstaken).__ne__,unknown))
        if len(unknown)>0:
            randomindex = random.choice(unknown)
            self.make_move(randomindex)

    def basic_ai(self):
        #setup
        player = self.player1 if self.player1_turn else self.playerAI
        search = player.search # self.player1.search if self.player1_turn else self.playerAI.search
        unknown = [i for i, square in enumerate(search) if square =="U"]
        hits = [i for i, square in enumerate(search) if square =="H"]

        #search in neighborhood of hits
        unknown_with_neighbors_hits = []
        unknown_with_neighbors_hits2=[]
        for u in unknown:
            if u+1 in hits or u-1 in hits or u+10 in hits or u-10 in hits:
                unknown_with_neighbors_hits.append(u)
            if u+2 in hits or u-2 in hits or u+20 in hits or u-20 in hits:
                unknown_with_neighbors_hits2.append(u)
        #pick 'U' square with direct and level2 neigh both marked as 'H'
        hit_choice=[]
        for u in unknown:
            if u in unknown_with_neighbors_hits and u in unknown_with_neighbors_hits2:
                hit_choice.append(u)
            if len(hit_choice)>0:
                self.make_move(random.choice(hit_choice))
                return
        #pick 'U' square that has a lvl 1 neighbor marked as 'H'
        if len(unknown_with_neighbors_hits)>0:
            self.make_move(random.choice(unknown_with_neighbors_hits))
            return

        #checkerboard pattern
        checker_board=[]
        for u in unknown:
            row = u//10
            col = u%10
            if (row+col)%2 ==0:
                checker_board.append(u)
        checker_board = list(filter((player.shotstaken).__ne__,checker_board))
        if len(checker_board)>0:
            self.make_move(random.choice(checker_board))
            return

        #random move
        self.random_ai()

    def basic_ai_v2(self):
        # setup
        player = self.player1 if self.player1_turn else self.playerAI
        opponent = self.player1 if not self.player1_turn else self.playerAI
        search = player.search  # self.player1.search if self.player1_turn else self.playerAI.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # search in neighborhood of hits
        unknown_with_neighbors_hits = []
        unknown_with_neighbors_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbors_hits.append(u)
            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                unknown_with_neighbors_hits2.append(u)
        # pick 'U' square with direct and level2 neigh both marked as 'H'
        hit_choice = []
        for u in unknown:
            if u in unknown_with_neighbors_hits and u in unknown_with_neighbors_hits2:
                hit_choice.append(u)
            if len(hit_choice) > 0:
                self.make_move(random.choice(hit_choice))
                return
        # pick 'U' square that has a lvl 1 neighbor marked as 'H'
        if len(unknown_with_neighbors_hits) > 0:
            self.make_move(random.choice(unknown_with_neighbors_hits))
            return

        # checkerboard pattern
        checker_board = []
        #check for smallest unit still sailing
        smallest_known_ship=2
        shots_fired = player.shotstaken
        ship_still_alive=[]
        for ship in opponent.ships:
            check = all(item in shots_fired for item in ship.indexes)
            if not check:
                ship_still_alive.append(ship.indexes)
        ship_still_alive.sort(key=len)
        smallest_known_ship=len(ship_still_alive[0])

        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % smallest_known_ship == 0:
                checker_board.append(u)
        checker_board = list(filter((player.shotstaken).__ne__, checker_board))
        if len(checker_board) > 0:
            self.make_move(random.choice(checker_board))
            return

        # random move
        self.random_ai()

    def basic_ai_v3(self):
        # setup
        player = self.player1 if self.player1_turn else self.playerAI
        opponent = self.player1 if not self.player1_turn else self.playerAI
        search = player.search  # self.player1.search if self.player1_turn else self.playerAI.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # search in neighborhood of hits
        lhi = player.last_success_hit_index
        if lhi not in hits and len(hits)>0:
           lhi=hits[0]
        l_hit_row = lhi//10
        l_hit_col = lhi%10

        unknown_with_neighbors_hits = []
        unknown_with_neighbors_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                if (u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0)):
                    unknown_with_neighbors_hits.append(u)

            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                if (u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0)):
                    unknown_with_neighbors_hits2.append(u)

        # pick 'U' square with direct and level2 neigh both marked as 'H'
        hit_choice = []
        for u in unknown:
            if u in unknown_with_neighbors_hits and u in unknown_with_neighbors_hits2:
                hit_choice.append(u)
        if len(hit_choice) > 0:
            self.make_move(random.choice(hit_choice))
            return
        # pick 'U' square that has a lvl 1 neighbor marked as 'H'
        if len(unknown_with_neighbors_hits) > 0:
            self.make_move(random.choice(unknown_with_neighbors_hits))
            return

        # checkerboard pattern
        checker_board = []
        #check for smallest unit still sailing
        smallest_known_ship=2
        shots_fired = player.shotstaken
        ship_still_alive=[]
        for ship in opponent.ships:
            check = all(item in shots_fired for item in ship.indexes)
            if not check:
                ship_still_alive.append(ship.indexes)
        ship_still_alive.sort(key=len)
        smallest_known_ship=len(ship_still_alive[0])

        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        checker_board = list(filter((player.shotstaken).__ne__, checker_board))
        if len(checker_board) > 0:
            target= random.choice(checker_board)
            board_check=[]
            target_sel=False
            while not target_sel:
                #now check if smallest ship could be in this target zone
                target_sel = True
                row = target // 10
                col = target % 10
                row_ship_count=0
                col_ship_count=0
                for x in range(smallest_known_ship):
                    if row == ((target+x)//10) and (target+x) in unknown:
                        row_ship_count+=1
                    else:
                        break

                for x in range(smallest_known_ship):
                    if row == ((target-x)//10) and (target-x) in unknown and target != (target-x):
                        row_ship_count+=1
                    elif target != (target-x):
                        break

                for x in range(smallest_known_ship):
                    if col == ((target+(x*10))%10) and (target+(x*10)) in unknown:
                        col_ship_count+=1
                    else:
                        break

                for x in range(smallest_known_ship):
                    if col == ((target-(x*10))%10) and (target-(x*10)) in unknown and target!=(target-(x*10)):
                        col_ship_count+=1
                    elif target!=(target-(x*10)):
                        break

                if row_ship_count< smallest_known_ship and col_ship_count<smallest_known_ship:
                    target_sel=False

                if not target_sel:
                    if target not in board_check: board_check.append(target)
                    target = random.choice(checker_board)
                    if len(checker_board) == len(board_check):
                      break

            self.make_move(target)
            return

        # random move
        self.random_ai()

    def basic_ai_random(self):
        #setup
        player = self.player1 if self.player1_turn else self.playerAI
        search = player.search # self.player1.search if self.player1_turn else self.playerAI.search
        unknown = [i for i, square in enumerate(search) if square =="U"]
        hits = [i for i, square in enumerate(search) if square =="H"]

        #search in neighborhood of hits
        unknown_with_neighbors_hits = []
        unknown_with_neighbors_hits2=[]
        for u in unknown:
            if u+1 in hits or u-1 in hits or u+10 in hits or u-10 in hits:
                unknown_with_neighbors_hits.append(u)
            if u+2 in hits or u-2 in hits or u+20 in hits or u-20 in hits:
                unknown_with_neighbors_hits2.append(u)
        #pick 'U' square with direct and level2 neigh both marked as 'H'
        hit_choice=[]
        for u in unknown:
            if u in unknown_with_neighbors_hits and u in unknown_with_neighbors_hits2:
                hit_choice.append(u)
            if len(hit_choice)>0:
                self.make_move(random.choice(hit_choice))
                return
        #pick 'U' square that has a lvl 1 neighbor marked as 'H'
        if len(unknown_with_neighbors_hits)>0:
            self.make_move(random.choice(unknown_with_neighbors_hits))
            return

        #random move
        self.random_ai()

    def placement_check(self,ship,unknown):
        # check if indexes are possible
        possible = True
        for i in ship.indexes:
            # indexes must be less then 100 since we are 0 - 99
            if i >= 100:
                possible = False
                break

            # check if ship goes over edge of board
            new_row = i // 10
            new_col = i % 10
            if new_row != ship.row and new_col != ship.col:
                possible = False
                break

            # check if ship is able to fit in space
            if i not in unknown:
                possible=False
                break

        # place ship
        if possible:
            return True # gain point
        else:
            return False

    def probability_generate_score(self,ship_still_alive,unknown,index):
        points=0
        row = index // 10
        col = index % 10
        # ship sizes
        for s in ship_still_alive:
            ship_length = len(s)
            v_check=True
            h_check=True
            for p in range(ship_length):
                # horizontal check
                new_ind_h = Ship(ship_length, row=row, col=(col - p), orientation='h')
                ship_check = self.placement_check(new_ind_h, unknown)
                if ship_check: points += 1

                # vertical check
                new_ind_v = Ship(ship_length, row=(row - p), col=col, orientation='v')
                ship_check = self.placement_check(new_ind_v, unknown)
                if ship_check: points += 1
                else: v_check=False
        return points

    def probability_ai(self,initalize=False,MemMode=False):
        # get most probabilistic locations
        player = self.player1 if self.player1_turn else self.playerAI
        opponent = self.player1 if not self.player1_turn else self.playerAI
        if player.probability_board==None: initalize=True
        if not initalize:
            fin_max = max(player.probability_board, key=player.probability_board.get)
            top_target_indexes = [k for k, v in player.probability_board.items() if
                                  v == player.probability_board.get(fin_max)]

            self.make_move(random.choice(top_target_indexes))

        if not self.over: #if game isn't over predict next move
            search = player.search  # self.player1.search if self.player1_turn else self.playerAI.search
            unknown = [i for i, square in enumerate(search) if square == "U"]
            hits = [i for i, square in enumerate(search) if square == "H"]

            #ships still alive
            shots_fired = player.shotstaken
            ship_still_alive = []
            for ship in opponent.ships:
                check = all(item in shots_fired for item in ship.indexes)
                if not check:
                    ship_still_alive.append(ship.indexes)
            ship_still_alive.sort(key=len)
            smallest_known_ship = len(ship_still_alive[0])
            largest_known_ship = len(ship_still_alive[-1])
            ship_still_alive.sort(key=len,reverse=True)

            #create probability grid
            search_dic ={} #search dictonary
            for i in range(100):
                search_dic[i]=0

            if len(hits)>0: #check hits first
                # now check for hits
                extra_points = 50
                if len(hits)>1:#find the line
                    mini_search = []
                    ms2=[]

                    for h in hits:
                        l_hit_row = h // 10
                        l_hit_col = h % 10
                        firstorder_row = 1
                        firstorder_col = 10
                        secondorder_row = firstorder_row * 2
                        secondorder_col = firstorder_col * 2

                        t1=(h - firstorder_row)
                        t2=(h + firstorder_row)
                        t3=(h - firstorder_col)
                        t4=(h + firstorder_col)

                        t5= (h - secondorder_row)
                        t6=(h + secondorder_row)
                        t7=(h - secondorder_col)
                        t8=(h + secondorder_col)

                        u=t1
                        if t1 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): mini_search.append(t1)
                        u = t2
                        if t2 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): mini_search.append(t2)
                        u = t3
                        if t3 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): mini_search.append(t3)
                        u = t4
                        if t4 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): mini_search.append(t4)

                        u = t5
                        if t5 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): ms2.append(t5)
                        u = t6
                        if t6 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): ms2.append(t6)
                        u = t7
                        if t7 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): ms2.append(t7)
                        u = t8
                        if t8 in unknown and ((u//10)==l_hit_row or ((u%10)==l_hit_col and ((u%10)<=9 or (u%10)>=0))): ms2.append(t8)

                    mini_search.sort()
                    for ms in mini_search:
                        if ms not in hits:
                                search_dic[ms] = search_dic.get(ms) + self.probability_generate_score(ship_still_alive, unknown, ms) +(extra_points/2)
                    for ms in ms2:
                        if ms in mini_search and ms not in hits:
                            if (ms // 10) == l_hit_row or ((ms % 10) == l_hit_col and ((ms % 10) <= 9 or (ms % 10) >= 0)):
                                search_dic[ms] = search_dic.get(ms) + self.probability_generate_score(ship_still_alive,unknown, ms)+extra_points
                else:
                    for h in hits:
                        row = h // 10
                        col = h % 10
                        firstorder_row = 1
                        firstorder_col = 10

                        t1 = h - firstorder_row
                        search_dic[t1]=self.probability_generate_score(ship_still_alive,unknown,t1)
                        t2 = h + firstorder_row
                        search_dic[t2] = self.probability_generate_score(ship_still_alive, unknown, t2)
                        t3 = h - firstorder_col
                        search_dic[t3] = self.probability_generate_score(ship_still_alive, unknown, t3)
                        t4 = h + firstorder_col
                        search_dic[t4] = self.probability_generate_score(ship_still_alive, unknown, t4)

                        # check if surroundings are in unknown, if so add major points to focus these spaces
                        if t1 in unknown and (row == (t1 // 10) or col == (t1 % 10)): search_dic[t1] = (
                            (search_dic.get(t1) + extra_points))
                        if t2 in unknown and (row == (t2 // 10) or col == (t2 % 10)): search_dic[t2] = (
                            (search_dic.get(t2) + extra_points))
                        if t3 in unknown and (row == (t3 // 10) or col == (t3 % 10)): search_dic[t3] = (
                            (search_dic.get(t3) + extra_points))
                        if t4 in unknown and (row == (t4 // 10) or col == (t4 % 10)): search_dic[t4] = (
                            (search_dic.get(t4) + extra_points))
            else:
                for u in unknown:
                #go through each possible ship type and how many ways it can fit into this square
                        # get and save points for index
                        search_dic[u]=self.probability_generate_score(ship_still_alive,unknown,u)

            if initalize and MemMode: #if we are setting up and in mem mode load map
                self.MakeMemBoards()
                self.maxinfluenceval= search_dic[max(search_dic, key=search_dic.get)]

            if MemMode:# add memory influence
                pmemmap = self.playerMemMap
                omemmap = self.opMemMap
                memmap = {}
                for i in range(0,100):
                    pi = pmemmap[i] * self.PlayerMemoryInfluence  # player influence
                    oi = omemmap[i] * (1 - self.PlayerMemoryInfluence)  # other player influence
                    val = round(pi + oi)
                    memmap[i]=val
                mIv = self.MemoryInfluence * self.maxinfluenceval #max Influence Value
                for i in range(0,100):
                    memval = memmap[i]
                    if memval>mIv: memval=mIv
                    if search_dic[i]!=0:search_dic[i] = search_dic[i]+memval

            player.probability_board=search_dic
        return

    def MakeMemBoards(self):
        #get past games
        db = self.DB
        db.process_prev_games()
        gamedata = db.gamedf.copy()
        gamedata['date']=pd.to_datetime(gamedata['date'])
        gamedata=gamedata.sort_values(by='date',ascending=False)
        playershipindex = gamedata['playershipindx']
        masterindx=[] #all players all placement type indexs
        for item in playershipindex:
            masterindx = masterindx+item

        usernametmp = self.DB.UserInfo.USERID
        gamequery = gamedata[(gamedata.userID==usernametmp)&(gamedata.userPlacedShips==True)]
        playerplacedshipindexPShips = gamequery['playershipindx'] #player placed ships
        ppshipindx=[] #player placed ships index only
        for item in playerplacedshipindexPShips:
            ppshipindx = ppshipindx+item

        gamequery = gamedata[(gamedata.userID==usernametmp)&(gamedata.userPlacedShips==False)]
        playerrandshipindexPShips = gamequery['playershipindx'] #player random placed ships
        pprshipindx=[] #player placed random ships index only
        for item in playerrandshipindexPShips:
            pprshipindx = pprshipindx+item

        gamequery = gamedata[(gamedata.userID!=usernametmp)&(gamedata.userPlacedShips==True)]
        othersshipindexPShips = gamequery['playershipindx']  # other players placed ships
        opshipindx = []  # player placed ships index only
        for item in othersshipindexPShips:
            opshipindx = opshipindx+item

        gamequery = gamedata[(gamedata.userID!=usernametmp)&(gamedata.userPlacedShips==False)]
        otherrandshipindexPShips = gamequery['playershipindx']  # other player random placed ships
        oprshipindx = []  # other player placed random ships index only
        for item in otherrandshipindexPShips:
            oprshipindx = oprshipindx+item

        allpopularindxes={} #All ship popular index
        pppI={} #player placed popular indexs
        prpI={} #player Random popular indexs
        opppI={} #other player placed popular indexs
        oprpI={} #other player random popluar indexs
        for i in range(0,100):
            allpopularindxes[i]=masterindx.count(i)
            pppI[i]=ppshipindx.count(i)  # player placed popular indexs
            prpI[i] = pprshipindx.count(i)  # player Random popular indexs
            opppI[i] = opshipindx.count(i)  # other player placed popular indexs
            oprpI[i] = oprshipindx.count(i)  # other player random popluar indexs

        #Create Single Player and Otherplayers map

        for i in range(0,100):
            #player map
            ppiv = pppI[i] * self.PlacedShipMemoryInfluence  # player placed popular indexs
            prpiv = prpI[i] * (1-self.PlacedShipMemoryInfluence)  # player Random popular indexs
            val = round(ppiv+prpiv)
            self.playerMemMap[i]=val

            #other players map
            oppiv = opppI[i] * self.PlacedShipMemoryInfluence   # other player placed popular indexs
            oprpiv = oprpI[i] * (1-self.PlacedShipMemoryInfluence)  # other player random popluar indexs
            val2 = round(oppiv+oprpiv)
            self.opMemMap[i]=val2
        return

    def advance_ai(self):
        return