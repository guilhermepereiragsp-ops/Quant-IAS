"""
Module: funcs_ParametricSplines.py
@author: Carlos Vinhais
cvinhais@gmail.com
Jun 08 2019
"""

import numpy as np
import vtk

math = vtk.vtkMath()
pi = math.Pi()
deg2rad = pi/float(180)
rad2deg = float(180)/pi


def ParametricOpenedSpline( points, N ):
    # ---------------------------------
    spline = vtk.vtkParametricSpline()
    spline.SetPoints( points )
    spline.ClosedOff()
    # ---------------------------------
    functionSource = vtk.vtkParametricFunctionSource()
    functionSource.SetParametricFunction( spline )
    functionSource.SetUResolution( N - 1 )
    # functionSource.SetVResolution( N - 1 )
    # functionSource.SetWResolution( N - 1 )
    functionSource.GenerateTextureCoordinatesOn()
    functionSource.Update()
    # ---------------------------------
    polydata = vtk.vtkPolyData()
    polydata = functionSource.GetOutput()
    K = polydata.GetNumberOfPoints()
    # ---------------------------------    
    lines = vtk.vtkCellArray()
    for k in range( K - 1 ):
        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, k)
        line.GetPointIds().SetId(1, k + 1)
        lines.InsertNextCell( line ) 
    # ---------------------------------
    spline = vtk.vtkPolyData()
    spline.SetPoints( polydata.GetPoints() )
    spline.SetLines( lines )
    
    return spline


def SimpleSegment( P0, P1 ):
    # ---------------------------------
    points = vtk.vtkPoints()
    points.InsertNextPoint( P0 )
    points.InsertNextPoint( P1 )
    # ---------------------------------    
    lines = vtk.vtkCellArray()
    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, 0)
    line.GetPointIds().SetId(1, 1)
    lines.InsertNextCell( line ) 
    # ---------------------------------
    polydata = vtk.vtkPolyData()
    polydata.SetPoints( points )
    polydata.SetLines( lines )
    # ---------------------------------
    return polydata


def ComputeLengthOfSpline( spline ):
    N = spline.GetNumberOfPoints()
    # ---------------------------------
    length  = 0.0
    for n in range(N - 1):
        P0 = spline.GetPoint( n )
        P1 = spline.GetPoint( n + 1 )
        length += np.sqrt( math.Distance2BetweenPoints(P0, P1) )
    # ---------------------------------
    return length

