from __future__ import print_function

from pysyncobj import SyncObj, replicated, replicated_sync

class ATM(SyncObj):


    def __init__(self, selfNode, otherNode):
        super(ATM, self).__init__(selfNode, otherNode)
        self.__accounts = dict()

    
    @replicated_sync 
    def deposit(self, id, amount:int):
        if id in self.__accounts:
            self.__accounts[id] += amount
            return 1
        else:
            return -1
            
        
    @replicated_sync
    def withdraw(self, id, amount:int):
        if id in self.__accounts:
            if self.__accounts[id] >= amount:
                self.__accounts[id] -= amount
                return 1
            else:
                return -2
        else:
            return -1

    
    def balance(self, id):
        if id in self.__accounts:
            return self.__accounts[id]
        else:
            return -1

    @replicated_sync
    def add(self, id):
        if id in self.__accounts:
            return -1
        else:
            self.__accounts[id] = 0
            return 1
    
    @replicated_sync
    def transfer(self, id1, id2, amount:int):
        if id1 in self.__accounts and id2 in self.__accounts:
            if self.withdraw(id1, amount) == 1:
                self.deposit(id2, amount)
                return 1
            else:
                return -2
        else:   
            return -1
    

    