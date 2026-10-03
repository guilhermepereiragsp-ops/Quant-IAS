"""
Module: GUI.py
@author: Carlos Vinhais and Guilherme Pereira
cvinhais@gmail.com
"""

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import ( QWidget, QApplication, QMenu, QAction, QProgressBar,
                              QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QStyle,
                              QLabel, QLineEdit, QSpinBox, QPushButton, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup,
                              QListView, QSizePolicy
                             )
import Interface_SceneViewer as SceneViewer
# import Interface_GraphPlotter as GraphPlotter
import Stenosis_GraphPlotter as GraphPlotter

""" A class for Interface GUI """

class Ui_MainWindow( QWidget ):
    
    def setupUi(self, MainWindow):
        

        QApplication.setStyle( 'Fusion' )
        
        # Main Window
        # -----------------------------------------
        MainWindow.setObjectName( 'MainWindow' )
        MainWindow.setWindowTitle( 'Stenosis' )
        MainWindow.setWindowIcon( QtGui.QIcon('pythonlogo.png') )
        
        self.centralWidget = QtWidgets.QWidget( MainWindow )
        
        # Group Widgets
        # -----------------------------------------
        self.InputDataGroup( 'Input Data' )
        self.IsoSurfaceGroup( 'Isosurface' )
        self.ROIGroup( 'ROI' )
        self.LandmarksGroup( 'Landmarks' )
        self.SplineGroup( 'Spline' )
        # self.ResultsGroup( 'Results' )
        
        
        self.IsoSurfaceGroup.setEnabled(False)
        self.ROIGroup.setEnabled(False)
        self.LandmarksGroup.setEnabled(False)
        self.SplineGroup.setEnabled(False)
        

                
        # VTK Viewer
        # -----------------------------------------
        self.qvtk1 = SceneViewer.SceneViewer()
       
        # PLT Plotter
        # -----------------------------------------
        self.qplt1 = GraphPlotter.GraphPlotter( )
        # self.qplt1 = GraphPlotter.DraggableVLine( )
        
        # TAB Widget
        # -----------------------------------------
        # self.tabwidget = TableWidget.TableWidget( )
        
        # Layouts
        # -------------------------------------
        layout1 = QVBoxLayout()
        layout1.setAlignment( QtCore.Qt.AlignTop )
        layout1.addWidget( self.InputDataGroup )
        layout1.addWidget( self.IsoSurfaceGroup )
        layout1.addWidget( self.ROIGroup )
        layout1.addWidget( self.LandmarksGroup )
        layout1.addWidget( self.SplineGroup )
        
       
        layout2 = QVBoxLayout()
        layout2.addWidget( self.qvtk1 )
        layout2.setContentsMargins( 0, 0, 0, 0 )
    
        layout3 = QVBoxLayout()
        layout3.addWidget( self.qplt1 )
        layout3.setContentsMargins( 0, 0, 0, 0 )
        
        layout = QHBoxLayout()        
        layout.addLayout( layout1, 2 )
        layout.addLayout( layout2, 5 )        
        layout.addLayout( layout3, 5 )
    
        # Frame
        # ------------------------------------- 
        frame = QFrame()
        frame.setFrameShape( QFrame.StyledPanel )
        frame.setLayout( layout )
        
        MainWindow.setCentralWidget( frame )
        
        # Menu Bar
        # -----------------------------------------
        # Add menu items
        self.FileMenu = QMenu("&File")
        self.HelpMenu = QMenu("&Help")
        
        self.menuBar = MainWindow.menuBar()
        self.menuBar.addMenu( self.FileMenu )
        self.menuBar.addMenu( self.HelpMenu )
        
        # Create actions
        # self.FileNewAction    = self.FileMenu.addAction('&New...')
        #self.FileOpenAction   = self.FileMenu.addAction('&Open Main Image ...')
        # self.FileExportAction = self.FileMenu.addAction('E&xport...')
        self.FileQuitAction   = self.FileMenu.addAction('&Quit')        
        self.HelpAboutAction  = self.HelpMenu.addAction('About Stenosis APP')
        
        # self.FileNewAction.setShortcut('Ctrl+N')
        #self.FileOpenAction.setShortcut('Ctrl+O')
        # self.FileExportAction.setShortcut('Ctrl+X')
        self.FileQuitAction.setShortcut('Ctrl+Q')        
        self.HelpAboutAction.setShortcut('Ctrl+A')
                
        # # Tool Bar
        # # -------------------------------------
        # icons = [
        #     'SP_DialogOpenButton',
        #     'SP_DialogApplyButton',
        #     'SP_DialogCancelButton',
        #     'SP_DialogResetButton',
        #     'SP_DialogDiscardButton',            
        #     'SP_DialogSaveButton',
        #     'SP_DialogCloseButton',
        #     'SP_DialogHelpButton',            
        #     'SP_CustomBase',
        #     'SP_ArrowBack',
        #     'SP_ArrowDown']
        # self.toolbar = MainWindow.addToolBar( '' )
        # for i in icons:        
        #     img = MainWindow.style().standardIcon(getattr(QStyle, i))
        #     action = QAction( img, i, MainWindow)
        #     action.setEnabled( 1 )
        #     self.toolbar.addAction( action ) 
    
        # # self.toolbar = MainWindow.addToolBar( '' )
        # # icon = 'SP_DialogOpenButton'
        # # img = MainWindow.style().standardIcon(getattr(QStyle, icon))
        # # self.action = QAction( img, icon, MainWindow)
        # # self.toolbar.addAction( self.action )
        # # self.action.triggered.connect( ... )
        
        # Progress Bar
        # -------------------------------------        
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum( 100 )
        
        # Status Bar
        # -------------------------------------
        self.statusBar = MainWindow.statusBar()
        self.statusBar.showMessage('Ready.') 
        self.statusBar.addPermanentWidget( self.progressBar )
    
    # ======================================================== 
    
    def InputDataGroup(self, title):
    
         # Widgets
         spinBoxLabel = QLabel('Case Idx')
         self.spinBox_Dataset = QSpinBox()
         self.spinBox_Dataset.setSingleStep( 1 )
         self.spinBox_Dataset.setRange(0, 16)
         self.spinBox_Dataset.setValue( 0 )  
         self.spinBox_Dataset.setEnabled( 1 )        
         
         lineEditLabel = QLabel( 'Dataset' )
         self.lineEdit_Dataset = QLineEdit( 'Sten0001' )
         self.lineEdit_Dataset.setEnabled( 0 )
         
         self.button_LoadDataset = QPushButton( '   Load' )
         img1 = self.centralWidget.style().standardIcon(getattr(QStyle,'SP_DialogOpenButton'))
         self.button_LoadDataset.setIcon( img1 )
         self.button_LoadDataset.setEnabled( 1 )
         
        # Layout
         layout = QGridLayout()
         layout.addWidget( spinBoxLabel,            0, 0 )
         layout.addWidget( self.spinBox_Dataset,    0, 1 )
         layout.addWidget( lineEditLabel,           1, 0 )
         layout.addWidget( self.lineEdit_Dataset,   1, 1 )
         layout.addWidget( self.button_LoadDataset, 2, 0, 1, 2 )
         layout.setColumnStretch(0, 1)
         layout.setColumnStretch(1, 1)
         
         # Group
         self.InputDataGroup = QGroupBox( title )
         self.InputDataGroup.setStyleSheet( 'QGroupBox { font-weight: bold; } ') 
         self.InputDataGroup.setLayout( layout )
         
     # -------------------------------------
     
    def IsoSurfaceGroup(self, title):
    
        # Widgets
        self.spinBox_Isovalue = QSpinBox()
        self.spinBox_Isovalue.setSingleStep( 1 )
        self.spinBox_Isovalue.setRange(1, 1024)
        self.spinBox_Isovalue.setValue( 180 )  
        self.spinBox_Isovalue.setEnabled( 1 )
        
        self.checkBox = QCheckBox("Apply Smoothing")
        self.checkBox.setChecked( False )
        
        self.spinBox_Smooth = QDoubleSpinBox()
        self.spinBox_Smooth.setSingleStep( 0.01 )
        self.spinBox_Smooth.setRange(0, 1)
        self.spinBox_Smooth.setValue( 0 )  
        self.spinBox_Smooth.setEnabled( 0 )
        
        self.spinBox_Iters = QSpinBox()
        self.spinBox_Iters.setSingleStep( 1 )
        # self.spinBox_Iters.setRange(0, 1)
        self.spinBox_Iters.setValue( 0 )  
        self.spinBox_Iters.setEnabled( 0 )
        
        self.button_ContourImage = QPushButton( '   Apply' )
        img1 = self.centralWidget.style().standardIcon(getattr(QStyle,'SP_DialogApplyButton'))
        self.button_ContourImage.setIcon( img1 )
        self.button_ContourImage.setEnabled( 1 )
        
        
        # Layout
        layout = QGridLayout()
        layout.addWidget( QLabel('Isovalue'),       0, 0 )
        layout.addWidget( self.spinBox_Isovalue,    0, 1 )
        layout.addWidget( self.checkBox,            1, 0 )
        layout.addWidget( QLabel('Smooth Factor'),  2, 0 )
        layout.addWidget( self.spinBox_Smooth,      2, 1 )
        layout.addWidget( QLabel('N iters'),        3, 0 )
        layout.addWidget( self.spinBox_Iters,       3, 1 )
        layout.addWidget( self.button_ContourImage, 4, 0, 1, 2 )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        
        # Group
        self.IsoSurfaceGroup = QGroupBox( title )
        self.IsoSurfaceGroup.setStyleSheet( 'QGroupBox { font-weight: bold; } ') 
        self.IsoSurfaceGroup.setLayout( layout )
        
        self.checkBox.clicked.connect( self.SetSceneVisibility )
        
    # ------------------------------------- 
    
    def ROIGroup(self, title):
    
        # Widgets
        self.spinBox_X = QSpinBox()
        self.spinBox_X.setSingleStep( 1 )
        self.spinBox_X.setRange(1, 1024) #limite x da imagem
        self.spinBox_X.setValue( 50 )  
        self.spinBox_X.setEnabled( 1 )
        
        self.spinBox_Y = QSpinBox()
        self.spinBox_Y.setSingleStep( 1 )
        self.spinBox_Y.setRange(1, 1024) #limite y da imagem
        self.spinBox_Y.setValue( 50 )  
        self.spinBox_Y.setEnabled( 1 )
        
        self.spinBox_Z = QSpinBox()
        self.spinBox_Z.setSingleStep( 1 )
        self.spinBox_Z.setRange(1, 1024) #limite z da imagem
        self.spinBox_Z.setValue( 50 )  
        self.spinBox_Z.setEnabled( 1 )
        
        self.button_GenerateSkeleton = QPushButton( '   Generate Skeleton' )
        img1 = self.centralWidget.style().standardIcon(getattr(QStyle,'SP_DialogApplyButton'))
        self.button_GenerateSkeleton.setIcon( img1 )
        self.button_GenerateSkeleton.setEnabled( 1 )
        
        
        # Layout
        layout = QGridLayout()
        layout.addWidget( QLabel('Dx (pixels)'),       0, 0 )
        layout.addWidget( self.spinBox_X,    0, 1 )
        layout.addWidget( QLabel('Dy (pixels)'),         1, 0 )
        layout.addWidget( self.spinBox_Y,      1, 1 )
        layout.addWidget( QLabel('Dz (pixels)'),        2, 0 )
        layout.addWidget( self.spinBox_Z,       2, 1 )
        layout.addWidget( self.button_GenerateSkeleton, 3, 0, 1, 2 )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        
        # Group
        self.ROIGroup = QGroupBox( title )
        self.ROIGroup.setStyleSheet( 'QGroupBox { font-weight: bold; } ') 
        self.ROIGroup.setLayout( layout )
        
    
    # -------------------------------------
    
    def LandmarksGroup(self, title):
        
        # Widgets
        self.radio_L0 = QtWidgets.QRadioButton("Start")
        self.radio_L1 = QtWidgets.QRadioButton("End")
        self.radio_L0.setChecked( True )
        self.radio_L1.setChecked( False )
        # self.radioGroup = QButtonGroup()
        # self.radioGroup.addButton(self.radio_L0)
        # self.radioGroup.addButton(self.radio_L1)
    
        
        # Layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget( self.radio_L0, 1, 0)
        layout.addWidget( self.radio_L1, 1, 1)   

        # Group
        self.LandmarksGroup = QtWidgets.QGroupBox( title )
        self.LandmarksGroup.setStyleSheet("QGroupBox { font-weight: bold; } ")
        self.LandmarksGroup.setLayout( layout )
        
    def SplineGroup(self, title):
        
        # Widgets
        self.spinBox_Nspline = QSpinBox()
        self.spinBox_Nspline.setRange( 5, 1000 )
        self.spinBox_Nspline.setSingleStep( 1 )
        self.spinBox_Nspline.setValue( 50 )  
        self.spinBox_Nspline.setEnabled( 1 ) 
        
        # RESOL - Snake resolution (mm/point)
        self.spinBox_Rspline = QDoubleSpinBox()
        self.spinBox_Rspline.setDecimals( 2 )
        self.spinBox_Rspline.setRange(0.0, 5.0)
        self.spinBox_Rspline.setSingleStep( 0.05 )
        self.spinBox_Rspline.setEnabled( 0 )
        
        self.spinBox_Lspline = QDoubleSpinBox()
        self.spinBox_Lspline.setDecimals( 2 )
        # self.spinBox_Lspline.setRange(0.0, 5.0)
        # self.spinBox_Lspline.setSingleStep( 0.05 )
        self.spinBox_Lspline.setEnabled( 0 )
        
        self.button_UpdateSpline = QtWidgets.QPushButton( "   Update" ) 
        self.button_SaveSpline = QtWidgets.QPushButton( "   Save VTK Spline" )
        self.button_ResetSpline = QtWidgets.QPushButton( "   Reset Spline" )
        
        icon1 = 'SP_DialogApplyButton'
        icon2 = 'SP_DialogResetButton'
        icon3 = 'SP_DialogSaveButton'
        img1 = self.centralWidget.style().standardIcon(getattr(QtWidgets.QStyle, icon1))
        img2 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon2))
        img3 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon3))
        self.button_UpdateSpline.setIcon( img1 )
        self.button_SaveSpline.setIcon( img3 )
        self.button_ResetSpline.setIcon( img2 )
        
        # Layout
        layout = QtWidgets.QGridLayout()
        layout.addWidget( QLabel('N spline'),    1, 0)
        layout.addWidget( self.spinBox_Nspline,  1, 1)        
        layout.addWidget( QLabel('R (mm/point)'),  2, 0)
        layout.addWidget( self.spinBox_Rspline,    2, 1 )
        layout.addWidget( QLabel('L (mm)'),        3, 0)
        layout.addWidget( self.spinBox_Lspline,    3, 1 )
        
        layout.addWidget(self.button_UpdateSpline,  4, 0, 1, 2)
        layout.addWidget(self.button_ResetSpline,  5, 0, 1, 2)
        layout.addWidget(self.button_SaveSpline,  6, 0, 1, 2)
        
        
               
        # Group
        self.SplineGroup = QtWidgets.QGroupBox( title )
        self.SplineGroup.setStyleSheet("QGroupBox { font-weight: bold; } ")
        self.SplineGroup.setLayout( layout )
        

    # -------------------------------------
    
    def SetSceneVisibility(self):
        
        self.spinBox_Smooth.setEnabled( self.checkBox.isChecked() )
        self.spinBox_Iters.setEnabled( self.checkBox.isChecked() )   
        