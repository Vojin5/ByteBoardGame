from art import *
from tabulate import tabulate

# Dodati enum za ovo kasnije
GL = 0
GD = 1
DL = 2
DD = 3

def start_game():
    stacks = [0,0] # [white_stacks , black_stacks]
    tprint("[------BYTE------]")
    board = []
    n = dimension_input_validate()
    figure = choose_figure()
    gameType = input("PVP ili PVC")
    opponent = "W" if figure == "B" else "B"
    set_start_state(board, n)
    drawBoard(board, n)
    player = "W"
    
    drawCounter = 0
    while not is_game_finished(n,stacks):
        if drawCounter == 2:
            tprint("Draw")
            break
        print(player + " is on turn ")
        turnDone = False
        while not turnDone:
            if(len(getGameStates(board,n,player)) != 0): # da li ima poteza
                if gameType == "PVP":
                    move = readPosition(board,n,player) # cita se potez igraca
                else:
                    if player == figure:
                        move = readPosition(board,n,player) # cita se potez igraca
                    else:
                        try:
                            move = minMax(board,5,True,opponent,stacks,n)
                            print(move)
                        except Exception as e:
                            print(e)
                        move = move[1]
                
                if move[2] in getMoves(board,move[0],move[1],n): # ukoliko je moguc potez
                    if makeMove(move,board):
                        turnDone = True
                        drawCounter = 0
                        checkBoard(board,n,stacks)
                        drawBoard(board,n)
                else:
                    print("Uneti potez nije optimalan za stanje igre")
            else:
                 turnDone = True
                 print("Trenutni igrac nema mogucih poteza")     
                 drawCounter = drawCounter + 1
        if(player == 'W'):
            player = 'B'
        else:
            player = 'W'

def checkDirection(position_i,position_j,direction,n,price,source):
    #funkcija proverava da li za datu poziciju moze da se krece u tom smeru i povecava cenu puta za 1 pri cemu source
    #odnosno izvorni prvi smer od pocetnog polja se propagira dalje kako bi kasnije vratili jer nam je on jedini od interesa
    #jer se krecemo u tom smeru od pocetnog polja
    if direction == 0 and (position_i - 1 < 0 or position_j - 1 < 0):
                    return False
    if direction == 1 and (position_i - 1 < 0 or position_j + 1 > (n-1)):
                    return False
    if direction == 2 and (position_j - 1 < 0 or position_i + 1 > (n-1)):
                    return False
    if direction == 3 and (position_i + 1 > (n-1) or position_j + 1 > (n-1)):
                    return False
    if direction == 0:
         return [position_i-1,position_j-1,price+1,source]
    if direction == 1:
         return [position_i-1,position_j+1,price+1,source]
    if direction == 2:
         return [position_i+1,position_j-1,price+1,source]
    if direction == 3:
         return [position_i+1,position_j+1,price+1,source]
         
