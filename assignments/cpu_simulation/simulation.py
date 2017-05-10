#!/usr/bin/python3
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/components')
import random
import time
from decimal import Decimal, ROUND_HALF_UP
from sim_components import *

"""
This is a starter pack for a cpu scheduling project. The code / classes provided are to give you a
head start in creating the scheduling simulation. Obviously this is a simulation, so the majority
of the concepts are "simulated". For example, process "burst times" and "IO times" are known
a-priori (not so in real world). Things like memory are abstracted from addressable locations and
page tables to total "blocks" needed.
"""

# === Class: Scheduler===

class Scheduler(object):
    """
    New:        In this status, the Process is just made or created.
    Running:    In the Running status, the Process is being executed.
    Waiting:    The process waits for an event to happen for example an input from the keyboard.
    Ready:      In this status the Process is waiting for execution in the CPU.
    Terminated: In this status the Process has finished its job and is ended.
    """
    def __init__(self, *args, **kwargs):
        self.clock = Clock()
        self.memory = Memory()
        self.cpu = Cpu()
        self.sem = SemaphorePool()
        self.job_scheduling_queue = Fifo()        #Purgatory Queue 
        self.level1_queue = Fifo()                #Level 1 ready Queue
        self.level2_queue = Fifo()                #Level 2 ready Queue    
        self.finished_list = Fifo()               #Queue to hold the process which have finished their job   
        self.io_wait_queue = Fifo()               #Interrupt wait Queue
        self.l1_time=100                          # Level 1 Time Quantum
        self.l2_time=300                          # Level 2 Time Quantum
       

    def new_process(self,job_info):
        """New process entering system gets placed on the 'job_scheduling_queue'.
        - **Args**:
            - job_info (dict): Contains new job information.
        - **Returns**:
            - None
        """
        #remove the process which requires memory more than system memory(512)
        if int(job_info['mem_required']) > 512:
            f.write("Event: A   Time: "+str(self.clock.current_time())+"\n")
            f.write("This job exceeds the system's main memory capacity.\n")
		#Add process to purgatory queue called job_scheduling_queue
        else:
            self.job_scheduling_queue.add(Process(**job_info))
            f.write("Event: A   Time: "+str(self.clock.current_time())+"\n")

    def perform_io(self,info):
        """Current process on cpu performs io
        """
        f.write("Event: I   Time: "+str(self.clock.current_time())+"\n")
        #current process in cpu is intserted to io wait queue
        proc=self.cpu.running_process
        #update I/O information for report 
        proc.acct['io_start_time']=info['time']
        proc.acct['io_burst']=info['ioBurstTime']
        proc.acct['io_end_time']=int(info['ioBurstTime'])+int(info['time'])
        #After compliting the wait time, process is inserted back to Level 1 Ready Queue
        proc['priority']='1'
        self.io_wait_queue.add(proc)
        self.cpu.remove_process()
        

    def sem_acquire(self,info):
        """Acquire one of the semaphores
        """
        f.write("Event: W   Time: "+str(self.clock.current_time())+"\n")
        # Check for Cpu Idle state before assigning Semaphores
        if self.cpu.busy():
            sem_proc=self.cpu.running_process           
            sem_proc['semnum']=int(info['semaphore'])
            #Owner process no preemption
            if self.sem.val[int(info['semaphore'])]>0:
                self.sem.val[int(info['semaphore'])]-=1
            else:
                #If owner exists push the process to its respective semaphore wait Queue  
                self.sem.acquire(sem_proc,int(info['semaphore']))
                #Preempt the process in CPU
                self.cpu.remove_process()

    def sem_release(self,info):
        """Release one of the semaphores
        """
        sem_num=int(info['semaphore'])
        f.write("Event: S   Time: "+str(self.clock.current_time())+"\n")
        #The next process in semaphore wait Queue is released to Level 1 ready queue
        if not self.sem.sem_dict[int(sem_num)].empty() :
                semr_proc = self.sem.sem_dict[sem_num].first()
                if semr_proc['priority']=='1':
                    self.level1_queue.add(semr_proc)
                if semr_proc['priority']=='2':
                     self.level2_queue.add(semr_proc)
        #release semaphore
        self.sem.release(sem_num)

    def terminate_proc(self):
    #When the remmaining burst is zero this method is called
      proc=self.cpu.running_process
      f.write("Event: T   Time: "+str(self.clock.current_time())+"\n")
      self.finished_list.add(proc)
      proc.acct['end_time']= self.clock.current_time()
      proc.acct['turnaround_time']= int(proc.acct['end_time'])-int(proc['arrival_time'])  
      self.memory.deallocate(self.cpu.running_process['process_id'])
	
	
    def check_cpu(self):
        #This method is responsible for Scheduling the process .i.e, Assigns the process priority 
        #Invokes the process termination method
        if self.cpu.busy():
            proc=self.cpu.running_process
            proc.acct['num_bursts']=str((int(proc.acct['num_bursts'])-1))
            temptime= self.clock.current_time()-self.cpu.process_start_time
            #Case 1: Level 1 ready queue is empty
            if not self.level1_queue.empty() and proc['priority']=='2':
                if int(proc.acct['num_bursts'])==0:
		    self.terminate_proc()
                self.level2_queue.add(proc)                        
                self.load_level1Q()        # empty system - presentt time a proc can enter is updated
                return True
            #Case 2: Process in CPU based on which Level it is from
            # For Time Quantum
            if proc['priority']=='1':                
                    if int(proc.acct['num_bursts'])==0 or temptime==self.l1_time:
                        if int(proc.acct['num_bursts'])==0:
			    self.terminate_proc()							
                        else:
                            self.level2_queue.add(proc)
                            f.write("Event: E   Time: "+str(self.clock.current_time())+"\n")
                            proc['priority']='2'
                            self.load_level1Q()        # empty system - presentt time a proc can enter is updated
                        return True
                    else:
                        return False
            elif proc['priority']=='2':
                    temptime= self.clock.current_time()-self.cpu.process_start_time
                    if int(proc.acct['num_bursts'])==0 or temptime==self.l2_time:
                        if int(proc.acct['num_bursts'])==0:
							                   self.terminate_proc()							
                        else:
                            f.write("Event: E   Time: "+str(self.clock.current_time())+"\n")
                            self.level2_queue.add(proc)                        
                            self.load_level1Q()        # empty system - current time a proc can enter is updated
                        return True
                    else:
                        return False                        
    
    def remove_cpu_proc(self):
        #Remove process from CPU and load if New/waiting process in Level 1 else from Level 2 to CPU 
        proc=self.cpu.running_process        
        proc.acct['wait_time']=int(self.clock.current_time())-int(proc['arrival_time'])-int(proc.acct['total_burst_time'])
        self.cpu.remove_process()
        self.load_level1Q() 
        self.load_cpu()
        
    def load_cpu(self):
        if not self.cpu.busy():
            #Load Level 1 process to CPU
            if not self.level1_queue.empty():
                self.cpu.run_process(self.level1_queue.first())
                cprocess=self.cpu.running_process
                cprocess['state']='running'
                if cprocess['io_state']:
                    cprocess.acct['pstart_time']=self.clock.current_time()
                    cprocess['io_state']=False
                self.level1_queue.remove()
            else:		#process from level 2 is added only when level1 is empty
                 if not self.level2_queue.empty():
                    self.cpu.run_process(self.level2_queue.first())
                    cprocess=self.cpu.running_process
                    cprocess['state']='running'
                    self.level2_queue.remove()                 
        #else:
         #   print("\tcpu busy, cannot run process")
    
    def load_level1Q(self):
        while not self.job_scheduling_queue.empty() :
             Rprocess=self.job_scheduling_queue.first() 
             if self.memory.available() < int(Rprocess['mem_required']):
                 #fill ready queue only if mem is available
                 break
             self.level1_queue.add(self.job_scheduling_queue.first())
             self.memory.allocate(Rprocess)
             Rprocess['state']='Waiting'
             Rprocess['priority']='1'
             Rprocess.acct['start_time']=self.clock.current_time()
             Rprocess.acct['num_bursts']=str(int(Rprocess['burst_time']))
             self.job_scheduling_queue.remove()
        self.load_cpu()

    def stop_simulation(self):
        #Used for test case
        #Stop the simulation when all the Queue's are empty()
        if self.job_scheduling_queue.empty():
            if self.level1_queue.empty():
                if not self.cpu.busy():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    
