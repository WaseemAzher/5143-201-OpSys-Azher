#!/usr/bin/env python3
# === Class: Semaphore===
from sim_components import *
###################################################################################################

# === Class: SemaphorePool===

class SemaphorePool(object):
    """A class to simulate a semaphore .
    - **Methods**:
        - acquire(obj_id) -> (int,None) : Attempt to acquire semaphore, success = value that is not None.
        - release(obj_id) -> (int,None) : Attempt to release semaphore, success = value that is not None.
    - **Attributes**:
        - sem_dict  : List of fake semaphores

    """
    __shared_state = {}
    def __init__(self, num_sems=5, count=1):
        self.__dict__ = self.__shared_state
        
        if len(self.__shared_state.keys()) == 0:
            self.sem_dict = {}
            #self.sem_owner = []
            self.val=[]
            for i in range(num_sems):
                self.sem_dict[i] = Fifo()
                #self.sem_owner.append(None)
                self.val.insert(i,1)

    #def check(self, obj_id=None, i=None):

    def acquire(self, obj_id=None, i=None):
        """Acquire a semaphore from pool.
        - **Args:**
            - obj_id (int) : Id of object (or some process id) requesting the semaphore
        - **Returns:**
            - (int , None) : Int if a semaphore was acquired, or None if no semaphore was available
        """
        if not isinstance(obj_id,Process):
            raise Exception("semaphore requires items added to be of type 'Process'")
        self.sem_dict[int(i)].add(obj_id)
        self.val[i]-=1


    def release(self, ind=None):
        """Release a semaphore from pool.

        - **Args:**
            - obj_id (int) : Id of object (or some process id) requesting the semaphore
        - **Returns:**
            - (int , None) : Int if a semaphore was released, None if 'obj_id' was not in dict
        """
        #if obj_id is None:
        #    raise Exception("Need object id to acquire semaphore.")
        
        if ind is None and (ind not in self.sem_dict.keys()) :
                raise Exception("Need semaphore number to continue.")
        else:
            i=int(ind)
            if self.sem_dict[i].empty():
                self.val[i]+=1
            else:
                self.sem_dict[i].remove()                            #.pop(0)
                self.val[i]+=1

    def __str__(self):
        string = ""
        for i, sem in self.sem_dict.items():
            string += "%s: %s\n" % (i,str(sem))
        return string

class dummy:pass

def test_semaphore_class():

        # Create 5 dummy classes to acquire and release semaphores
    d1 = dummy()
    d2 = dummy()
    d3 = dummy()
    d4 = dummy()
    d5 = dummy()
    d6 = dummy()
    d7 = dummy()
    d8 = dummy()

    print("Creating a semaphore pool with 5 semaphores with a start value of 1")
    SP = SemaphorePool()
    print(SP)

    print("d2 Attempt to release ... (should work)")
    SP.release(2)
    print(SP.val[2])
    print(SP)
    
    print("d1 Attempt to acquire sem 3... (should work)")
    print(str(id(d1)))
    SP.acquire(id(d1),3)
    print(SP.val[3])
    if not SP.sem_dict[2].empty():
        print(SP.sem_dict[2].first())
    else:
        print(SP.sem_dict[3].first())

    print("d2 Attempt to acquire ... (should work)")
    print(str(id(d2)))
    SP.acquire(id(d2),4)
    print(SP.val[4])
    print(SP)

    print("d3 Attempt to acquire ... (should work)")
    print(str(id(d3)))
    SP.acquire(id(d3),6)
    #print(SP.val[6])
    print(SP)

    print("d4 Attempt to acquire ... (should work)")
    print(str(id(d4)))
    SP.acquire(id(d4),2)
    print(SP.val[2])
    print(SP)

    print("d5 Attempt to acquire ... (should work)")
    print(str(id(d5)))
    SP.acquire(id(d5),0)
    print(SP.val[0])
    print(SP)

    print("d6 Attempt to acquire ... (should fail - none left)")
    print(str(id(d6)))
    SP.acquire(id(d6),4)
    print(SP.val[4])
    print(SP)

    print("Attempt to release ...")
    SP.release(4)
    print(SP.val[4])
    print(SP)

    print("d6 Attempt to release ... (should fail - never got copy)")
    SP.release(2)
    print(SP.val[2])
    print(SP)

    print("d2 Attempt to release ... (should work)")
    SP.release(2)
    print(SP.val[2])
    print(SP)


if __name__=='__main__':
    test_semaphore_class()