#ova funkcija vraca smerove u kojima moze da se krece trenutni stack ali ne i da li je taj potez izvodiv.Od pocetne pozicije se krecemo u svim smerovima
#ukoliko je polje prazno i od njega se sirimo u svim pravcima,ukoliko je neki stek onda proveravamo da li cena puta do njega je najmanja do sad
#ukoliko jeste onda kreiramo novi niz sa tim smerom i dodajemo ga u finalstates,ukoliko je to polje sa istom cenom koja vec postoji onda samo taj smer
#dodajemo u postojecu listu kako bi na kraju imali vise dostupnih smerova sa istom cenom
#ukoliko je polje na vecoj ceni od prethodnih odbacuje se
#rezultat funkcije su svi smerovi u kojima moze da se krece dato polje
def getMoves(board,position_i,position_j,n):
    open_states = list()
    final_states = list()
    currentCost = n*n # trazimo najblizi stek i ovde se skadisti trenutno najblizi kako bi ostali znali da li su nasli blizi stek
    # Stanje : [pos_i,pos_j,cena puta]
    # Ukoliko je kretanje u tom smeru moguce prihvaticemo taj korak kao novo stanje
    # Cilj je pronaci prvi stek krecuci se u svim dostupnim smerovima i prihvatiti smerove koji vode do najblizeg steka/stekova
    starter_i = position_i
    starter_j = position_j
    newState = checkDirection(position_i,position_j,0,n,0,0)
    if newState != False:
        open_states.append(newState)
    newState = checkDirection(position_i,position_j,1,n,0,1)
    if newState != False:
        open_states.append(newState)
    newState = checkDirection(position_i,position_j,2,n,0,2)
    if newState != False:
        open_states.append(newState)
    newState = checkDirection(position_i,position_j,3,n,0,3)
    if newState != False:
        open_states.append(newState)
    # U ovom trenutku imamo pocetno stanje gde su svi smerovi u kojima se mozemo kretati iz datog polja
    while len(open_states) > 0:
        currentState = open_states.pop() # izvlaci i brise iz liste
        # slucaj da smo pronasli polje sa stekom
        # i da to polje nije pocetno polje od koga smo krenuli
        if board[currentState[0]][currentState[1]] != "" and board[currentState[0]][currentState[1]] != None and not(currentState[0] == starter_i and currentState[1] == starter_j):
            if currentState[2] < currentCost: # slucaj da smo nasli stek na manjem rastojanju,kreiramo novi niz sa samo tim pocetnim smerom
                  final_states = [currentState[3]] 
                  currentCost = currentState[2] # postavljamo najnizu cenu
            if currentState[2] == currentCost: # slucaj da smo nasli stek sa istim rastojanjem kao trenutno najblizi (ako postoje vise puteva sa na istoj udaljenosti)
                 if currentState[3] not in final_states:
                    final_states.append(currentState[3]) # samo dodajemo taj izvor tj smer ali ne pravimo novi niz jer je cena ista
        if board[currentState[0]][currentState[1]] == "" or board[currentState[0]][currentState[1]] == None: # Slucaj da je polje prazno,sada treba dodati sve moguce pozicije na koje mozemo otici
            if currentState[2] <= currentCost:     # Ne zelimo da obradjujemo puteve koji su vec duzi od najkraceg jer ih necemo uzeti svakako
                #sada dodajemo sve smerove u kojima mozemo da se krecemo od tog praznog polja
                newState = checkDirection(currentState[0],currentState[1],0,n,currentState[2],currentState[3])
                if newState != False:
                    open_states.append(newState)
                newState = checkDirection(currentState[0],currentState[1],1,n,currentState[2],currentState[3])
                if newState != False:
                    open_states.append(newState)
                newState = checkDirection(currentState[0],currentState[1],2,n,currentState[2],currentState[3])
                if newState != False:
                    open_states.append(newState)
                newState = checkDirection(currentState[0],currentState[1],3,n,currentState[2],currentState[3])
                if newState != False:
                    open_states.append(newState)
    return final_states # vracamo samo smerove u kome sme da se krece

def fill_board_default(board, n):
    for i in range(0, n):
        board.append([])
        for j in range(0, n):
            board[i].append(None)


def set_start_state(board, n):
    fill_board_default(board, n)
    first = False
    second = True

    for i in range(1, n - 1):
        for j in range(0, n):
            if second:
                if j % 2 == 0:
                    board[i][j] = None
                else:
                    board[i][j] = 'B'
            if first:
                if j % 2 == 0:
                    board[i][j] = 'W'
                else:
                    board[i][j] = None
        pom = first
        first = second
        second = pom


def dimension_input_validate():
    n = None
    print('Unesite dimenziju table')
    while True:
        try:
            n = int(input())
            if (n < 8 or n > 16) or ((n - 2) * (n / 2)) % 8 != 0:
                print('Unesite broj u opsegu od [8, 16] gde je ukupan broj figura na tabli deljiv sa 8')
            else:
                return n
        except:
            print('Unesite broj u opsegu od [8, 16] gde je ukupan broj figura na tabli deljiv sa 8')


def choose_figure():
    figure = ''
    while True:
        print('Izaberite igraca W ili B')
        figure = input()
        if figure == 'W' or figure == 'B':
            return figure

def silent_is_game_finished(n,stacks):
    stacks_to_win = int(((((n - 2) * (n / 2)) / 8) / 2) + 1)

    if stacks[0] == stacks_to_win:
        return "W"
    if stacks[1] == stacks_to_win:
        return "B"
    return False

def is_game_finished(n,stacks):
    stacks_to_win = int(((((n - 2) * (n / 2)) / 8) / 2) + 1)

    if stacks[0] == stacks_to_win:
        tprint("White player has won")
        return True
    if stacks[1] == stacks_to_win:
        tprint("Black player has won")
        return True
    return False

def silent_checkBoard(board,n,stacks):
    adventage = None
    for i in range(0,n):
        for j in range(0,n):
            if board[i][j] is not None and len(board[i][j]) == 8:
                if board[i][j][7] == 'W':
                    stacks[0] = stacks[0] + 1
                    adventage = "W"
                else:
                    stacks[1] = stacks[1] + 1
                    adventage = "B"
                board[i][j] = ""
    return adventage

