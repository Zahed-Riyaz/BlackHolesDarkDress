### this is an example of how to generate an initial condition file

import numpy as np
import pygadgetic



##define number of particles
npart=[1,2,0,0,0,0]
total_number_of_particles=np.sum(npart) #total number of particles


##create objects
my_header=pygadgetic.Header()
my_body=pygadgetic.Body(npart)


##fill in the header
my_header.NumPart_ThisFile = np.array(npart)
my_header.NumPart_Total = np.array(npart)


##fill the body with minimal information
#position
my_body.pos[0,:]=np.array([0,0,0]) #the first particle will be at the center
my_body.pos[1,:]=np.array([1,1,1])
my_body.pos[2,:]=np.array([-1,0,1])





#velocity
my_body.vel[:,:]=0.

#id
my_body.id[:]=np.arange(0,total_number_of_particles) #generate an array from 0 to total_number_of_particles

#mass
my_body.mass[:]=1. #all particles have the same mass =1 (gadget units)

##now writes the initial condition file
my_name="./test_ic.dat"
pygadgetic.dump_ic(my_header,my_body,my_name)
