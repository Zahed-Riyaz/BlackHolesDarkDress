import os
import struct
import numpy as np
import io

# ====== SET YOUR FILE PATH HERE ======
DAT_FILE_PATH = "/Users/zahed_riyaz/Documents/prbh/BlackHolesDarkDress/Nbody/run/PBH1.dat"
# =====================================


def read_gadget_header(f):
    # read block size and then the 256-byte header
    block_bytes = f.read(4)
    if not block_bytes:
        raise EOFError("Unexpected EOF while reading header block size")
    nbytes = struct.unpack('<I', block_bytes)[0]
    hdr = f.read(nbytes)
    f.read(4)            # closing block size

    buf = io.BytesIO(hdr)
    hdr_struct = {}

    hdr_struct['NumPart_ThisFile'] = np.frombuffer(buf.read(24), '<u4')
    hdr_struct['MassTable'] = np.frombuffer(buf.read(48), '<f8')
    hdr_struct['Time'], hdr_struct['Redshift'] = struct.unpack('<dd', buf.read(16))
    hdr_struct['Flag_Sfr'], hdr_struct['Flag_Feedback'] = struct.unpack('<ii', buf.read(8))
    hdr_struct['NumPart_Total'] = np.frombuffer(buf.read(24), '<u4')
    hdr_struct['Flag_Cooling'], hdr_struct['NumFilesPerSnapshot'] = struct.unpack('<ii', buf.read(8))
    hdr_struct['BoxSize'], hdr_struct['Omega0'], hdr_struct['OmegaLambda'], hdr_struct['HubbleParam'] = struct.unpack('<dddd', buf.read(32))
    hdr_struct['Flag_StellarAge'], hdr_struct['Flag_Metals'] = struct.unpack('<ii', buf.read(8))
    # remaining bytes are padding

    return hdr_struct


def read_block(f, count, dtype):
    nbytes = struct.unpack('<I', f.read(4))[0]
    data = np.fromfile(f, dtype=dtype, count=count)
    f.read(4)
    return data


def read_gadget_body(f, header):
    nptot = int(np.sum(header['NumPart_ThisFile']))
    pos = read_block(f, 3*nptot, '<f4').reshape((nptot,3))
    vel = read_block(f, 3*nptot, '<f4').reshape((nptot,3))
    ids = read_block(f, nptot, '<u4')
    mass = read_block(f, nptot, '<f4')
    ngas = int(header['NumPart_ThisFile'][0])
    u = read_block(f, ngas, '<f4')
    return pos, vel, ids, mass, u


def read_dat_file(file_path):
    if not os.path.exists(file_path):
        print("File does not exist.")
        return

    with open(file_path, "rb") as f:
        hdr = read_gadget_header(f)
        print("Header contents:")
        for k,v in hdr.items():
            print("  %-20s %s"%(k,str(v)))
        print()

        pos, vel, ids, mass, u = read_gadget_body(f, hdr)
        print("read %d particles"%pos.shape[0])
        print("first 5 positions:", pos[:5])
        print("first 5 velocities:", vel[:5])
        print("first 5 ids:", ids[:5])
        print("first 5 masses:", mass[:5])
        print("u array length:", u.shape)

        return hdr, pos, vel, ids, mass, u

if __name__ == "__main__":
    read_dat_file(DAT_FILE_PATH)
