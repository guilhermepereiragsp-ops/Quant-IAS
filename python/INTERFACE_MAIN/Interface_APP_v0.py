"""
Module: APP.py
@author: Carlos Vinhais and Guilherme Pereira
cvinhais@gmail.com
"""
import itk
import os 
import sys  
import numpy as np
import vtk
import csv
# from vtk.util import numpy_support as ns

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox


import Interface_GUI_v0
import funcs_ParametricSplines as spl

math = vtk.vtkMath()
pi = math.Pi()
deg2rad = pi/float(180)
rad2deg = float(180)/pi

""" A class for Interface APP """

class InterfaceApp( QMainWindow ):
    
    def __init__(self):
      
        # Parent constructor
        super( InterfaceApp, self ).__init__()
          
        self.ui = Interface_GUI_v0.Ui_MainWindow()
        self.ui.setupUi( self )
          
        self.APP_NAME    = 'STENOSIS'
        self.APP_VERSION = 'v1 (Maio 2025)'
          
        # APP Callbacks
        # --------------------------------------------------------        
        # "Menu -> File, Help"
        # self.ui.FileNewAction.triggered.connect(  self.File_New )
        # self.ui.FileOpenAction.triggered.connect(  self.File_Open )
        self.ui.FileQuitAction.triggered.connect(  self.File_Quit )
        self.ui.HelpAboutAction.triggered.connect( self.Help_About )
        
        # UI group "Input Data"
        self.ui.spinBox_Dataset.valueChanged.connect( self.SelectCase )
        self.ui.button_LoadDataset.clicked.connect(   self.OnClick_LoadDataset )  
        self.ui.button_ContourImage.clicked.connect(  self.OnClick_ContourImage )
        # self.ui.button_GenerateSkeleton.clicked.connect(  self.OnClick_LoadROISkeleton )
        self.ui.button_UpdateSpline.clicked.connect(  self.OnClick_UpdateSpline )
        self.ui.button_ResetSpline.clicked.connect(  self.ResetSpline )
        self.ui.button_SaveSpline.clicked.connect(  self.OnClick_WriteSpline )
        
        # UI group "Spline"
        self.ui.spinBox_Nspline.valueChanged.connect( self.callback_Nspline )
        # self.ui.spinBox_Rspline.valueChanged.connect( self.callback_Rspline )        
        
        self.ui.qplt1.exportDat_Button.clicked.connect(
            lambda: self.ui.qplt1.export_table_to_csv(self.dataset, self.isovalue)
        )

      
        # USER default settings
        # --------------------------------------------------------
        self.workFilename = '../../datasets/STEN_worklist.txt'
        self.INPUTDIR1    = '../../datasets/stens_isotropic_025/'
        self.INPUTDIR2    = '../Thinning/output/'
        # self.INPUTDIR2    = '../Thinning/teste/'
        self.OUTPUTDIR    = './output/'
        
        # self.INPUTDIR1    = '../../datasets/stens_isotropic_050/'
        # self.INPUTDIR2    = '../Thinning/output/'     # SNAKES
      
        
        # VTK objects        
        # --------------------------------------------------------        
        self.vtkimg     = vtk.vtkImageData()
        self.outline    = vtk.vtkPolyData()
        self.isosurface = vtk.vtkPolyData()		
        
        # self.ROIoutline    = vtk.vtkPolyData()

        self.skeleton   = vtk.vtkPolyData()
        self.geopath    = vtk.vtkPolyData()
        self.spline     = vtk.vtkPolyData()
        self.centerline = vtk.vtkPolyData()
        
        self.mesh       = vtk.vtkPolyData()
        self.closest    = vtk.vtkPolyData()
        
        self.picker = vtk.vtkPointPicker()
        self.ui.qvtk1.iren.SetPicker( self.picker )
        self.picker.SetTolerance( 0.005 )
        self.picker.AddObserver( vtk.vtkCommand.EndPickEvent, self.OnPick_Event )        
        
        self.locator  = vtk.vtkPointLocator()

        self.dijkstra       = vtk.vtkDijkstraGraphGeodesicPath()
        self.dijkstraIdList = vtk.vtkIdList()         

        self.picked_pid_L0 = 0 # 1288
        self.picked_pid_L1 = -1 # 11827
        self.pickedPoint   = [0,0,0]
        self.pickedPoint0  = [ 1,0,0]
        self.pickedPoint1  = [-1,0,0]
           
        self.geolength  = 0.0
        
    
       
        # FIRST OPENING of APP
        # --------------------------------------------------------
        self.worklist = np.loadtxt( self.workFilename, dtype='str' )
        
        

    # ========================================================
    # INPUT DATA
    # ========================================================
    def SelectCase( self ):        
        n = int( self.ui.spinBox_Dataset.value() )
        
        # find corresponding dataset in worklist
        dataset = self.worklist[n]
        
        self.ui.lineEdit_Dataset.setText( dataset )
    
    
    def OnClick_LoadDataset(self):
        self.ui.statusBar.showMessage( 'Load Button clicked!' )
        # -----------------------------------------
        self.dataset  = str( self.ui.lineEdit_Dataset.text() )
    
        inputFilename1 = self.INPUTDIR1 + self.dataset + '_isotropic_025.vtk'
        inputFilename2 = self.INPUTDIR2 + '%s_025_180_none_polydata_line.vtk' %self.dataset
        # inputFilename2 = self.INPUTDIR2 + '%s_025_180_none_roi_polydata_line.vtk' %self.dataset
        #print( inputFilename2 )
        
        
        # -----------------------------------------
        # Load VTK Image (vtkimg)
        # -----------------------------------------
        reader1 = vtk.vtkStructuredPointsReader()
        reader1.SetFileName( inputFilename1 )
        reader1.Update()
        
        outlineFilter = vtk.vtkOutlineFilter()
        outlineFilter.SetInputConnection( reader1.GetOutputPort() )
        outlineFilter.Update()
        
        self.vtkimg   = reader1.GetOutput() 
        self.outline  = outlineFilter.GetOutput() 
        
        
        # -----------------------------------------
        # Load skeleton
        # -----------------------------------------
        reader2 = vtk.vtkPolyDataReader()
        reader2.SetFileName( inputFilename2 ) 
        reader2.Update()

        self.skeleton = vtk.vtkPolyData()
        self.skeleton = reader2.GetOutput()
        
        self.locator.SetDataSet( self.skeleton )
        self.dijkstra.SetInputData( self.skeleton )

 
       
        # VTK rendering 1
        # -----------------------------------------
        self.ui.qvtk1.CleanViewer()
        # self.ui.qvtk1.CreateActors()        # necessario ?
        self.ui.qvtk1.SetSceneVisibility()
        # -----------------------------------------
        self.ui.qvtk1.cornerAnnotation.SetText( 2, self.dataset )        
        self.ui.qvtk1.DisplayImageOutline( self.outline )
        self.ui.qvtk1.DisplaySkeleton( self.skeleton )    
        self.ui.qvtk1.renWin.Render()
        self.ui.qvtk1.ResetCamera()
        

        # -------------------------------------------
        self.ui.statusBar.showMessage( 'Input Filename: %s' % inputFilename1 )     
               
        self.OnClick_ContourImage()
        
        # UI Visibility
        self.ui.IsoSurfaceGroup.setEnabled(True)
        # self.ui.ROIGroup.setEnabled(True)
        self.ui.LandmarksGroup.setEnabled(True)
        self.ui.SplineGroup.setEnabled(True)
        # self.ui.qvtk1.checkBox3.setEnabled( 1 )
        # self.ui.qvtk1.checkBox4.setEnabled( 1 )
        # self.ui.qvtk1.checkBox6.setEnabled( 1 )
        
    # ========================================================
    # CONTOUR
    # ========================================================        
    def OnClick_ContourImage(self):
        self.ui.statusBar.showMessage( 'Contour Button clicked!' )
        # -----------------------------------------
        self.isovalue = int( self.ui.spinBox_Isovalue.value() )
        fsmooth = float( self.ui.spinBox_Smooth.value()  )
        Nsmooth = int( self.ui.spinBox_Iters.value() )
        # -----------------------------------------
        contourFilter = vtk.vtkContourFilter()
        contourFilter.SetValue(0, self.isovalue)
        contourFilter.SetInputData( self.vtkimg )
        contourFilter.Update()
        
        print(f"Smooth, {fsmooth} \n Iters, {Nsmooth}")
    
        if ( self.ui.spinBox_Smooth.isEnabled()  ): 
            smoothFilter = vtk.vtkSmoothPolyDataFilter()
            smoothFilter.SetInputData( contourFilter.GetOutput() )
            smoothFilter.SetRelaxationFactor( fsmooth )
            smoothFilter.SetNumberOfIterations( Nsmooth )
            smoothFilter.Update()

            self.isosurface = smoothFilter.GetOutput()
            
        else:
            
            self.isosurface = contourFilter.GetOutput()
        
        # VTK rendering 1
        # -----------------------------------------        
        self.ui.qvtk1.DisplayIsosurface( self.isosurface )             
        self.ui.qvtk1.renWin.Render()
    
        
        # UI update
        # -----------------------------------------
        self.ui.statusBar.showMessage('Data OK. Ready.')
        
    # ========================================================
    # ROI
    # ========================================================
    # def OnClick_LoadROISkeleton(self):
    #     self.ui.statusBar.showMessage( 'Load Button clicked!' )
    #     # -----------------------------------------
    #     self.dataset  = str( self.ui.lineEdit_Dataset.text() )
    
    #     inputFilename1 = self.INPUTDIR1 + self.dataset + '_isotropic_025.vtk'
    #     inputFilename2 = self.INPUTDIR2 + '%s_025_180_none_polydata_line.vtk' %self.dataset
    #     #print( inputFilename2 )
        
    #     Dimension = 3
    #     PixelType = itk.US
    #     ImageType = itk.Image[PixelType, Dimension]
        

    #     # -----------------------------------------
    #     # Load VTK Image (vtkimg)
    #     # -----------------------------------------
    #     reader1 = vtk.vtkStructuredPointsReader()
    #     reader1.SetFileName( inputFilename1 )
    #     reader1.Update()
        
    #     self.roiimg   = reader1.GetOutput()
        
    #     # Define as dimensões do ROI cúbico (em pixels)
    #     roi_size = [self.ui.spinBox_X.value(), self.ui.spinBox_Y.value(), self.ui.spinBox_Z.value()]  # largura, altura, profundidade (x, y, z)
        
    #     # Obtém as dimensões da imagem original
    #     image_size = reader1.GetOutput.GetLargestPossibleRegion().GetSize()
    #     print("Tamanho da imagem original:", image_size)
        
    #     # Calcula o índice do início do ROI para centralizar o cubo
    #     start_index = [
    #         int((image_size[0] - roi_size[0]) / 2),
    #         int((image_size[1] - roi_size[1]) / 2),
    #         int((image_size[2] - roi_size[2]) / 2),
    #     ]
        
    #     print("Índice inicial do ROI:", start_index)
        
    #     # Define a região do ROI
    #     roi_region = itk.ImageRegion[Dimension]()
    #     roi_region.SetIndex(start_index)
    #     roi_region.SetSize(roi_size)
        
    #     # Cria o filtro ROI e aplica
    #     roi_filter = itk.RegionOfInterestImageFilter[ImageType, ImageType].New()
    #     roi_filter.SetRegionOfInterest(roi_region)
    #     roi_filter.SetInput(self.roiimg)
    #     roi_filter.Update()
        
    #     # Pega a imagem recortada
    #     roi_img = roi_filter.GetOutput()
        
    #     outlineFilter = vtk.vtkOutlineFilter()
    #     outlineFilter.SetInputConnection( roi_img )
    #     outlineFilter.Update()
        
    #     self.roiimg   = reader1.GetOutput() 
    #     self.ROIoutline  = outlineFilter.GetOutput() 
        
        
    # ========================================================
    # LANDMARKS
    # ========================================================
    def OnPick_Event(self, caller, event):         
        pickId = self.picker.GetPointId()
        if ( pickId >= 0 ):
            
            pickedPoint = self.picker.GetPickPosition()         
            
            # Find the closest point ID of skeleton polydata
            # -----------------------------------------
            pid = self.locator.FindClosestPoint( pickedPoint )            
            self.pickedPoint = self.skeleton.GetPoint( pid ) 
            print( pid, self.pickedPoint )
            
            if( self.ui.radio_L0.isChecked() ):
                self.picked_pid_L0 = pid
                self.ui.qvtk1.GlyphPickedPoint( self.pickedPoint ) 
            else:
                self.picked_pid_L1 = pid
                self.ui.qvtk1.GlyphPickedPoint( self.pickedPoint )
                
            # Garante que os dois pontos estão definidos
            if self.picked_pid_L0 is None or self.picked_pid_L1 is None:
                return
               
            # dijkstra.GetIdList() output will give ids in reverse order! 
            self.dijkstra.SetStartVertex( self.picked_pid_L1 ) # 
            self.dijkstra.SetEndVertex(   self.picked_pid_L0 ) # 
            self.dijkstra.Update()
            
            self.geopath   = self.dijkstra.GetOutput()
            self.geolength = spl.ComputeLengthOfSpline( self.geopath )
            print( 'geolength =',  self.geolength )
            
            self.spline.DeepCopy( self.geopath )
            print( self.spline.GetNumberOfPoints() )
            
            
            self.UpdateSplineRadii()
            self.UpdateGraphPlotter()  
            self.ResetVlinesPlotter()
            self.UpdateTube()
            self.UpdateCenterline()
            self.UpdateTriangularMesh()
            # self.UpdateCuts()
            
            
            # VTK rendering 1
            # -----------------------------------------
            self.ui.qvtk1.GlyphPickedPoint( self.pickedPoint )    
            self.ui.qvtk1.DisplayGeoPath( self.geopath )
            self.ui.qvtk1.DisplaySpline( self.spline ) 
            self.ui.spinBox_Nspline.setValue( self.spline.GetNumberOfPoints() ) 
            self.ui.spinBox_Lspline.setValue(self.geolength)
            
      
        self.ui.qvtk1.renWin.Render()
        
        # self.ui.qvtk1.checkBox7.setEnabled( 1 )
        
    # ========================================================
    # SPLINE
    # ========================================================   
    def callback_Nspline(self):
        L = spl.ComputeLengthOfSpline( self.geopath )
        Nspline = int( self.ui.spinBox_Nspline.value() )
        print( 'geolength =', L )
        # --------------------------------
        Rspline = L/Nspline        
        self.ui.spinBox_Rspline.setValue( Rspline )  
        
    def ResetSpline(self):
        self.spline.DeepCopy( self.geopath )
        
        self.UpdateSplineRadii()
        self.UpdateGraphPlotter()            
        self.UpdateTube()
        self.UpdateCenterline()
        self.UpdateTriangularMesh()
        # self.UpdateCuts()
        
        
        # VTK rendering 1
        # -----------------------------------------
        self.ui.qvtk1.GlyphPickedPoint( self.pickedPoint )    
        self.ui.qvtk1.DisplayGeoPath( self.geopath )
        self.ui.qvtk1.DisplaySpline( self.spline ) 
        self.ui.spinBox_Nspline.setValue( self.spline.GetNumberOfPoints() ) 
        
        self.ui.qvtk1.renWin.Render()
    
    def OnClick_UpdateSpline(self):
        
        # Nspline = int( self.ui.spinBox_Nspline.value() )
        # self.spline = spl.ParametricOpenedSpline( self.geopath.GetPoints(), Nspline )
    
        # N1 = int( self.geolength/0.5 ) # R = 1.0 mm
        # spline1 = spl.ParametricOpenedSpline( self.geopath.GetPoints(), N1 )
        
        Nspline = int( self.ui.spinBox_Nspline.value() )
        self.spline = spl.ParametricOpenedSpline( self.geopath.GetPoints(), Nspline )
        
        
        self.UpdateSplineRadii()
        self.UpdateGraphPlotter()
        self.UpdateTube()
        self.UpdateCenterline()
        self.UpdateTriangularMesh()

        # VTK rendering 1
        # -----------------------------------------  
        self.ui.qvtk1.DisplaySpline( self.spline ) 
        self.ui.qvtk1.renWin.Render()        
        
        
        # self.ui.qvtk1.button_SaveSpline.clicked.connect( self.WriteSpline )
   
    
    # CAV ========================================================
    def UpdateSplineRadii(self):

        K = self.spline.GetNumberOfPoints()
        
        # Create radii
        # -----------------------------------------
        radii = vtk.vtkDoubleArray()
        radii.SetNumberOfComponents( 1 )
        radii.SetNumberOfTuples( K )
        radii.SetName( 'Radius' )
        
        # Get Radii from isosurface
        # ------------------------------------------------        
        implicitDistance = vtk.vtkImplicitPolyDataDistance()
        implicitDistance.SetInput( self.isosurface )
        
        for k in range( K ):
            point = self.spline.GetPoint( k )             
            # Points interior to the geometry have a negative distance
            distance = implicitDistance.EvaluateFunction( point )
            if ( distance < 0 ):
                radius = - distance
            else:
                radius = 0.0                
            radii.SetTuple1( k, radius )
            # print( k, radius )
            
        self.spline.GetPointData().AddArray( radii )
        self.spline.GetPointData().SetActiveScalars('Radius')
    # ========================================================
    
    def Get_Laterality(self):
        num_points = self.spline.GetNumberOfPoints()
        if num_points == 0:
            return "Unknown"
        
        # Soma das coordenadas X
        x_coords = [self.spline.GetPoint(i)[0] for i in range(num_points)]
        mean_x = sum(x_coords) / num_points
    
        if mean_x > 0:
            return "L"  # Direita
        else:
            return "R"  # Esquerda
        
    def OnClick_WriteSpline(self):
        side = self.Get_Laterality()
        
        # outputFilename = self.OUTPUTDIR + "%s_%s_%s_spline.vtk" %(self.dataset, self.isovalue, side )
        
        outputFilename = QtWidgets.QFileDialog.getSaveFileName( self, 'Save Spline As...', 
        self.OUTPUTDIR + "%s_%s_%s_spline.vtk" %(self.dataset, self.isovalue, side ), filter=('*.vtk'))[0]
        
        print ( "Writing:", outputFilename )
        
        writer = vtk.vtkPolyDataWriter()
        writer.SetInputData( self.spline )
        writer.SetFileName( outputFilename )
        writer.Write()


    # ========================================================
    # GRAPH PLOTTER
    # ======================================================== 
    def UpdateGraphPlotter(self):        
        
        radii = self.spline.GetPointData().GetArray("Radius")        
        # ------------------------------------------------
        D = []
        R = []

        sum_d = 0.0
        D.append( sum_d )
        R.append( radii.GetValue(0) )

        # Iterate Radii
        # ---------------------------------
        K = self.spline.GetNumberOfPoints()
        for k in range(1, K):
            P0 = self.spline.GetPoint( k - 1 )
            P1 = self.spline.GetPoint( k )
            sum_d += np.sqrt( math.Distance2BetweenPoints(P0, P1) )
            D.append( sum_d )
            R.append( radii.GetValue(k) )

        self.length_tot = sum_d            
        # print('length_tot', length_tot)
        # print('np.max(R)', np.max(R))            
        
        # PLT plot
        # -----------------------------------------       
        # Set axis limits
        self.ui.qplt1.ax1.set_xlim(0, self.length_tot)
        self.ui.qplt1.ax1.set_ylim(0, np.max(R) * 1.5)
        self.ui.qplt1.ax2.set_xlim(0, self.length_tot)
        
        # # Set vlines
        # self.ui.qplt1.vline1.set_x( (1/5)*self.length_tot )
        # self.ui.qplt1.vline2.set_x( (2/5)*self.length_tot )
        # self.ui.qplt1.vline3.set_x( (3/5)*self.length_tot )
        # self.ui.qplt1.vline4.set_x( (4/5)*self.length_tot )
        
        # Update data - colormap JET 
        self.ui.qplt1.SetData( D, R )
        
        # Update the plot with colormap JET
        self.ui.qplt1.UpdatePlot()
        
        # Add the legend for line1
        # self.ui.qplt1.lc.set_label( 'T = %i' % self.isovalue )
       
        # Refresh the canvas
        # self.ui.qplt1.canvas.draw()    
        # self.ui.qplt1.canvas.draw_idle()     
        self.ui.qplt1.canvas.flush_events()
    
                
    def ResetVlinesPlotter( self ):
       self.ui.qplt1.ResetVlinesPlotter()
        
    # ========================================================
    # TUBE
    # ======================================================== 
    def UpdateTube(self):
        
        self.tube = vtk.vtkTubeFilter()
        self.tube.SetInputData( self.spline )
        self.tube.SetNumberOfSides( 500 )
        self.tube.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
        
        self.ui.qvtk1.DisplayTube( self.tube, self.spline )
        
    # ========================================================
    # CENTERLINE
    # ======================================================== 
    def UpdateCenterline( self ):
        # print ('ves > GenerateCenterline')
        
        self.fstangents  = vtk.vtkDoubleArray()
        self.fsnormals   = vtk.vtkDoubleArray()
        self.fsbinormals = vtk.vtkDoubleArray()
        # radii       = vtk.vtkDoubleArray()
        # length_tot  = 0.0
            
        # ---------------------------------
        points = self.spline.GetPoints()
        # ---------------------------------
        K = points.GetNumberOfPoints()
        # ---------------------------------
        self.fstangents = vtk.vtkDoubleArray()
        self.fstangents.SetNumberOfComponents( 3 )
        self.fstangents.SetNumberOfTuples( K )
        self.fstangents.SetName( 'fstangents' )
        # ---------------------------------
        self.fsnormals = vtk.vtkDoubleArray()
        self.fsnormals.SetNumberOfComponents( 3 )
        self.fsnormals.SetNumberOfTuples( K )
        self.fsnormals.SetName( 'fsnormals' )
        # ---------------------------------
        self.fsbinormals = vtk.vtkDoubleArray()
        self.fsbinormals.SetNumberOfComponents( 3 )
        self.fsbinormals.SetNumberOfTuples( K )
        self.fsbinormals.SetName( 'fsbinormals' )
        # ---------------------------------
        normal   = [1,0,0]  # RED
        binormal = [0,1,0]  # GREEN
        tangent  = [0,0,1]  # BLUE        
        # ===========================================
        # tangent of first center
        for k in [0]:
            P0 = points.GetPoint(k)
            P1 = points.GetPoint(k + 1)
            tangent = [0,0,0]      
            math.Subtract(P1, P0, tangent)
            math.Normalize( tangent )
            self.fstangents.SetTuple( k, tangent )
        # tangent of last center
        for k in [K - 1]:
            P0 = points.GetPoint(k - 1)
            P1 = points.GetPoint(k)
            tangent = [0,0,0]      
            math.Subtract(P1, P0, tangent)
            math.Normalize( tangent )
            self.fstangents.SetTuple( k, tangent )
        # ---------------------------------
        for k in range( 1, K - 1 ):
            P1 = points.GetPoint( k - 1 )
            P2 = points.GetPoint( k + 1 )
            tangent = [0,0,0]      
            math.Subtract(P2, P1, tangent)
            math.Normalize( tangent )
            self.fstangents.SetTuple( k, tangent )            
        # ---------------------------------
        # Find perpendiculares and solve problem of correspondence
        # between centers of centerline; 
        # vtkMath.Perpendiculars(...) works for all points...
        # but provides TWISTING of vessel for data 'tof_66.mat'!!              
        for k in range( K ):
            tangent = self.fstangents.GetTuple( k )
            if ( k == 0 ): 
                math.Perpendiculars( tangent, normal, binormal, 0.0 ) # theta = 0.0 ??
                math.Cross( tangent, normal, binormal )
            else:
                math.Cross( tangent, normal, binormal )            
                math.Cross( binormal, tangent, normal )
                math.Normalize( normal )
                math.Normalize( binormal )            
            self.fsnormals.SetTuple(k, normal)
            self.fsbinormals.SetTuple(k, binormal)
        # ---------------------------------
        self.centerline = vtk.vtkPolyData()
        self.centerline.DeepCopy( self.spline )
        
        self.centerline.GetPointData().AddArray( self.fstangents )
        self.centerline.GetPointData().AddArray( self.fsnormals )
        self.centerline.GetPointData().AddArray( self.fsbinormals )

        self.ui.qvtk1.GlyphFrenet(self.centerline, 0.25)
        
    # ========================================================
    # MESH
    # ======================================================== 
    def UpdateTriangularMesh( self ):
        
        centers     = self.centerline.GetPoints()
        radii       = self.centerline.GetPointData().GetArray("Radius")
        # fsnormals   = self.centerline.GetPointData().GetArray("fsnormals")
        # fsbinormals = self.centerline.GetPointData().GetArray("fsbinormals")
        
        K = centers.GetNumberOfPoints()
        
        # if radii is None or radii.GetNumberOfTuples() != K:
            # raise ValueError("Centerline must have a point array named 'Radius'.")
            
        N = 20
        dtheta = (2.0*pi)/float( N )
            
        # Step 1: Generate mesh points
        
        # ---------------------------------     
        mesh_points = vtk.vtkPoints()
        # ---------------------------------
        for k in range( K ):

            P  = centers.GetPoint( k )
            v2 = self.fsnormals.GetTuple( k )
            v3 = self.fsbinormals.GetTuple( k )
            radius = radii.GetValue( k )
            
            # Circle points Q per centerline position
            Q = [0,0,0]
            for n in range( N ):
                theta = float(n)*dtheta
                w2 = np.cos( theta )
                w3 = np.sin( theta )
                for i in range(0,3):
                    Q[i] = P[i] + radius*( w2*v2[i] + w3*v3[i] )
                mesh_points.InsertNextPoint( Q )

     
        # Step 2: Generate mesh triangle faces
        # --------------------------------- 
        triangles  = vtk.vtkCellArray()
        # ---------------------------------
        for k in range( K - 1 ):    
            for n in range( N ): 
                
                triangles.InsertNextCell( 3 )
                triangles.InsertCellPoint( k*N + n )
                triangles.InsertCellPoint( k*N + np.mod(n + 1, N) )
                triangles.InsertCellPoint( (k + 1)*N + n )
                # cellData.InsertNextTuple( rgb )
                
                triangles.InsertNextCell( 3 )
                triangles.InsertCellPoint( k*N + np.mod(n + 1, N) )
                triangles.InsertCellPoint( (k + 1)*N + n )
                triangles.InsertCellPoint( (k + 1)*N + np.mod(n + 1, N) )
                # cellData.InsertNextTuple( rgb )

        
        cellData  = vtk.vtkUnsignedCharArray()
        cellData.SetNumberOfComponents( 3 )
        cellData.SetName('cellColor')
        
        cellData.InsertTuple(        0, [0,0,0] )   # black
        # cellData.InsertTuple( int(N/2), [255,0,0] ) # red

        
        num_cells = triangles.GetNumberOfCells()
        rgb = [0,0,0]
        rgb[0] = np.random.randint(0,255)
        rgb[1] = np.random.randint(0,255)
        rgb[2] = np.random.randint(0,255)    
        
        rgb=[255,0,0]
        for c in range( 1, num_cells ):
            # cellData.InsertTuple( c, color )
            
            # rgb = [0,0,0]
            # rgb[0] = np.random.randint(0,255)
            # rgb[1] = np.random.randint(0,255)
            # rgb[2] = np.random.randint(0,255)
            cellData.InsertTuple( c, rgb )
            
        
        # Step 3: Assemble into PolyData
        self.mesh = vtk.vtkPolyData()
        self.mesh.SetPoints( mesh_points )
        self.mesh.SetPolys( triangles )
        self.mesh.GetCellData().AddArray( cellData )
        self.mesh.GetCellData().SetScalars( cellData )


        self.ui.qvtk1.DisplayMesh(self.mesh, 1, 1)
    
    # def UpdateCuts(self):
    #     K = self.centerline.GetNumberOfPoints()
        
    #     centers = self.centerline.GetPoints()
    #     # fstangents  = self.centerline.GetPointData().GetArray("fstangents")
        
    #     for k in range( K ):
    #         P  = centers.GetPoint( k )
    #         versor = self.fstangents.GetTuple( k )
            
    #         plane = vtk.vtkPlane()
    #         plane.SetOrigin( P )
    #         plane.SetNormal( versor )
            
    #         # create cutter
    #         cutter = vtk.vtkCutter()    
    #         cutter.SetInputData( self.outline )
    #         cutter.SetCutFunction( plane )
    #         cutter.Update()   
        
    #         # Extract Region Closest to Point P
    #         connectivity = vtk.vtkPolyDataConnectivityFilter()
    #         connectivity.SetInputData( cutter.GetOutput() )
    #         connectivity.SetExtractionModeToClosestPointRegion()
    #         connectivity.SetClosestPoint ( P )
    #         connectivity.Update()
            
    #         self.closest = vtk.vtkPolyData()
    #         self.closest = connectivity.GetOutput() 
        
            
    #         self.ui.qvtk1.DisplayCuts(self.closest)
        
  
    # ========================================================
     
    def Help_About(self): # QMessageBox.information
        # -----------------------------------------
        message = self.APP_NAME + ' - ' + str( self.APP_VERSION ) + '\n'
        message += '\n'
        # message += "Release: " + str( self.APP_RELEASE ) + "\n"
        # message += "Expires: " + str( self.APP_EXPIRED ) + "\n"
        # message += '\n'
        message += 'Carlos Vinhais @ 2025'
        # -----------------------------------------        
        QMessageBox.information( QtWidgets.QWidget(), 'About', message )
        
        self.ui.statusBar.showMessage('About.') 
    
        # QMessageBox.about(self, "About Stenosis APP",
        #                   "<p>The <b>Image Viewer</b> example shows how to combine "
        #                   "QLabel and QScrollArea to display an image. QLabel is "
        #                   "typically used for displaying text, but it can also display "
        #                   "an image. QScrollArea provides a scrolling view around "
        #                   "another widget. If the child widget exceeds the size of the "
        #                   "frame, QScrollArea automatically provides scroll bars.</p>"
        #                   "<p>The example demonstrates how QLabel's ability to scale "
        #                   "its contents (QLabel.scaledContents), and QScrollArea's "
        #                   "ability to automatically resize its contents "
        #                   "(QScrollArea.widgetResizable), can be used to implement "
        #                   "zooming and scaling features.</p>"
        #                   "<p>In addition the example shows how to use QPainter to "
        #                   "print an image.</p>")
        
    
    def File_Quit(self):  # QMessageBox.question    
        self.ui.statusBar.showMessage('File_Quit() ... ')
        # -----------------------------------------    
        ret = QMessageBox.question(self, self.APP_NAME, 
              "Do you really want to quit?", 
              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            
            # rever este codigo !!
            QApplication.quit()
            self.hide()
            # sys.exit();
            
        else: 
            pass
        # -----------------------------------------
        self.ui.statusBar.showMessage('Ready.')
      
# ========================================================

if __name__ == "__main__":
    
    app = QApplication( sys.argv )
    
    myapp = InterfaceApp()
    # myapp.myapp.Help_About()
    
    myapp.show()
    # myapp.showMaximized()
   
    # -----------------------------------------    
    sys.exit( app.exec_() )