###################################################################################################

# === Class: Simulator===

class Simulator(object):
    """
    Not quite sure yet
    """
    def __init__(self, **kwargs):

        # Must have input file to continue
        if 'input_file' in kwargs:
            self.input_file = kwargs['input_file']
        else:
            raise Exception("Input file needed for simulator")

        # Can pass a start time in to init the system clock.
		#did not understand the significance of it
        if 'start_clock' in kwargs:
            self.start_clock = kwargs['start_clock']
        else:
            self.start_clock = 0

        # Read jobs in apriori from input file.
        self.jobs_dict = load_process_file(self.input_file,return_type="Dict")
       # create system clock and do a hard reset it to make sure
        # its a fresh instance.
        self.system_clock = Clock()
        self.system_clock.hard_reset(self.start_clock)
        # Initialize all the components of the system.
        self.scheduler = Scheduler()
        self.memory = Memory()
        self.cpu = Cpu()
        
        # A = new process enters system             -> calls scheduler.new_process
        # D = Display status of simulator           -> calls display_status
        # I = Process currently on cpu performs I/O -> calls scheduler.perform_io
        # S = Semaphore signal (release)            -> calls scheduler.sem_acquire
        # W = Semaphore wait (acquire)              -> calls scheduler.sem_release
        self.event_dispatcher = {
            'A': self.scheduler.new_process,
            'D': self.display_status,
            'I': self.scheduler.perform_io,
            'W': self.scheduler.sem_acquire,
            'S': self.scheduler.sem_release
        }

        self.system_clock+=100
        # Start processing jobs:
        first=True
        # While there are still jobs to be processed
        while len(self.jobs_dict) > 0:
            # Events are stored in dictionary with time as the key
            key = str(self.system_clock.current_time())
			# If current time is a key in dictionary, run that event.
            if key in self.jobs_dict.keys():
                event_data = self.jobs_dict[key]
                event_type = event_data['event']
               # Call appropriate function based on event type
                self.event_dispatcher[event_type](event_data)
                # Remove job from dictionary
                del self.jobs_dict[key]
        
            #inserting process to ready queue from job scheduling queue based on memory availability
            self.scheduler.load_level1Q()
            self.system_clock += 1
            self.sys_handler()
    
        run_simulation=True
        while run_simulation:
            #increment clock till every queue becomes empty
            if self.scheduler.stop_simulation():
                run_simulation=False
                break
            self.system_clock += 1
            self.sys_handler()
         #Final report
        f.write("\nThe contents of the FINAL FINISHED LIST\n")
        f.write("---------------------------------------\n")
        self.print_queue_fin(self.scheduler.finished_list)
        self.print_report()

    def sys_handler(self):  
        
        #io waiting process are placed back to ready queue after complition of wait time
        for ioproc in iter(self.scheduler.io_wait_queue):
                temp_iot=int(ioproc.acct['io_end_time'])
                if temp_iot == int(str(self.system_clock.current_time())):
                    f.write("Event: C   Time: "+str(self.system_clock.current_time())+"\n")
                    self.scheduler.level1_queue.add(ioproc)
                    self.scheduler.io_wait_queue.remove_p(ioproc)

        #check is it time to remove process from cpu for every clock cycle
        if self.scheduler.check_cpu():
                self.scheduler.remove_cpu_proc()
               
    def display_status(self,info):
        #display simulation status
        f.write("Event: D   Time: "+str(self.system_clock.current_time())+"\n")
        f.write("\n************************************************************\n")
        f.write("\nThe status of the simulator at time "+str(self.system_clock.current_time())+".\n")
        f.write("\nThe contents of the JOB SCHEDULING QUEUE\n")
        f.write("----------------------------------------\n")
        if not self.scheduler.job_scheduling_queue.empty():             
             self.print_queue(self.scheduler.job_scheduling_queue)
             f.write("\n")
        else:
            f.write("\nThe Job Scheduling Queue is empty.\n\n")
        f.write("\nThe contents of the FIRST LEVEL READY QUEUE\n")
        f.write("-------------------------------------------\n")
        if not self.scheduler.level1_queue.empty():
             self.print_queue(self.scheduler.level1_queue)
             f.write("\n")
        else:
            f.write("\nThe First Level Ready Queue is empty.\n\n")
            
        f.write("\nThe contents of the SECOND LEVEL READY QUEUE\n")
        f.write("--------------------------------------------\n")
        if not self.scheduler.level2_queue.empty():             
             self.print_queue(self.scheduler.level2_queue)
             f.write("\n")
        else:
            f.write("\nThe Second Level Ready Queue is empty.\n\n")
        f.write("\nThe contents of the I/O WAIT QUEUE\n")
        f.write("----------------------------------\n")
        if not self.scheduler.io_wait_queue.empty():             
            self.print_queue_io(self.scheduler.io_wait_queue)
            f.write("\n")
        else:
            f.write("\nThe I/O Wait Queue is empty.\n\n")
        f.write("\nThe contents of SEMAPHORE ZERO\n")
        f.write("------------------------------\n")   
        f.write("\nThe value of semaphore 0 is "+ str(self.scheduler.sem.val[0])+".\n")
        if not self.scheduler.sem.sem_dict[0].empty():
             f.write("\n")
             for p in iter(self.scheduler.sem.sem_dict[0]):
                f.write(p['process_id']+"\n")
             #f.write("\n")
        else:
            f.write("\nThe wait queue for semaphore 0 is empty.\n")
        f.write("\n\nThe contents of SEMAPHORE ONE\n")
        f.write("-----------------------------\n")

        f.write("\nThe value of semaphore 1 is "+  str(self.scheduler.sem.val[1])+".\n")
        if not self.scheduler.sem.sem_dict[1].empty():
            f.write("\n")
            for p in iter(self.scheduler.sem.sem_dict[1]):
                f.write(p['process_id']+"\n")
            f.write("\n")
        else:
            f.write("\nThe wait queue for semaphore 1 is empty.\n\n")
        
        f.write("\nThe contents of SEMAPHORE TWO\n")
        f.write("-----------------------------\n")

        f.write("\nThe value of semaphore 2 is "+  str(self.scheduler.sem.val[2])+".\n")
        if not self.scheduler.sem.sem_dict[2].empty():
            f.write("\n")
            for p in iter(self.scheduler.sem.sem_dict[2]):
                f.write(p['process_id']+"\n")
            f.write("\n")
        else:
            f.write("\nThe wait queue for semaphore 2 is empty.\n\n")
        
        f.write("\nThe contents of SEMAPHORE THREE\n")
        f.write("-------------------------------\n")

        f.write("\nThe value of semaphore 3 is "+  str(self.scheduler.sem.val[3])+".\n")
        if not self.scheduler.sem.sem_dict[3].empty():
            f.write("\n")
            for p in iter(self.scheduler.sem.sem_dict[3]):
                f.write(p['process_id']+"\n")
            f.write("\n")
        else:
            f.write("\nThe wait queue for semaphore 3 is empty.\n\n")
        
        f.write("\nThe contents of SEMAPHORE FOUR\n")
        f.write("------------------------------\n")

        f.write("\nThe value of semaphore 4 is "+  str(self.scheduler.sem.val[4])+".\n")
        if not self.scheduler.sem.sem_dict[4].empty():
            f.write("\n")
            for p in iter(self.scheduler.sem.sem_dict[4]):
                f.write(p['process_id']+"\n")
            f.write("\n")
        else:
            f.write("\nThe wait queue for semaphore 4 is empty.\n\n")
        
       
        f.write("\nThe CPU  Start Time  CPU burst time left\n")
        f.write("-------  ----------  -------------------\n\n")
        if self.scheduler.cpu.busy():             
             cproc=self.scheduler.cpu.running_process
             f.write(str(cproc['process_id']).rjust(7)+"   "+str(cproc.acct['pstart_time']).rjust(9)+"  "+str(cproc.acct['num_bursts']).rjust(19)+"\n")
        else:
            f.write("The CPU is idle.\n")        
        f.write("\n\nThe contents of the FINISHED LIST\n")
        f.write("---------------------------------\n") 
        if not self.scheduler.finished_list.empty():             
             self.print_queue_fin(self.scheduler.finished_list)
        else:
            f.write("\nThe FINISHED LIST is empty.\n\n")      
        f.write("\n\nThere are "+str(self.scheduler.memory.available())+" blocks of main memory available in the system.\n\n")   
        #print("hello")

    def print_queue_fin(self,que):
        #prints the Finished Process List
        f.write("\nJob #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time\n")
        f.write("-----  ---------  ---------  --------  ----------  ---------\n\n")
        for proc in iter(que):
           f.write(str(proc['process_id']).rjust(5)+"  "+str(proc['arrival_time']).rjust(9)+"  "+str(proc['mem_required']).rjust(9)+"  "+str(proc['burst_time']).rjust(8)+"  "+str(proc.acct['pstart_time']).rjust(10)+"  "+str(proc.acct['end_time']).rjust(9)+"\n")

    def print_queue_io(self,que):
        #Prints the process waiting for I/O complition
        newlist=[]
        f.write("\nJob #  Arr. Time  Mem. Req.  Run Time  IO Start Time  IO Burst  Comp. Time\n")
        f.write("-----  ---------  ---------  --------  -------------  --------  ----------\n\n")
        #Sort I/O wait queue based on Complition Time
        for proc in iter(que):
            newlist.append(proc['acct']['io_end_time'])
        newlist.sort();
        for proc1 in newlist:
          for proc in iter(que):
            if proc1==proc.acct['io_end_time']:
             f.write(str(proc['process_id']).rjust(5)+"  "+str(proc['arrival_time']).rjust(9)+"  "+str(proc['mem_required']).rjust(9)+"  "+str(proc['burst_time']).rjust(8)+"  "+str(proc.acct['io_start_time']).rjust(13)+"  "+str(proc.acct['io_burst']).rjust(8)+"  "+str(proc.acct['io_end_time']).rjust(10)+"\n")

    def print_queue(self,que):
        #Common print method to display Job_scheduling, Level 1 and Level 2 Queue's
        f.write("\nJob #  Arr. Time  Mem. Req.  Run Time\n")
        f.write("-----  ---------  ---------  --------\n\n")
        for proc in iter(que):
           f.write(str(proc['process_id']).rjust(5)+"  "+str(proc['arrival_time']).rjust(9)+"  "+str(proc['mem_required']).rjust(9)+"  "+str(proc['burst_time']).rjust(8)+"\n")

    def print_report(self):
        #Calculates Avg. wait and turnaround time and prints it
        avg_tat=0.0
        avg_wt=0.0
        count=0 
        jsq_waittime=0.0
        for proc in self.scheduler.finished_list:             
            avg_tat=avg_tat+float(proc.acct['turnaround_time'])
            count=count+1       
        f.write("\n")
        avg_tat=avg_tat/count        
        f.write("\nThe Average Turnaround Time for the simulation was "+(('%%.%df' % 3)%avg_tat)+" units.\n")        
        for proc in self.scheduler.finished_list:          
          jsq_waittime=jsq_waittime+(int(proc.acct['start_time']))-(int(proc['arrival_time']))          
        avg_wt=jsq_waittime/count       
        f.write("\nThe Average Job Scheduling Wait Time for the simulation was "+(('%%.%df' % 3) %avg_wt)+" units.\n")
        f.write("\nThere are "+str(self.scheduler.memory.available())+" blocks of main memory available in the system.\n\n")    
    
if __name__ == '__main__':

    file_name1 = os.path.dirname(os.path.realpath(__file__))+'/input_data/jobs_myout_c.txt'
    file_name2 = os.path.dirname(os.path.realpath(__file__))+'/input_data/jobs_in_c.txt'
    f = open(file_name1, 'w')  #jobs_in_a
    S = Simulator(input_file=file_name2)
    f.close()