def checkBoard(board,n,stacks):
    for i in range(0,n):
        for j in range(0,n):
            if board[i][j] is not None and len(board[i][j]) == 8:
                if board[i][j][7] == 'W':
                    stacks[0] = stacks[0] + 1
                    print("White player got a stack")
                else:
                    stacks[1] = stacks[1] + 1
                    print("Black player got a stack")
                board[i][j] = ""

def readPosition(board,n,turn):
        stack_place = 0
        while True:
            try:
                #Unos se splituje na dve vrednosti koje dalje ispitujemo da li odgovaraju u odnosu na tablu
                position = input("Unesite lokaciju polja u formatu:BRVRSTE BRKOLONE  ")
                if position == "list": #radi testiranja,nepotrebni deo trenutno
                    stanja = getGameStates(board,n,turn)
                    for (x,y) in stanja:
                        print(y)
                    position = input("Unesite lokaciju polja u formatu:BRVRSTE BRKOLONE  ")
                position = position.split(' ') #split na osnovu razmaka
                position_i = int(position[0]) - 1 #1-based da se pretvori u 0-based
                position_j = int(position[1]) - 1
                #prevelika vrsta,premala vrsta,premala kolona,prevelika kolona, vrednost na tabli je None
                if position_i > n or position_i < 0 or position_j < 0 or position_j > n or board[position_i][position_j] == None:
                    print("Neispravan unos polja,pokusajte ponovo")
                else:
                    #ukoliko duzina steka je samo 1 onda nema potrebe da pitamo korisnika od koje figure ce da prenosi
                    stack_length = len(board[position_i][position_j])
                    if stack_length == 1:
                        picked_stack = board[position_i][position_j] # uzimamo string sa tog polja
                        picked_stack = picked_stack[0] # 0 jer je stack_length = 1
                        # da slucajno korisnik nije izabrao polje sa suprotnom figurom
                        if picked_stack != turn:
                            print("Ovo polje ne sadrzi vasu boju,odaberite polje ponovo")
                        else:
                            break
                    # Ukoliko postoji stek sa velicinom vecom od 1 ali tu se ne nalaze figure trenutnog igraca
                    elif not turn in board[position_i][position_j]:
                        print("na zadatom polju se ne nalazi figura vase boje")
                    #Korisnik unosi od koje pozicije hoce da nosi stek
                    else:
                        while True:
                            try:
                                stack_place = input("Unesite poziciju steka za pomeranje kao vrednosti od 1-8 ")
                                stack_place = int(stack_place) - 1 #1-based to 0-based
                                if stack_place < 0 or stack_place > 8 or stack_place > stack_length:
                                    print("Neispravan unos stek pozicije,pokusajte ponovo")
                                    continue
                                picked_stack = board[position_i][position_j] # uzimamo string sa te pozicije na tabli
                                picked_stack = picked_stack[stack_place] # uzimamo figuru od koje se uzima stek na dalje da bi proverili da li taj igrac moze da 
                                #odigra taj stack tj da ne odigra protivnicku figuru
                                if picked_stack != turn:
                                    print("Odabrali ste protivnicku figuru,pokusajte ponovo")
                                else:
                                    break
                            except:
                                print("Neispravan unos stek pozicije,pokusajte ponovo")
                        break
            except:
                print("Neispravan unos polja,pokusajte ponovo")
        while True:
            try:
                #provera smera
                direction = input("Unesite smer kretanja kao jedan od ponudjenjih : <GoreLevo - 0, GoreDesno - 1, DoleLevo - 2, DoleDesno - 3>")
                direction = int(direction)
                if direction < 0 or direction > 3:
                    print("Neispravan smer,pokusajte ponovo")
                    continue
                if direction == 0 and (position_i - 1 < 0 or position_j - 1 < 0):
                    print("Nedozvoljen smer,pokusajte ponovo")
                    continue
                if direction == 1 and (position_i - 1 < 0 or position_j + 1 > (n-1)):
                    print("Nedozvoljen smer,pokusajte ponovo")
                    continue
                if direction == 2 and (position_j - 1 < 0 or position_i + 1 > (n-1)):
                    print("Nedozvoljen smer,pokusajte ponovo")
                    continue
                if direction == 3 and (position_i + 1 > (n-1) or position_j + 1 > (n-1)):
                    print("Nedozvoljen smer,pokusajte ponovo")
                    continue
                else:
                    break
            except:
                print("Neispravan smer,pokusajte ponovo")
        return (position_i,position_j,direction,stack_place)

