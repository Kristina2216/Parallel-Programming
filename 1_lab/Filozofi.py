import random
import time
from mpi4py import MPI


class Fork(object):
    def __init__(self, ruka = "desnu"):
        self.clean = False
        self.hand = ruka


class Philosopher(object):
    def __init__(self, index, size, forks: []):
        self.index = index
        self.leftN = index-1 if index != 0 else size-1
        self.rightN = index+1 if index != size-1 else 0
        self.oldRequests = set()
        self.forks = forks
        self.printForks()
        self.loop()

    def loop(self):
        while(True):
            self.think()
            self.getForks()
            self.eat()

    def think(self):
        print("Filozof "+str(self.index)+" misli.", flush="True")
        for i in range(random.randint(1,5)):
            time.sleep(1)
            self.findMessages()


    def checkMessage(self, message, idx):
        #vraca vilicu
        if message == "clean":
            if world_size == 2:
                    self.forks.append(Fork("lijevu"))
                    self.forks.append(Fork())
            elif idx == self.leftN:
                self.forks.append(Fork("lijevu"))
                self.printForks()
            else:
                self.forks.append(Fork())
                self.printForks()

        #trazi vilicu
        elif world_size == 2 and len(self.forks)== 2  and not self.forks[1].clean:
            for fork in self.forks:
                self.forks=[]
            comm.send("clean", dest=self.leftN)
            print("Filozof " + str(self.index) + " salje obje vilice filozofu " + str(idx),
                  flush=True)

        elif len(self.forks) != 0:
            if idx == self.leftN:
                for fork in self.forks:
                    if not fork.clean and fork.hand == "lijevu":
                        comm.send("clean", dest = self.leftN)
                        print("Filozof "+str(self.index)+" salje "+fork.hand+" vilicu filozofu "+ str(idx), flush=True)
                        self.forks.remove(fork)
                    else:
                        self.oldRequests.add(tuple([str(message), idx]))

            elif idx == self.rightN:
                for fork in self.forks:
                    if not fork.clean and fork.hand == "desnu":
                        comm.send("clean", dest=self.rightN)
                        print("Filozof " + str(self.index) + " salje " + fork.hand + " vilicu filozofu " + str(idx), flush=True)
                        self.forks.remove(fork)
                    else:
                        self.oldRequests.add(tuple([str(message), idx]))


    def printForks(self):
        for fork in self.forks:
            print("Filozof "+ str(self.index) + " ima " + fork.hand + " vilicu.", flush=True)

    def getForks(self):
        if (world_size==2):
            comm.send("request", dest=self.rightN)
            while (len(self.forks) != 2):
                time.sleep(1)
                self.findMessages()
        else:
            while(len(self.forks) != 2):
                if(len(self.forks)==1):
                    if(self.forks[0].hand == "lijevu"):
                        comm.send("request", dest = self.rightN)
                    else:
                        comm.send("request", dest = self.leftN)
                else:
                    comm.send("request", dest=self.rightN)
                    comm.send("request", dest=self.leftN)
                for i in range(4):
                    time.sleep(1)
                    self.findMessages()
            self.findMessages()

    def eat(self):
        print("Filozof " +str(self.index) + " je isao jesti.", flush=True)
        time.sleep(2)
        for fork in self.forks:
            fork.clean = False
        print("Filozof " + str(self.index) + " je zavrsio s jelom.", flush=True)


    def findMessages(self):
        for message in self.oldRequests:
            self.checkMessage(message[0], message[1])
        if comm.iprobe(source=self.leftN):
            self.checkMessage(comm.recv(source=self.leftN), self.leftN)
        if comm.iprobe(source=self.rightN):
            self.checkMessage(comm.recv(source=self.rightN), self.rightN)


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
world_size = comm.Get_size()
forks1 = []
forks1.append(Fork())
if rank == 0:
    forks1.append(Fork("lijevu"))
    Philosopher(rank, world_size, forks1)
elif rank == world_size-1:
    Philosopher(rank, world_size, [])
else:
    Philosopher(rank, world_size, forks1)
