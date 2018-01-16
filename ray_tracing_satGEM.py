"""
Author: Manish Devana
Date: December 31, 2017

Ray Tracing functions for internal waves

The goal is to use an object oriented approach to a ray tracing model.
CURRENT STATUS:
load in satGEM data and rewrite functions to remove all assumptions and run in a 4d field. 

- Figure out how to make k and l and m vary in all 4 dimensions (x,y,z, and t)
- need a solid conversion method for x and y distances to lat and long (long is the tricker one)




"""


import numpy as np
import scipy
import pandas as pd
import gsw
import oceans as oc
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.colors as colors
import cmocean
import h5py


def instructions():
    """
    Print instructions
    """
    text = '''
Ray Tracing Instructions:
------------------------
1. Generate a "wave" object : rt.wave(inputs)
    - enter wave frequency, horizontal and vertical wavenumber components, and initial depth
    - view properties to check if things were entered correctly

satGEM Details
--------------
\t This ray tracing model utilizes the 4D velocity and density field constructed by Dr. Andrew Meijers. Full details are available in Meijers 2013. 
    '''

    print(text)

# Wave ray tracing equations
def N2(x, y, z, t):
    """
    N2 as a function (x, y, z, t ) taken from the satGEM field
    """
    

    return N2

def wkb_disp(f, N, k, l, m, U, V):
    """
    WKB Disperision Relation as a function of N, U, V, and K(k, l, m)
    """

    W = 0


    return W


def absoluteF(x, y, z, t):
    """
    Omega as a function of (x, y ,z ,t) from the satGEM field
    """

    return omegaF


def CGz(w0, f, kh, m):
    """
    Vertical Group Speed
    """
    return np.squeeze((((w0**2 - f**2))/(w0*(kh**2 + m**2)))*m)


def CGx(N2, w0, k, kh, m, U):
    """
    Horizontal group speed in x-direction in a flow
    """
    return np.squeeze(((N2 - w0**2)/(w0*(kh**2 + m**2)))*k)


def CGy(N2, w0, l, kh, m, V):
    """
    Horizontal group speed in y-direction in a flow
    """
    return np.squeeze(((N2 - w0**2)/(w0*(kh**2 + m**2)))*l)


def EoZ(N2, w0, f, ):
    """
    Wave ray energy when variations can only occur in the vertical (i.e. N2 and
    flow only vary with depth not horizontally) - Olbers 1981
    """
    Ez = np.squeeze((w0**2 * (N2 - f**2))
                    / ((w0**2 - f**2)**(3 / 2) * (N2 - w0**2)**(1 / 2)))
    return Ez



def xy2ll(x, y, lat0, lon0):
    """
    Conversion for x and y points to lat and long starting with an intitial lat and lon point. 
    """
    

def make_segments(x, y):
    """
    Create list of line segments from x and y coordinates, in the correct format
    for LineCollection: an array of the form numlines x (points per line) x 2 (x
    and y) array
    """

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments

def inverse_hav(x, y, lon1, lat1):
    """
    Uses the inverse haversine function to convert x and y distance to a new lat and long coordinate. (see ray tracing docs for full formula)

    Parameters
    ----------
    x: x distance traveled (east-west)
    y: y distance traveled (north-south)
    lon1: starting longitude (Degrees)
    lat1: starting latitude (Degrees)

    Returns
    -------
    lon2: final longitude (Degrees)
    lat2: final latitude (Degrees)

    
    """

    r = 6371e3 # radius of the earth
    d = np.sqrt(x**2 + y**2) # total distance traveled
    lat2 =  lat1 + (y/111.11e3) # convert y distance to a new latitude point

    # Convert to radians for use in trig functions
    latrev1 = np.deg2rad(lat1)
    latrev2 = np.deg2rad(lat2)

    # inverse haversine formula
    lon2 = lon1 + 0.5 * np.rad2deg(np.arccos(1 - 2 * ((np.sin(d / (2 * r))**2 
                - np.sin((latrev2 - latrev1)/2)**2) /
                (np.cos(latrev1) * np.cos(latrev2)))))


    return lon2, lat2 # in degrees




