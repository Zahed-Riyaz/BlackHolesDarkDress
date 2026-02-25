###NAME: write.py
###PURPOSE: routines to write the header and body of a snapshot


import struct
import numpy as np








def write_header(header, ic_file, format_output=1):
    """Write the header into a specified already open file

    Parameters
    ----------

    header : object
       see Class Header defined in this file

    ic_file : object
       file identifier when opening file in python

    format_output : integer
       format of desired initial condition (1:binary, 3:hdf5). Only binary 1 is implemented

    Comments
    --------

    Please note that NumPart_Total_HW, nor Flag_Entropy_ICs will be written to the header. Need to be implemented
    """

    print "Writing header (little endian)"
    #* Note that we use struct.pack to form a block, whereas we have to use tostring() on a non-block *#
    #write header into file
    ic_file.write(struct.pack('<I',256))                             #dummy
    ic_file.write(struct.pack('<6I',
                             header.NumPart_ThisFile[0],
                             header.NumPart_ThisFile[1],
                             header.NumPart_ThisFile[2],
                             header.NumPart_ThisFile[3],
                             header.NumPart_ThisFile[4],
                             header.NumPart_ThisFile[5]))
    ic_file.write(struct.pack('<6d',
                             header.MassTable[0],
                             header.MassTable[1],
                             header.MassTable[2],
                             header.MassTable[3],
                             header.MassTable[4],
                             header.MassTable[5]))
    ic_file.write(struct.pack('<d',header.Time))                            #a
    ic_file.write(struct.pack('<d',header.Redshift))                        #z
    ic_file.write(struct.pack('<i',header.Flag_Sfr))                         #sfrFlag
    ic_file.write(struct.pack('<i',header.Flag_Feedback))                          #FBFlag
    ic_file.write(struct.pack('<6I',
                             header.NumPart_Total[0],
                             header.NumPart_Total[1],
                             header.NumPart_Total[2],
                             header.NumPart_Total[3],
                             header.NumPart_Total[4],
                             header.NumPart_Total[5]))
    ic_file.write(struct.pack('<i',header.Flag_Cooling))                     #coolingFlag    
    ic_file.write(struct.pack('<i',header.NumFilesPerSnapshot))                               #numfiles
    ic_file.write(struct.pack('<d',header.BoxSize))                              #boxsize
    ic_file.write(struct.pack('<d',header.Omega0))                              #Omega_0
    ic_file.write(struct.pack('<d',header.OmegaLambda))                              #Omega_Lambda
    ic_file.write(struct.pack('<d',header.HubbleParam))                               #HubbleParam
    ic_file.write(struct.pack('<i',header.Flag_StellarAge))
    ic_file.write(struct.pack('<i',header.Flag_Metals))
    ##should add here NumPart_Total_HW. not implemented yet, nor Flag Entropy


    ##fill in empty space
    header_bytes_left = 260 - ic_file.tell()
    for j in range(header_bytes_left):
        ic_file.write(struct.pack('<x'))
    ic_file.write(struct.pack('<I',256))
    if ic_file.tell()-8 != 256:
        raise IOError, "header has wrong format"


    return None






def write_body(body, ic_file, format_output):
    """Write the body of initial condition file in a already open specified file

    Parameters
    ----------

    body : object
       see Class Body defined in this file

    ic_file : object
       file identifier when opening file in python

    format_output : integer
       format of desired initial condition (1:binary, 3:hdf5). Only binary 1 is implemented

    """

    print "Writing body (little endian)"

    def write_block(block, nbytes, ic_file):
        """Write a block from the body structure

        Parameters
        ----------
        
        block : float array
           The data block to be written.

        nbytes : float
           Size of the block

        ic_file ; Object
           File identifier to write in
            
        """

        ic_file.write(struct.pack('<I',nbytes)) #dimensions*number of particles
        ic_file.write(block.tostring())
        ic_file.write(struct.pack('<I',nbytes))

        return None

    total_number_of_particles = np.size(body.pos[:,0])
    gas_particles = np.size(body.u)

    
    #write in binary format
    write_block(body.pos.astype('f'), 3*4*total_number_of_particles, ic_file)
    write_block(body.vel.astype('f'), 3*4*total_number_of_particles, ic_file)
    write_block(body.id.astype('I'), 4*total_number_of_particles, ic_file)
    write_block(body.mass.astype('f'), 4*total_number_of_particles, ic_file)
    write_block(body.u.astype('f'), 4*gas_particles, ic_file)


    # ##need to set conditions to write these blocks. Maybe it's better to do a loop over each block, but it need some more work.
    # write_block(body.rho.astype('f'), 4*gas_particles, ic_file)
    # write_block(body.ne.astype('f'), 4*gas_particles, ic_file)
    # write_block(body.nh.astype('f'), 4*gas_particles, ic_file)
    # write_block(body.hsml.astype('f'), 4*gas_particles, ic_file)
    
    return None
