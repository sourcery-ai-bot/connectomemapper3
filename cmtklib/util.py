# Copyright (C) 2009-2017, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

""" CMTK Utility functions
""" 



import warnings

warnings.simplefilter("ignore")
from collections import OrderedDict

from os import path as op
import numpy as np
import networkx as nx

class bcolors:
    """ Utility class for color unicode
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_graphs(output_dir,subjects,parcellation_scheme,weight):

    if parcellation_scheme == 'Lausanne2008':
        bids_atlas_label = 'L2008'
    elif parcellation_scheme == 'Lausanne2018':
        bids_atlas_label = 'L2018'
    elif parcellation_scheme == 'NativeFreesurfer':
        bids_atlas_label = 'Desikan'

    if parcellation_scheme == 'NativeFreesurfer':
        subj_dir = os.path.join(output_dir,subj)
        subj_session_dirs = glob(op.join(subj_dir, "ses-*"))
        subj_sessions = ['ses-{}'.format(subj_session_dir.split("-")[-1]) for subj_session_dir in subj_session_dirs]

        if len(subj_sessions) > 0: #Session structure
            for subj_session in subj_sessions:
                conn_derivatives_dir = op.join(output_dir,'cmp', subj, subj_session, 'connectivity')

                #Extract the connectivity matrix
                #self.subject+'_label-'+bids_atlas_label+'_desc-scale5_conndata-snetwork_connectivity'
                connmat_fname = op.join(conn_derivatives_dir,'{}_{}_label-{}_conndata-snetwork_connectivity.gpickle'.format(sub,subj_session,bids_atlas_label))
                connmat_gp = nx.read_gpickle(connmat_fname)
                connmat = nx.to_numpy_matrix(connmat_gp,weight=weight,dtype=np.float32)
    else:
        # For each parcellation scale
        for scale in np.arange(1,6):
            for subj in subjects:
                subj_dir = os.path.join(output_dir,subj)
                subj_session_dirs = glob(op.join(subj_dir, "ses-*"))
                subj_sessions = ['ses-{}'.format(subj_session_dir.split("-")[-1]) for subj_session_dir in subj_session_dirs]

                if len(subj_sessions) > 0: #Session structure
                    for subj_session in subj_sessions:
                        conn_derivatives_dir = op.join(output_dir,'cmp', subj, subj_session, 'connectivity')

                        #Extract the connectivity matrix
                        #self.subject+'_label-'+bids_atlas_label+'_desc-scale5_conndata-snetwork_connectivity'
                        connmat_fname = op.join(conn_derivatives_dir,'{}_{}_label-{}_desc-scale{}_conndata-snetwork_connectivity.gpickle'.format(sub,subj_session,bids_atlas_label,scale))
                        connmat_gp = nx.read_gpickle(connmat_fname)
                        connmat = nx.to_numpy_matrix(connmat_gp,weight=weight,dtype=np.float32)


def length(xyz, along=False):
    """
    Euclidean length of track line

    Parameters
    ----------
    xyz : array-like shape (N,3)
       array representing x,y,z of N points in a track
    along : bool, optional
       If True, return array giving cumulative length along track,
       otherwise (default) return scalar giving total length.

    Returns
    -------
    L : scalar or array shape (N-1,)
       scalar in case of `along` == False, giving total length, array if
       `along` == True, giving cumulative lengths.

    Examples
    --------
    >>> xyz = np.array([[1,1,1],[2,3,4],[0,0,0]])
    >>> expected_lens = np.sqrt([1+2**2+3**2, 2**2+3**2+4**2])
    >>> length(xyz) == expected_lens.sum()
    True
    >>> len_along = length(xyz, along=True)
    >>> np.allclose(len_along, expected_lens.cumsum())
    True
    >>> length([])
    0
    >>> length([[1, 2, 3]])
    0
    >>> length([], along=True)
    array([0])
    """
    xyz = np.asarray(xyz)
    if xyz.shape[0] < 2:
        if along:
            return np.array([0])
        return 0
    dists = np.sqrt((np.diff(xyz, axis=0) ** 2).sum(axis=1))
    if along:
        return np.cumsum(dists)
    return np.sum(dists)
    
def magn(xyz,n=1):
    ''' magnitude of vector
        
    '''    
    mag=np.sum(xyz**2,axis=1)**0.5
    imag=np.where(mag==0)
    mag[imag]=np.finfo(float).eps

    if n>1:
        return np.tile(mag,(n,1)).T
    return mag.reshape(len(mag),1)   
    
def mean_curvature(xyz):    
    ''' Calculates the mean curvature of a curve
    
    Parameters
    ------------
    xyz : array-like shape (N,3)
       array representing x,y,z of N points in a curve
        
    Returns
    -----------
    m : float 
        float representing the mean curvature
    
    Examples
    --------
    Create a straight line and a semi-circle and print their mean curvatures
    
    >>> from dipy.tracking import metrics as tm
    >>> import numpy as np
    >>> x=np.linspace(0,1,100)
    >>> y=0*x
    >>> z=0*x
    >>> xyz=np.vstack((x,y,z)).T
    >>> m=tm.mean_curvature(xyz) #mean curvature straight line    
    >>> theta=np.pi*np.linspace(0,1,100)
    >>> x=np.cos(theta)
    >>> y=np.sin(theta)
    >>> z=0*x
    >>> xyz=np.vstack((x,y,z)).T
    >>> m=tm.mean_curvature(xyz) #mean curvature for semi-circle    
    '''
    xyz = np.asarray(xyz)
    n_pts = xyz.shape[0]
    if n_pts == 0:
        raise ValueError('xyz array cannot be empty')
    
    dxyz=np.gradient(xyz)[0]            
    ddxyz=np.gradient(dxyz)[0]
    
    #Curvature
    k = magn(np.cross(dxyz,ddxyz),1)/(magn(dxyz,1)**3)    
        
    return np.mean(k)
