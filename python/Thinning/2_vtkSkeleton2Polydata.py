# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 16:53:08 2025

@author: gui_m
"""

import vtk
import datetime
import numpy as np

tic = datetime.datetime.now()

INPUTDIR = "../../datasets/"

worklistFilename = INPUTDIR + 'STEN_worklist.txt'
worklist = np.loadtxt( worklistFilename, dtype=str )
# print( worklist )
# print( len(worklist) )

for i in range(min(1, len(worklist))):
    dataset = worklist[i]

    # dataset = "Sten0004"

    res = "025"
    # res = "050"
    
    # threshold = 160
    threshold = 180
    # threshold = 200
    
    morph = "none"
    # morph = "open"
    # morph = "close"
    
    inputFilename = './output/%s_%s_%s_%s_skeleton.vtk' % ( dataset, res, threshold, morph )
    # inputFilename = './teste/%s_%s_%s_%s_roi_skeleton.vtk' % (dataset, res, threshold, morph)
    
    outputFilename = './output/%s_%s_%s_%s_polydata.vtk' % ( dataset, res, threshold, morph )
    # outputFilename = './teste/%s_%s_%s_%s_roi_polydata.vtk' % ( dataset, res, threshold, morph )
    
    # Leitura do arquivo VTK (assumido como vtkImageData)
    print ("Reading:", inputFilename)
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(inputFilename)
    reader.Update()
    image = reader.GetOutput()
    
    dims = image.GetDimensions()
    spacing = image.GetSpacing()
    origin = image.GetOrigin()
    
    # Acessar os valores da imagem
    scalars = image.GetPointData().GetScalars()
    
    # Extrair pontos com valor > 0
    points = vtk.vtkPoints()
    # verts = vtk.vtkCellArray()
    
    for k in range(dims[2]):
        for j in range(dims[1]):
            for i in range(dims[0]):
                idx = k * dims[0] * dims[1] + j * dims[0] + i
                value = scalars.GetTuple1(idx)
                if value > 0:
                    coord = (
                        origin[0] + i * spacing[0],
                        origin[1] + j * spacing[1],
                        origin[2] + k * spacing[2]
                    )
                    pid = points.InsertNextPoint(coord)
                    # verts.InsertNextCell(1)
                    # verts.InsertCellPoint(pid)
    
    # Criar polydata com os pontos
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    # polydata.SetVerts(verts)
    
    # Salvar como polydata .vtk
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(outputFilename)
    writer.SetInputData(polydata)
    writer.Write()
    
    toc = datetime.datetime.now()
    print(toc-tic)

# --------------------------------------------------
# VTK visuialization pipeline
# Using spheres or cubes to glyph all polydata points
# --------------------------------------------------

# Spheres (with radius of 0.31 mm ?)
glyphSource = vtk.vtkSphereSource()
glyphSource.SetRadius( 0.31 )

# Cubes (with Lengths = pixel spacing)
glyphSource = vtk.vtkCubeSource()
glyphSource.SetXLength( spacing[0] )
glyphSource.SetYLength( spacing[1] )
glyphSource.SetZLength( spacing[2] )

glyph = vtk.vtkGlyph3D()
glyph.SetInputData( polydata )
glyph.SetSourceConnection( glyphSource.GetOutputPort() )
glyph.GeneratePointIdsOn()
glyph.Update()

# Create mappers
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputData( glyph.GetOutput() )

mapper2 = vtk.vtkLabeledDataMapper()
mapper2.SetInputData( polydata )
mapper2.SetLabelModeToLabelIds()

# Create actors, and connect mappers
actor_axes = vtk.vtkAxesActor()
actor_axes.SetTotalLength(10.0, 10.0, 10.0)
actor_axes.AxisLabelsOff()

actor_glyphs = vtk.vtkActor()
actor_glyphs.SetMapper( mapper1 )
actor_glyphs.GetProperty().SetColor(1,0,1) # RGB

# Create a renderer, and add actors to it
ren = vtk.vtkRenderer()
ren.SetBackground(0,0,0) # RGB
ren.AddActor( actor_axes )
ren.AddActor( actor_glyphs )

# Create a render window
renwin = vtk.vtkRenderWindow()
renwin.SetSize( 512, 512 )
renwin.SetWindowName( 'Glyph 3D Points' )
renwin.AddRenderer( ren )

# Create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow( renwin )

# --------------------------------------------------

# render and enable user interface interactor
iren.Initialize()
renwin.Render()
iren.Start()

print("EOF.")
