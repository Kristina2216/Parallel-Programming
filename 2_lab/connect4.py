import random
import time
import sys
from mpi4py import MPI
import psutil

FIRST_PLAYER="C"
DEPTH=7

#psutil.Process().cpu_affinity([0]) 
#psutil.Process().cpu_affinity([0,1]) 
#psutil.Process().cpu_affinity([0,1,2]) 
#psutil.Process().cpu_affinity([0,1,2,3]) 
psutil.Process().cpu_affinity([0,1,2,3,4]) 
#psutil.Process().cpu_affinity([0,1,2,3,4,5])
#psutil.Process().cpu_affinity([0,1,2,3,4,5,6]) 
#psutil.Process().cpu_affinity([0,1,2,3,4,5,6,7]) 

class Board(object):
    def __init__(self, rows, columns, draw=False):
        self.state= 1
        self.columns= columns
        self.rows = rows
        self.lastPlayed=[]
        self.spaces=[["N" for row in range(self.rows)] for col in range(self.columns)]
        self.heights=[0 for col in range(self.columns)]
        self.lastBusyProcess=1
        if draw:
            self.drawBoard()

    def createCopy(self):
        newBoard=Board(self.rows, self.columns)
        newBoard.lastPlayed = self.lastPlayed
        newBoard.state = self.state
        newBoard.spaces = self.spaces
        newBoard.heights = self.heights
        newBoard.lastBusyProcess = self.lastBusyProcess
        return newBoard

    def drawBoard(self):
        print("Stanje na ploci: ")
        for i in range(self.rows):
            print("_"*4*self.columns)
            for j in range(self.columns+1):
                print("|", end="")
                if j!= self.columns and self.spaces[j][i]!="N":
                    print(" " + self.spaces[j][i], end=" ")
                else:
                    print("   ", end="")
            print()
        print("_"*4*self.columns)

    def checkHorizontal(self, column, player):
        height=self.heights[column]-1
        control=0
        for i in range(self.rows):
            if self.spaces[i][self.rows-height-1]==player:
                control+=1
                if control==4:
                    return True
            else:
                control=0
        return False

    def checkVertical(self, column, player):
        height=self.heights[column]-1
        control=0
        for i in range(self.rows-height-1, self.rows):
            if self.spaces[column][i]!=player:
                return False
            control+=1
            if control==4:
                return True
            
    def checkDiagonal(self, column, player):
        height=self.heights[column]-1
        col=column
        control=0

        #desno dolje
        for i in range(self.rows-height-1, self.rows):
            if self.spaces[col][i]!=player:
                break
            col=col+1
            control+=1
            if control==4:
                return True
            if col==self.columns:
                break

        if column==0:
            return
        col=column-1

        #lijevo gore
        for i in range(self.rows-height-2, -1, -1):
            if self.spaces[col][i]!=player:
                break
            col=col-1
            control+=1
            if control==4:
                return True
            if col==-1:
                break

        control=0
        col=column
   
        #lijevo dolje
        for i in range(self.rows-height-1, self.rows):
            if self.spaces[col][i]!=player:
                break
            col=col-1
            control+=1
            if control==4:
                return True
            if col==-1:
                break

        if column==self.columns-1:
            return
        col=column+1

        #desno gore
        for i in range(self.rows-height-2, -1, -1):
            if self.spaces[col][i]!=player:
                break
            col=col+1
            control+=1
            if control==4:
                return True
            if col==self.columns:
                break
            
        return False
            
    def checkEndCondition(self, column, player):
        if(self.checkHorizontal(column, player) or self.checkVertical(column, player) or self.checkDiagonal(column, player)):
            self.state = 0
            return


    def playOneTurn(self, column, player):
        height=self.heights[column]
        if self.isColumnFull(column):
            return -1
        self.spaces[column][self.rows-height-1]=player
        self.heights[column]=height+1
        self.checkEndCondition(column, player)
        self.lastPlayed.append(column)
        return 1

    def undoLastTurn(self):
        column=self.lastPlayed.pop()
        height=self.heights[column]
        self.spaces[column][self.rows-height]="N"
        self.heights[column]=height-1    

    def isColumnFull(self, column):
        if self.heights[column]==self.rows:
            return True
        return False

    def computerMove(self, depth):
        time1 = time.time()
        self.lastBusyProcess=1
        bestMove=0
        bestValue=-1
        if depth==0:
            return 0
        numJobs=0
        while depth > 0 and bestValue==-1:
            for i in range(0, self.columns):
                if(self.playOneTurn(i,"C")<0):
                    continue
                numJobs=self.splitDepthSearch(i, depth, numJobs) #racunaj vrijednost svakog podstanja u odvojenom procesu
                self.undoLastTurn()
            for i in range(numJobs):
                data= comm.recv(source=MPI.ANY_SOURCE, tag=99)
                #print(i, data)
                if(data["result"]>bestValue):
                    bestMove = data["column"]
                    bestValue = data["result"]
            depth /= 2
        self.playOneTurn(bestMove, "C")
        time2 = time.time()
        print("Potroseno vrijeme: " + str(time2 - time1))
        sys.stdout.flush()


            
    def splitDepthSearch(self, column, depth, numJobs):
        nextDestination=0
        for i in range(self.columns):
            #self.playOneTurn(i, "U") #dodano
            data = {"board": self.createCopy(), "column": column, "player": "C", "depth": depth-1} #umjesto c, u
            nextDestination=self.lastBusyProcess % self.columns
            comm.send(data, dest = nextDestination, tag=99)
            numJobs+=1
            self.lastBusyProcess+=1
            if(self.lastBusyProcess) % self.columns == 0:
                self.lastBusyProcess+=1 #preskoci 0. proces jer je u njemu glavna logika
            if(self.lastBusyProcess>=world_size):
                self.lastBusyProcess=1 
                #self.undoLastTurn()
                #self.state=1
        return numJobs

    def calculateValue(self, previousPlayer, depth):
        if self.state == 0 and previousPlayer == "C":
            self.state = 1
            return 1
        elif self.state == 0 and previousPlayer == "U":
            self.state =1
            return -1
        if previousPlayer == "U":
            previousPlayer = "C"
        else: previousPlayer = "U"
        possibleMoves=0
        totalValue=0
        tempValue=0
        allLose=True
        allWin=True
        if depth == 0:
            return 0
        for i in range(self.columns):
            if(self.playOneTurn(i, previousPlayer)<1):
                continue
            possibleMoves+=1
            tempValue = self.calculateValue(previousPlayer, depth-1)
            self.undoLastTurn()
            if(tempValue > -1):
                allLose = False
            if(tempValue != 1):
                allWin = False
            if(tempValue == 1 and previousPlayer == "C"):
                #self.state=1
                return 1;	#ako svojim potezom mogu doci do pobjede (pravilo 1)
            if(tempValue == -1 and previousPlayer == "U"):
                #self.state=1
                return -1;	#ako protivnik moze potezom doci do pobjede (pravilo 2)
            totalValue+= tempValue
            
        if allWin:
            return 1
        if allLose:
            return -1
        return totalValue/possibleMoves


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
world_size = comm.Get_size()
playingBoard = Board(6,7, True)
player=FIRST_PLAYER
if rank!=0:
    while True:
        data = comm.recv(source=0, tag=99)
        result = data["board"].calculateValue(data["player"], data["depth"])
        comm.send ({"result": result, "column": data["column"]}, dest = 0, tag = 99)

else:
    while 1:
        if player=="U":
            col=int(input("Unesite potez:"))
            playingBoard.playOneTurn(col-1,"U")
            if (playingBoard.state==0):
                playingBoard.drawBoard()
                print("Defeat")
                exit(0)
            playingBoard.drawBoard()
        playingBoard.computerMove(DEPTH)
        if(playingBoard.state==0):
            playingBoard.drawBoard()
            print("Victory")
            exit(0)
        playingBoard.drawBoard()
        player="U"
