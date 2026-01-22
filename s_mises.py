"""Abaqus script to compute signed mises stress

S_MISES is calculated according to the Abaqus 2023 method, sign(trace(S)),
and stored in each frame of the odb file.

Usage:

    abaqus python s_mises.py Job-1.odb [Job-2.odb ...]

Carl Osterwisch, September 2023
"""

from __future__ import print_function, with_statement  # use python3 syntax
import numpy as np

__version__ = "1.2.0"
foName = 'S_MISES'  # fieldOutput name for results

def onJobCompletion():
    """Copy this method into abaqus_v6.env for automatic execution"""
    import os, s_mises
    s_mises.fromOdb(os.path.join(savedir, id + ".odb"))


def sign_trace(A):
    """Compute sign(trace(A))

    A is a list of 3D stress tensors.
    Each stress tensor is a list in the form S11, S22, S33, S12, S13, S23

    Returns +1 for trace >= 0, -1 otherwise

    Examples:
    >>> S11, S22, S33, S12, S13, S23 = -0.4, 0.2, 0.1, 0.4, 0.5, 0.6
    >>> sign_trace( [[S11, S22, S33, S12, S13, S23],
    ...              [0.2, 0.0, -.2, 0.3, -.5, 0.0],
    ...              [0.2, 0.0, 0.0, 0.3, -.5, 0.0]] )
    array([[-1.], [ 1.], [ 1.]])

    >>> sign_trace( [[S11, S22, S33, S12],
    ...              [0.2, 0.0, -.2, 0.3],
    ...              [0.2, 0.0, 0.0, 0.3]] )
    array([[-1.], [ 1.], [ 1.]])

    >>> sign_trace( [[S11, S22, S12],
    ...              [0.2, 0.0, 0.3],
    ...              [0.2, 0.0, 0.3]] )
    array([[-1.], [ 1.], [ 1.]])
    """

    A = np.asarray(A)
    assert 2 == len(A.shape), "Data must be a 2D array of tensors"
    if 6 == A.shape[1]: # S11, S22, S33, S12, S13, S23
        trace = np.sum(A[:,0:3], axis=1)
    elif 4 == A.shape[1]: # S11, S22, S33, S12
        trace = np.sum(A[:,0:3], axis=1)
    elif 3 == A.shape[1]: # S11, S22, S12
        trace = np.sum(A[:,0:2], axis=1)
    else:
        raise RuntimeError("Tensor length {} is unsupported".format(A.shape[1]))
    result = np.ones_like(trace)
    result[trace < 0] = -1
    return result.reshape([-1,1])


def calculate(outputFrame):
    """Calculate signed mises stress fieldOutput and store in outputFrame"""
    import abaqusConstants

    S = outputFrame.fieldOutputs['S']
    if foName in outputFrame.fieldOutputs:
        S_MISES = outputFrame.fieldOutputs[foName]
    else:
        S_MISES = outputFrame.FieldOutput(
                name=foName,
                description="Signed Mises equivalent stress",
                type=abaqusConstants.SCALAR,
            )

    for block in S.bulkDataBlocks:
        if not hasattr(block.mises, "reshape"):
            continue  # no mises data available
        try:
            options = dict(
                position=block.position,
                instance=block.instance,
                labels=np.unique(block.elementLabels),
                data=sign_trace(block.data)*block.mises.reshape(-1, 1),
            )
            if np.any(block.sectionPoint):
                options["sectionPoint"] = block.sectionPoint
        except RuntimeError as E:
            print(E)
        else:
            S_MISES.addData(**options)


def fromOdb(odbName):
    """Add signed mises fieldOutput to each odb frame which contains stress"""

    from odbAccess import openOdb
    from contextlib import closing

    with closing(openOdb(odbName)) as odb:
        for step in odb.steps.values():
            print(step.name)
            for frame in step.frames:
                if "S" in frame.fieldOutputs:
                    print(frame.description)
                    calculate(frame)


import sys
for arg in sys.argv[1:]:
    if "--help" == arg:
        print(__doc__)
    elif "--test" == arg:
        import doctest
        doctest.testmod(verbose=True)
    else:
        if len(sys.argv) > 2: print(arg)
        fromOdb(odbName = arg)
