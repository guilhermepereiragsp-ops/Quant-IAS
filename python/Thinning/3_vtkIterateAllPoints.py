""" vtkIterateAllPoints.py """

# import itk
import vtk
import numpy as np
import datetime

tic = datetime.datetime.now()

math = vtk.vtkMath()
pi = math.Pi()
deg2rad = pi/float(180)
rad2deg = float(180)/pi





INPUTDIR = "../../datasets/"

worklistFilename = INPUTDIR + 'STEN_worklist.txt'
worklist = np.loadtxt( worklistFilename, dtype=str )
print( worklist )
print( len(worklist) )

for i in range( min(1, len(worklist))):
    dataset = worklist[i]
    # dataset = "Sten0011"
    
    res = "025"; RR = 3 * 0.25**2 + 0.0001;
    # res = "050"; RR = 3 * 0.50**2 + 0.0001;
     
    # RR = 1 + 1e-4 
    # Rmax = np.sqrt( RR )
    
    # threshold = 160
    threshold = 180
    # threshold = 200
    
    morph = "none"
    # morph = "open"
    # morph = "close"
     
    
    inputFilename  = './output/%s_%s_%s_%s_polydata.vtk' % ( dataset, res, threshold, morph )
    # inputFilename  = './teste/%s_%s_%s_%s_roi_polydata.vtk' % ( dataset, res, threshold, morph )
    
    outputFilename = './output/%s_%s_%s_%s_polydata_line.vtk' % ( dataset, res, threshold, morph )
    # outputFilename = './teste/%s_%s_%s_%s_roi_polydata_line.vtk' % ( dataset, res, threshold, morph )
    
    # inputFilename  ='./output/test_polydata.vtk'
    # outputFilename  ='./output/test_polydata_line.vtk'
    
    # VTK PolyData - input
    # ------------------------------------------------------------
    print ('Reading VTK PolyData:', inputFilename )
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName( inputFilename )
    reader.Update()    
    
    # polydata = vtk.vtkPolyData()
    polydata = reader.GetOutput()
    
    print( polydata.GetNumberOfPoints() )
    
    # Find polydata
    # --------------------------------  
    print ('Finding VTK PolyData Lines ...' ) 
    
    lines = vtk.vtkCellArray()
    
    N = polydata.GetNumberOfPoints()
    
    for n in range( N - 1 ):    
        P = polydata.GetPoint( n )    
        for m in range( n + 1, N ):
            Q = polydata.GetPoint( m )
            dd = math.Distance2BetweenPoints(P,Q)
            if ( dd < RR ):            
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, n)
                line.GetPointIds().SetId(1, m)
                lines.InsertNextCell( line ) 
    
    
    # VTK polydata 2 - output
    # polydata2 = vtk.vtkPolyData()
    # polydata2.SetPoints( polydata.GetPoints() )
    polydata.SetLines( lines )
    
    print( polydata.GetNumberOfPoints() )
    print( polydata.GetNumberOfCells() )
    
    # # Clean polydata ?
    # # --------------------------------  
    # print ('Cleaning VTK PolyData ...' ) 
    # tolerance = 0.001
    # clean = vtk.vtkCleanPolyData()
    # clean.SetInputData( polydata )
    # clean.ToleranceIsAbsoluteOn()
    # clean.SetAbsoluteTolerance( tolerance )
    # clean.PointMergingOn()
    # clean.Update()
    
    # polydata2 = vtk.vtkPolyData()
    # polydata2 = clean.GetOutput()
    
    
    # Output polydata
    # --------------------------------  
    print ('Writing VTK PolyData:', outputFilename)
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData( polydata )
    writer.SetFileName( outputFilename )
    writer.Write()
        
    toc = datetime.datetime.now()
    print(toc-tic)

# # --------------------------------------------------
# # VTK visuialization pipeline
# # Using spheres or cubes to glyph all polydata points
# # --------------------------------------------------

# Spheres (with radius of 0.31 mm ?)
glyphSource = vtk.vtkSphereSource()
glyphSource.SetRadius( 0.31 )

# Cubes (with Lengths = pixel spacing)
glyphSource = vtk.vtkCubeSource()
glyphSource.SetXLength( 0.05 ) # spacing[0] )
glyphSource.SetYLength( 0.05 ) # spacing[1] )
glyphSource.SetZLength( 0.05 ) #spacing[2] )

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

# actor_labels = vtk.vtkActor2D()
# actor_labels.SetMapper( mapper2 )
# actor_labels.GetProperty().SetColor(1,1,1) # RGB

# Create a renderer, and add actors to it
ren = vtk.vtkRenderer()
ren.SetBackground(0,0,0) # RGB
ren.AddActor( actor_axes )
ren.AddActor( actor_glyphs )
# ren.AddActor( actor_labels )

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


print('EOF.')