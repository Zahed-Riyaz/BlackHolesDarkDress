import numpy as np
import os
import sys
import struct
from modules.check import *
from modules.write import write_header, write_body






class Header:
    r"""Structure of the header for initial condition file

    Parameters
    ----------

    None

    Comments
    --------

    (1) Please note that NumPart_Total_HW, nor Flag_Entropy_ICs are defined in header. Need to be implemented
    (2) Naming conventions follows users-guide.pdf of Gadget-2 for attribute names
    
    """
    
    ##A possible improvement would be to freeze the attribute structure. Maybe we can start by looking at  http://stackoverflow.com/questions/3603502/prevent-creating-new-attributes-outside-init


    ##naming use HDF5 identifier
    def __init__(self):
        self.NumPart_ThisFile    = np.zeros(6) #number of particles of each type in present file
        self.MassTable           = np.zeros(6) #mass of each particle type
        self.Time                = 0 #time of output, or expansion factor for cosmo simu
        self.Redshift            = 0 #redshift
        self.Flag_Sfr            = int(0) #flag star formation (unused in GADGET2)
        self.Flag_Feedback       = int(0) #flag feedback (unused in GADGET2)
        self.NumPart_Total       = np.zeros(6,dtype=np.int8) #total number of particles of each type in simulation
        self.Flag_Cooling        = int(0) #flag for cooling
        self.NumFilesPerSnapshot = int(1) #number of files in each snapshot
        self.BoxSize             = 0 #box size if periodic boundary condition
        self.Omega0              = 0 #matter density at z=0
        self.OmegaLambda         = 0 #vaccum energy at z=0
        self.HubbleParam         = 0 #hubble constant
        self.Flag_StellarAge     = int(0) #creation times of stars (unused)
        self.Flag_Metals         = int(0) #flag mettalicity (unused)

        ##not implemented yet
        # self.NumPart_Total_HW    = 0 #not implemented yet. assume number of particles  <2^32
        # self.Flag_Entropy_ICs    = 0




class Body:
    r"""Structure of body for initial condition file

    Parameters
    ----------
    
    npart : integer array (6)
        Number of particles for each type

    rho : boolean
        Density will be in initial condition file
        
    ne : boolean
        Electron abundance will be in initial condition file

    nh : boolean
        Hydrogen abundance will be in initial condition file

    hsml : boolean
        SPH smoothing length will be in initial condition file

    pot : boolean
        Gravitational potential enable in Makefile ?
        
    acce : boolean
        Acceleration of particles enable in Makefile ?

    endt : boolean
        Rate of change of entropic function of SPH particles enable in Makefile ?
   
    tstp : boolean
        Timestep of particles enable in Makefile ?

        
    Comments:
    --------

    (1) For the moment, all boolean optional keywords are useless.
    """

    def __init__(self, npart,
           rho=False, ne=False, nh=False, hsml=False,
           acce=False, endt=False, tstp=False):

        npart=np.array(npart) #make sure it is a numpy array
        total_number_of_particles = np.sum(npart,dtype="float64")
        gas_particles=npart[0] #number of gas particles

        if total_number_of_particles != 0. :
            self.pos = np.zeros([total_number_of_particles,3]) #Positions
            self.vel = np.zeros([total_number_of_particles,3]) #Velocities
            self.id  = np.zeros(total_number_of_particles)     #Particle ID's
            self.mass =  np.zeros(total_number_of_particles)   #Masses
        else:
            raise ValueError, "There are no particles !"

        self.u =  np.zeros(gas_particles)                  #Internal energy per unit mass





        # ##initialize only if enable in makefile to save memory. Maybe there is a smarter way to do that. But the idea is that if you need for example acce, you need all the blocks before. Need to be implemented
        # if tstp:
        #     rho = True
        #     ne = True
        #     nh = True
        #     hsml = True
        #     pot = True
        #     acce = True
        #     endt = True
        #     self.tstp =np.zeros(total_number_of_particles)

        # if endt:
        #     rho = True
        #     ne = True
        #     nh = True
        #     hsml = True
        #     pot = True
        #     acce = True
        #     self.endt =np.zeros(gas_particles)

        # if acce:
        #     rho = True
        #     ne = True
        #     nh = True
        #     hsml = True
        #     pot = True
        #     self.acce =np.zeros(total_number_of_particles)

        # if pot:
        #     rho = True
        #     ne = True
        #     nh = True
        #     hsml = True
        #     self.pot = np.zeros(total_number_of_particles)            

        # if hsml:
        #     rho = True
        #     ne = True
        #     nh = True
        #     self.hsml =np.zeros(gas_particles) #SPH Smoothing Length

        # if nh:
        #     rho = True
        #     ne = True
        #     self.nh = np.zeros(gas_particles) #Hydrogen Abundance

        # if ne:
        #     rho = True
        #     self.ne = np.zeros(gas_particles) #Electron Abundance

        # if rho:
        #     self.rho =np.zeros(gas_particles) #Density























def dump_ic(header, body, destination_file="ic.dat", format_output=1):
    r"""Generates output initial condition file for Gadget


    Parameters
    ----------
    header : object
        header for snapshot.

    body : object
        body of snapshot (POS,VEL,MASS, etc.)

    destination_file : string
        Full path of the output file name.

    format_output : integer
        Define output format as defined in Gadget-2. Only Binary 1 supported for now.

      
    """


    ##create ic_file
    if not check_if_file_exists(destination_file):
        ic_file=open(destination_file,'w')

    ##run some sanity checks.
    check_header(header)
    check_body(body)
    check_consistency(header,body)

    ##write the data
    write_header(header,ic_file,format_output)
    write_body(body,ic_file,format_output)

    ##finally close file and return
    print "=== SUMMARY ==="
    print_summary(header,body)
    ic_file.close()        
    return None