#potpuno isto kao make move samo bez printova za potrebe funkcije get game states
def tryMakeMove(move,board):
    start = board[move[0]][move[1]] #temp promenljiva za pocetnu lokaciju
    start = start[move[3]:] # ucitavamo stek od figure koja je izabrana pa na gore (stek koji pomeramo)
    end_i = None
    end_j = None
    if move[2] == 0: # trazimo na osnovu direction gde cemo pomeriti tekuci stack
        end_i = move[0] - 1
        end_j = move[1] - 1
    if move[2] == 1:
        end_i = move[0] - 1
        end_j = move[1] + 1
    if move[2] == 2:
        end_i = move[0] + 1
        end_j = move[1] - 1
    if move[2] == 3:
        end_i = move[0] + 1
        end_j = move[1] + 1
    #Patch za prvu i poslednju vrstu kako bi bile igrive i ako inicijalno nemaju vrednost postavljenu
    if board[end_i][end_j] == None:
        board[end_i][end_j] = ""
    destinationLength = len(board[end_i][end_j])
    # da li je stek koji pomeramo prevelik za odredisni kao i da li narusava pravilo da se element
    # sa vece visine spusta na nizu
    if (destinationLength + len(start)) > 8: 
        return False
    if destinationLength != 0: #ukoliko je odredisni stek prazan nema potrebe proveravati nivoe 
        if (move[3]+1) > destinationLength:
            return False
    # ukoliko se krece na prazno polje ne moze se ici delom steka vec celim stekom
    if destinationLength == 0:
        if move[3] != 0:
            return False
    board[end_i][end_j] = board[end_i][end_j] + (start) # na odrediste nalepimo stek koji pomeramo
    board[move[0]][move[1]] = board[move[0]][move[1]][:move[3]] # mesto sa kojeg smo pomerili skratimo za stek koji je pomeren
    return True

def makeMove(move,board):
    start = board[move[0]][move[1]] #temp promenljiva za pocetnu lokaciju
    start = start[move[3]:] # ucitavamo stek od figure koja je izabrana pa na gore (stek koji pomeramo)
    end_i = None
    end_j = None
    if move[2] == 0: # trazimo na osnovu direction gde cemo pomeriti tekuci stack
        end_i = move[0] - 1
        end_j = move[1] - 1
    if move[2] == 1:
        end_i = move[0] - 1
        end_j = move[1] + 1
    if move[2] == 2:
        end_i = move[0] + 1
        end_j = move[1] - 1
    if move[2] == 3:
        end_i = move[0] + 1
        end_j = move[1] + 1
    #Patch za prvu i poslednju vrstu kako bi bile igrive i ako inicijalno nemaju vrednost postavljenu
    if board[end_i][end_j] == None:
        board[end_i][end_j] = ""
    destinationLength = len(board[end_i][end_j])
    # da li je stek koji pomeramo prevelik za odredisni kao i da li narusava pravilo da se element
    # sa vece visine spusta na nizu
    if (destinationLength + len(start)) > 8: 
        print("Odabrani stek premasuje maksimalnu velcinu steka,odaberite drugi potez")
        return False
    if destinationLength != 0: #ukoliko je odredisni stek prazan nema potrebe proveravati nivoe 
        if (move[3]+1) > destinationLength: #pravilo da se dno steka ne moze pomerati na nizi ili isti nivo 
            print("Stek koji zelite pomeriti je na vecoj visini od odredisnog")
            return False
    # ukoliko se krece na prazno polje ne moze se ici delom steka vec celim stekom
    if destinationLength == 0:
        if move[3] != 0:
            print("Ne mozete pomeriti deo steka na prazno polje vec uvek ceo,pokusajte ponovo")
            return False
    board[end_i][end_j] = board[end_i][end_j] + (start) # na odrediste nalepimo stek koji pomeramo
    board[move[0]][move[1]] = board[move[0]][move[1]][:move[3]] # mesto sa kojeg smo pomerili skratimo za stek koji je pomeren
    return True


def drawBoard(board, n):
    startLetter = 'A'
    newBoard = []
    numberArray = []
    for number in range(0,n+1):
        if number == 0:
            numberArray.append("/")
        else:
            numberArray.append([number])
    newBoard.append(numberArray)
    for indX,x in enumerate(board):
        newRow = [startLetter]
        startLetter = chr(ord(startLetter)+1)
        for indY,y in enumerate(x):
            if y == None:
                if indX == 0:
                    if indY%2==0:
                        newRow.append("...\n...\n...\n")
                    else:
                        newRow.append(None)
                elif indX is n-1:
                    if indY%2==0:
                        newRow.append(None)
                    else:
                        newRow.append("...\n...\n...\n")
                else:
                    newRow.append(None)
            else:
                y = y.ljust(9,'.')
                arr1 = y[:3] + '\n'
                arr2 = y[3:6] + '\n'
                arr3 = y[6:9] + '\n'
                finalarray = arr3+arr2+arr1
                newRow.append(finalarray)
        newBoard.append(newRow)
    tablestr = tabulate(newBoard,headers="firstrow",tablefmt="fancy_grid")
    print(tablestr)

