# project2
scheduling project


>Group Members
>
| Name     | Email   | Github Username |
|----------|---------|-----------------|
| Name 1   | waseemazher89@gmail.com | waseemazher  |
| Name 2   | divya.h.shree12@gmail.com | divyah12  |
| Name 3   | Sowjanyanemani13@gmail.com | sowjanya137 |


![](https://github.com/WaseemAzher/5143-201-OpSys-Azher/blob/master/assignments/participation.png)



Which additional code is attributed to each team member.

>Divyashree:

semaphore.py

fifo.py

implementation of interrupt, semaphore, display status and FCFS scheduling
 
>Sowjanya and Waseem:

implementation of memory constriant

implementation of sorted display for I/O queue

final finished list and its report

Responsible for wait and turnaround time

Implementation of level 1 scheduling and testing was done in group.


>Time each team member spent working on project.
>
| Name     | Time   | 
|----------|---------|
| divyashree, H B | 56|
| Sowjanya,Nemani  | 41|
| Azher, Waseem	  |41|


Files in project

>A list showing the file structure of your code and which files are included in your project.

This simulation uses the template provided and has the implementation for schedular class.
Furthermore, additional implimentation of multilevel feedback queue is inside the schedular class

The following are added to schedular class:

     def load_level1Q(self):# load process to 
         
    def load_cpu(self):
    
    def check_cpu(self):
        #This method is responsible for Scheduling the process .i.e, Assigns the process priority 
        #Invokes the process termination method
           
    def remove_cpu_proc(self):
        #Remove process from CPU and load if New/waiting process in Level 1 else from Level 2 to CPU 
        
    def terminate_proc(self): 
     #When the remmaining burst is zero this method is called
     
   def stop_simulation(self):
        #Used for test case
        #Stop the simulation when all the Queue's are empty()
        
 In simulation class:
 
     def sys_handler(self):  
     #check cpu every clock tick and puts back the process from I/O wait queue
     #after its I/O wait complition time
     
      def display_status(self,info):
        #display simulation status
        
  The following are helper methods for display status:     
  
      def print_queue_io(self,que):
        #Prints the process waiting for I/O complition
               
    def print_queue_fin(self,que):
        #prints the Finished Process List
        
    def print_queue(self,que):
        #Common print method to display Job_scheduling, Level 1 and Level 2 Queue's

     def print_report(self):
        #Calculates Avg scheduling queue wait time and turnaround time and prints it
        
 The following files are changed for this simulation:
 
 Accounting.py
 
     Holds I/O data i.e,         
     self.io_start_time=0
     self.io_burst=0
     self.io_end_time=0
     self.pstart_time = 0  # point of time where the process is placed on cpu from ready queue
        
  Semaphore.py
  
    Has semaphorepool class only and its methods are implemented.
    
  Fifo.py
  
     def remove_p(self,proc):
     #removes the element based on the process passed
     
  Process.py
  
  Holds data information such as:
       self.semnum = None  # semaphore number
       self.io_state= True
       #io_state is a flag for storing the process start time when it gets Cpu for the first time 
       
       