class wave(object):
    """
    Creates a wave which has varying functionality including:
    - time forward modelling
    - time reverse modelling
    - variable velocity and density field inputs
    - plotting and saving rays
    - HOPEFULLY: built in gui
    """

    # Add functionality for a default Buoyancy Frequncy and Velocity Profile

    def __init__(self, k=10*1000, l=10*1000, m=500, w0=8e-4, z0=500):

        # Convert wavelengths into wavenumbers
        # Save initial values becuase running the model will change
        # the wave features.
        self.k_init = np.array([k], dtype='float')
        self.l_init = np.array([l], dtype='float')
        self.m_init = np.array([m], dtype='float')
        self.w0_init = np.array([w0], dtype='float')
        self.kh_init = np.array([np.sqrt(self.k_init**2 + self.l_init**2)])
        self.x_init = np.array([0], dtype='float')
        self.y_init = np.array([0], dtype='float')
        self.z_init = np.array([z0], dtype='float')

        # These are empty for now- they get filled in during model runs. 
        self.x_all = []
        self.y_all = []
        self.z_all = []
        self.m_all = []
        self.w0_all = []
        self.E_all = []
        self.Ac_all = []


    def help(self):
        """
        Print instructions on how to use wave class
        """
        text = '''
Instructions for using ray tracing model.
\nGenerate a wave with chosen properties or use the defualt Parameters
'''
        print(text)


    def model_error_message(self, x, y, z, m, idx, idx2):
        error_message = '''
        current variables:
-----------------
x = {}
y = {}
z = {}
N2 = {}
U = {}
V = {}
m = {}
'''.format(x, y, z,
 self.N2[idx2], self.U[idx], self.V[idx], m)

        return error_message

    def properties(self):
        """
        Print wave properties
        """
        txt = '''Wave Properties:
---------------
    k: {}
    l: {}
    m: {}
    kh: {}
    Frequency: {}
'''.format(np.array2string(self.k_init), self.l_init, self.m_init, self.kh_init, self.w0_init)

        print(txt)
  
    def back_trace(self, satGEM, duration=24, tstep=5,status=2,
                   seafloor=4000, print_run_report=False, updates=False):
        """
        3 dimensional ray tracing within the time evolving satGEM density and velocity fields
        
        - load in the satGEM object when running the model
        - Structure of integration outlines in ray tracing docs. 



        Parameters
        ----------
        duration:  Run duration (in hours)
        tstep: time step of model in seconds
        status:
        seafloor: choose a seafloor depth in meters (maybe integrate bathymetry at some point using gebco data)
        
        
        Returns
        -------
        """

        # Set up model run
        


class satGEM_field(object):
    """
    load in the satGEM data as an object (this might be wierd though becuase the h5py module loads in each file as an object so not sure...)
    
    The objects built in functions can then be used to easily access the data set without ever having to load the whole thing in.
    """

    def __init__(self):
        # Load satGEM data as h5py file objects
        gamma_file = h5py.File('DIMES_GAMMA_09_12_upd.mat')
        vel_file = h5py.File('DIMES_vel_09_12_upd.mat')
        ts_file = h5py.File('DIMES_TS_09_12_upd.mat')
        gamma = gamma_file['satGEM_gamma']

        self.u = vel_file['satGEM_east']
        self.v = vel_file['satGEM_north']
        self.temp = ts_file['satGEM_temp']
        self.sal = ts_file['satGEM_sal']

        # Data grids
        self.time = gamma_file['time']
        self.depth_grid = gamma_file['depthlvl']
        self.lon = gamma_file['lons']
        self.lat = gamma_file['lats']

        # The u and v grids are one point off each so I need
        # to figure out how to handle this
        self.centerlat = vel_file['centerlat']
        self.centerlon = vel_file['centerlon']
    

    def locate(lon, lat, depth, time):
        """
        Locate point/points within the satgem data set

        Parameters
        ----------
        lon: longitude of point
        lat: latitude of point
        depth: depth of point
        time: of point

        Returns
        -------
        lon_id: index along longitude axis
        lat_id: index along latitude axis
        depth_id: index along latitude axis
        time_id: index along time axis

        These are for the velocity grids
        centerlon_id: index along centerlon axis
        centerlat_id: index along centerlat axis


        """

        # Add warning for out of time and space boundaries. 

        lon_id = np.argmin(np.abs(self.lon[:] - lon))
        lat_id = np.argmin(np.abs(self.lat[:] - lat))
        depth_id = np.argmin(np.abs(self.depth_grid[:] - depth))
        time_id = np.argmin(np.abs(self.time[:] - time))

        centerlon_id = np.argmin(np.abs(self.centerlon[:] - lon))
        centerlat_id = np.argmin(np.abs(self.centerlat[:] - lat))

        return lon_id, lat_id, depth_id, time_id, centerlon_id, centerlat_id
            
        



# def testing():
#     """
#     This is where I load parameters to test functions
#     """

#     # These are parameters taken from the lee wave dissertation project
#     l1 =  -0.000139543
#     k1 = 0.000324448
#     m1 = -0.00976433
#     z0 = 1500
#     w0 = -0.000132755
#     wave1 = wave(k=k1, l=l1, m=m1, w0=w0, z0=z0)


#     # run models
#     duration = 48
#     tstep = 10
#     status = 6 # intervals to give run status
#     wave1.backward3d(duration=duration, tstep=tstep,
#                      status=status, print_run_report=True)


#     plt.figure()
#     plt.plot(wave1.x_ray, wave1.z_ray)
#     plt.gca().invert_yaxis()