def getPlayerTurns(board,player,n):
    # Vraca za svako polje u kome se nalazi igraceva figura to polje i listu smerova u kojima moze da ode
    turn_states = list()
    for indx,x in enumerate(board): #za svaku vrstu
          for indy,y in enumerate(x): #za svaki element u tabli
               if y != None and player in y: # ukoliko se na tom polju nalazi nesto i postoji figura trenutnog igraca na tom polju
                    moves = getMoves(board,indx,indy,n) # zovemo getMoves koji za dato polje ispituje u kojim smerovima se mozemo kretati
                    turn_states.append((indx,indy,moves))
    return turn_states # [( Index X , Index Y , [ Moves ] )] format vracanja

def getGameStates(board,n,player):
    game_states = list() #finalna lista
    currentPlayer = player
    turns = getPlayerTurns(board,currentPlayer,n)
    for turn in turns: #za svako polje
        pos_i = turn[0] 
        pos_j = turn[1]
        moves = turn[2] #sve direkcije u kojima moze da se krece
        for move in moves:
            stack_slice = 0 #ispitujemo sve mogucnosti celog stacka od 0
            lenght = len(board[pos_i][pos_j]) #duzina stacka kako bi isli od 0 do len
            for stack_slice in range(0,lenght): #za svaku figuru u stacku ispitujemo da li je moguc potez
                if board[pos_i][pos_j][stack_slice] != player: #ukoliko ta figura nije trenutni igrac
                    continue
                newMove = (pos_i,pos_j,move,stack_slice) #kreiramo novi potez 
                newBoard = list() #kreiramo novu tabelu kako ne bi promenili aktuelnu
                for x in board:
                    row = x.copy()
                    newBoard.append(row) #pokomponentno kopiranje tabele jer je ona niz nizova
                if tryMakeMove(newMove,newBoard): #ukoliko je taj potez moguc dodajemo ga u listu poteza
                    game_states.append((newBoard,newMove))
    return game_states

def getAdventage(stacks):
    if(stacks[0] > stacks[1]):
        return "W"
    elif(stacks[1] > stacks[0]):
        return "B"
    else:
        return "D"

def evaluation(board,player,oldStacks,newStacks,madePoint,n):
    points = 0 #start 

    opponent = "W" if player == "B" else "B"
    if player == madePoint:
        return 999998
    elif opponent == madePoint:
        return -999998

    for x in board:
        for y in x:
            if y != None:
                ln = len(y)
                ln3 = ln * ln * ln
                points = points + ln3 # prioritet je na stanjima koja imaju polja sa vecim stekovima
                if ln > 0:
                    if y[ln-1] == player: #ukoliko se na vrhu steka nalazi figura trenutnog igraca 
                        points = points + 10


    return points

def minMax(board,depth,maxPlayer,player,stacks,n,alpha = -999999,beta = 999999,move = None):
    localStacks = stacks.copy()
    madePoint = silent_checkBoard(board,n,localStacks)
    if depth == 0 or silent_is_game_finished(n,localStacks):
        return (evaluation(board,player,stacks,localStacks,madePoint,n),move) #minmax : (value,move)
    
    opponent = "W" if player == "B" else "B"
    
    if maxPlayer:
        maxEval = -999999
        gameStates = getGameStates(board,n,player)
        for (x,y) in gameStates:
            eval = minMax(x,depth-1,False,player,localStacks,n,alpha,beta,y)
            if eval[0] > maxEval:
                maxEval = eval[0]
                move = y
            alpha = max(alpha,eval[0])
            if beta <= alpha:
                break
        return (maxEval,move)
    else:
        minEval = 999999
        gameStates = getGameStates(board,n,opponent)
        for (x,y) in gameStates:
            eval = minMax(x,depth-1,True,player,localStacks,n,alpha,beta,y)
            if eval[0] < minEval:
                minEval = eval[0]
                move = y
            beta = min(beta,eval[0])
            if beta <= alpha:
                break
        return (minEval,move) 

start_game()
