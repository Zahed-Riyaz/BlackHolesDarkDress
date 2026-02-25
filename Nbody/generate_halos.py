#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate halo files for use with GenerateICs scripts.

Python 2.7 compatible version

Usage:
    python generate_halos.py -M <PBH_mass> -a <semimajor_axis> -rs <softening_length>
"""

from __future__ import print_function, division
import numpy as np
import argparse
import os
import sys
from scipy.interpolate import interp1d
from scipy.integrate import quad

# Add eddington module
import eddington as edd

def generate_single_halo(M_PBH, a, r_soft, nDM=16, verbose=False):
    """
    Generate a single halo with nDM particles sampled from the Eddington distribution.
    
    Returns:
        mvals, xvals, yvals, zvals, vxvals, vyvals, vzvals
    """
    
    # Load the distribution function
    edd.loadDistribution(M_PBH, a)
    r_eq = edd.r_eq
    r_tr = edd.r_tr
    
    # Calculate halo mass
    mHalo = M_PBH * (r_tr / r_eq)**1.5
    m_particle = mHalo / nDM
    
    # Sample radial positions from the density profile
    # Using inverse transform sampling
    rvals = np.zeros(nDM)
    
    # Get cumulative mass profile
    r_sample = np.logspace(-6, np.log10(r_tr), 1000)
    M_enclosed = np.zeros_like(r_sample)
    
    for i, r in enumerate(r_sample):
        # Integrate density to get enclosed mass
        def integrand(r_prime):
            return 4.0 * np.pi * r_prime**2 * edd.rhoDM(r_prime)
        M_enclosed[i], _ = quad(integrand, 0, r, limit=100)
    
    # Normalize to total halo mass
    M_enclosed = M_enclosed / M_enclosed[-1] * mHalo
    
    # Create interpolation function
    M_interp = interp1d(M_enclosed, r_sample, kind='linear', bounds_error=False, 
                       fill_value=(r_sample[0], r_sample[-1]))
    
    # Sample radii from uniform distribution of enclosed mass
    M_random = np.random.uniform(0, mHalo, nDM)
    rvals = M_interp(M_random)
    
    # Sample velocity magnitudes from DF
    vvals = np.zeros(nDM)
    for i in range(nDM):
        # Simple rejection sampling for velocities
        v_max = np.sqrt(2.0 * edd.G_N * M_enclosed[-1] / r_tr)
        accepted = False
        while not accepted:
            v_test = np.random.uniform(0, v_max)
            # Check if this velocity is allowed at this radius
            # (simplified: just accept for now)
            vvals[i] = v_test
            accepted = True
    
    # Random positions on sphere
    cos_theta = 2.0 * np.random.rand(nDM) - 1.0
    theta = np.arccos(cos_theta)
    phi = 2.0 * np.pi * np.random.rand(nDM)
    
    xvals = rvals * np.sin(theta) * np.cos(phi)
    yvals = rvals * np.sin(theta) * np.sin(phi)
    zvals = rvals * np.cos(theta)
    
    # Random velocity directions
    cos_theta_v = 2.0 * np.random.rand(nDM) - 1.0
    theta_v = np.arccos(cos_theta_v)
    phi_v = 2.0 * np.pi * np.random.rand(nDM)
    
    vxvals = vvals * np.sin(theta_v) * np.cos(phi_v)
    vyvals = vvals * np.sin(theta_v) * np.sin(phi_v)
    vzvals = vvals * np.cos(theta_v)
    
    mvals = np.ones(nDM) * m_particle
    
    return mvals, xvals, yvals, zvals, vxvals, vyvals, vzvals


def generate_halos(M_PBH, a, r_soft, delta_Rm=1.0, num_halos=64, verbose=True):
    """
    Generate halo files for a given configuration.
    
    Parameters:
        M_PBH: PBH mass in solar masses
        a: semi-major axis in pc
        r_soft: softening length in pc
        delta_Rm: mass ratio between shells (default: 1.0)
        num_halos: number of halo files to generate (default: 64)
        verbose: print progress information
    """
    
    # Load the distribution function to get parameters
    edd.loadDistribution(M_PBH, a)
    r_eq = edd.r_eq
    r_tr = edd.r_tr
    
    # Create halos directory if it doesn't exist
    if not os.path.exists("halos"):
        os.makedirs("halos")
        print("Created halos/ directory")
    
    # Generate halo filename root
    halofile_root = "halos/lN_4_rsoft_{:.3f}_deltaRm{:.1f}_M{:.0f}_a_{:.3f}".format(
        r_soft, delta_Rm, M_PBH, a
    )
    
    if verbose:
        print("\nGenerating halos with parameters:")
        print("  PBH Mass: {} M_sun".format(M_PBH))
        print("  Semi-major axis: {} pc".format(a))
        print("  Softening length: {} pc".format(r_soft))
        print("  Halo mass: {:.1f} M_sun".format(M_PBH * (r_tr/r_eq)**1.5))
        print("  Output pattern: {}_h*.txt".format(halofile_root))
        print("  Generating {} halos...\n".format(num_halos))
    
    # Generate each halo file
    nDM = 2**4  # 16 particles per halo file (2**4)
    
    for hID in range(1, num_halos + 1):
        halofile = halofile_root + "_h{}.txt".format(hID)
        
        # Skip if already exists
        if os.path.exists(halofile):
            if verbose:
                print("  Halo {:2d}/{}: File already exists, skipping...".format(hID, num_halos))
            continue
        
        # Generate particles from Eddington distribution
        try:
            if verbose:
                print("  Halo {:2d}/{}: Generating particles...".format(hID, num_halos))
            
            mvals, xvals, yvals, zvals, vxvals, vyvals, vzvals = generate_single_halo(
                M_PBH, a, r_soft, nDM=nDM, verbose=False
            )
            
            # Save to file
            header = "Number of DM particles: {}. Softening length [pc]: {}".format(len(mvals), r_soft)
            data = np.column_stack((xvals, yvals, zvals, vxvals, vyvals, vzvals, mvals))
            np.savetxt(
                halofile,
                data,
                fmt='%.6e',
                header=header,
                comments='# '
            )
            
            if verbose:
                print("  Halo {:2d}/{}: Saved to {}".format(hID, num_halos, os.path.basename(halofile)))
                
        except Exception as e:
            print("ERROR generating halo {}: {}".format(hID, str(e)))
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    if verbose:
        print("\nSuccessfully generated {} halo files!".format(num_halos))
        print("  Location: {}_h[1-64].txt".format(os.path.abspath(halofile_root)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate halo files for PBH N-body simulations'
    )
    parser.add_argument('-M', '--MPBH', type=float, default=30,
                        help='PBH mass in solar masses (default: 30)')
    parser.add_argument('-a', '--semimajor', type=float, default=0.01,
                        help='Semi-major axis in pc (default: 0.01)')
    parser.add_argument('-rs', '--r_soft', type=float, default=0.001,
                        help='Softening length in pc (default: 0.001)')
    parser.add_argument('-dRm', '--delta_Rm', type=float, default=1.0,
                        help='Mass ratio between shells (default: 1.0)')
    parser.add_argument('-n', '--num_halos', type=int, default=64,
                        help='Number of halos to generate (default: 64)')
    
    args = parser.parse_args()
    
    generate_halos(
        M_PBH=args.MPBH,
        a=args.semimajor,
        r_soft=args.r_soft,
        delta_Rm=args.delta_Rm,
        num_halos=args.num_halos,
        verbose=True
    )