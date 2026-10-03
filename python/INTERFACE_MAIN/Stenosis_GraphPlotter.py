"""
Module: GraphPlotter.py
@author: Carlos Vinhais and Guilherme Pereira
cvinhais@gmail.com
"""
# see also:
# https://www.learnpyqt.com/courses/graphics-plotting/plotting-matplotlib/
import sys
import vtk
import numpy as np
import csv

from PyQt5 import QtGui, QtCore, QtWidgets # 
from PyQt5.QtWidgets import (QApplication, QWidget, 
                             QLabel, QPushButton, 
                             QLineEdit, QSizePolicy, QCheckBox, 
                             QGridLayout, QGroupBox, QFileDialog, QMessageBox)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D


math = vtk.vtkMath()



""" A class for Graph Plotter """
class DraggableVLine:
    
    def __init__(self, ax, x, color, label, on_update_callback):
        
        self.ax = ax
        self.label = label
        self.x = x
        self.on_update_callback = on_update_callback

        self.line = ax.axvline(x, color=color, lw=1.5, picker=5)
        self.press = False

        fig = self.line.figure
        fig.canvas.mpl_connect('button_press_event', self.on_press)
        fig.canvas.mpl_connect('button_release_event', self.on_release)
        fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        contains, _ = self.line.contains(event)
        if contains:
            self.press = True

    def on_release(self, event):
        if self.press and event.xdata is not None:
            self.x = event.xdata
        self.press = False
        self.on_update_callback()

    def on_motion(self, event):
        if self.press and event.inaxes == self.ax and event.xdata is not None:
            self.x = event.xdata
            self.line.set_xdata([self.x, self.x])
            self.line.figure.canvas.draw()
            self.on_update_callback()

    def set_x(self, x):
        self.x = x
        self.line.set_xdata([x, x])
        self.line.figure.canvas.draw()
        self.on_update_callback()
        
    def get_x(self):
        return self.x
    

class GraphPlotter( QtWidgets.QWidget ):
    
    def __init__(self, parent=None):

        # Widget
        super(GraphPlotter, self).__init__()
        # QtWidgets.QGroupBox.__init__(self, parent)

        QApplication.setStyle('Fusion')
        
        # Main Window
        # -------------------------------------
        self.setObjectName("GraphPlotter")
        self.setWindowTitle("Graph Plotter")
        self.setWindowIcon( QtGui.QIcon('icon.png') )
        # self.resize( 1024, 1024 )
        
        
        # Setup PLT environment
        # -------------------------------------        
        self.fig    = Figure( figsize=(6, 6), dpi=100 )
        self.canvas = FigureCanvasQTAgg(self.fig)
        # self.canvas.setFixedWidth( 512 )
        # self.canvas.setFixedHeight( 512 )
        
        # self.canvas.setMinimumSize(600, 400)  # ou o tamanho que desejar
        # self.canvas.setMaximumSize(800, 600)  # para evitar crescimento exagerado
        # self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


        self.canvas.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # NavigationToolbar(self.canvas, self.canvas )

        # Create PLT Axes
        self.CreateAxes()

        # Create fake data
        # -------------------------------------        
        self.x_data  = np.linspace(0, 1, 100)
        self.y_data = np.ones( len(self.x_data) )
   
        self.ax1.set_xlim( 0, 1 )
        self.ax1.set_ylim( 0, 1 )
 
        self.ax2.set_xlim( 0, 1 )
        self.ax2.set_ylim( 0, 100 )
        
        # ax1
        # -------------------------------------          
        # Prepare empty LineCollection for colored line
        empty_segments = np.empty((0, 2, 2))
        self.lc = LineCollection( empty_segments, cmap='jet_r', linewidth=3, alpha=0.9, label='JET' )
        self.ax1.add_collection( self.lc )

        # Draggable vertical lines
        self.vline1 = DraggableVLine( self.ax1, x=0.00, color='gray', label='Line 1', on_update_callback=self.UpdatePlot )
        self.vline2 = DraggableVLine( self.ax1, x=0.33, color='gray', label='Line 2', on_update_callback=self.UpdatePlot )
        self.vline3 = DraggableVLine( self.ax1, x=0.66, color='gray', label='Line 3', on_update_callback=self.UpdatePlot )
        self.vline4 = DraggableVLine( self.ax1, x=1.00, color='gray', label='Line 4', on_update_callback=self.UpdatePlot )

        # Highlight span between vertical lines
        # self.highlight_span_I  = self.ax1.axvspan(0, 0, color='lightgray', alpha=0.3, zorder=0)
        # self.highlight_span_II = self.ax1.axvspan(0, 0, color='lightgray', alpha=0.3, zorder=0)
        
        # Trend line
        self.meanI      = self.ax1.scatter([], [], color='purple', s=30, zorder=5 )
        self.meanII     = self.ax1.scatter([], [], color='purple', s=30, zorder=5 )
        self.trendline, = self.ax1.plot([], [], color='purple', linestyle='--', label='Base line' )
  
        # ax2
        # -------------------------------------  
        self.line50 = self.ax2.axhline( 50, color='red', lw=1, linestyle='--' ) # , label='50%')
        self.line75 = self.ax2.axhline( 70, color='red', lw=1, linestyle='--' ) # , label='75%')
      
        self.line1, = self.ax2.plot([], [], color='black', linestyle='--',  label='Radius' )
        self.line2, = self.ax2.plot([], [], color='black', linestyle='-', label='Area' )
        # self.line3, = self.ax2.plot([], [], color='black', linestyle=':', label='Diameter' )

        self.maxima = self.ax2.scatter([], [], color='blue', zorder=5) # s=100, 
        
        self.fill50 = self.ax2.fill_between(self.x_data, self.y_data, 0.5, where=(self.y_data > 0.50), 
                 interpolate=True, color='orange', alpha=0.50, label='> 50%')
        
        self.fill70 = self.ax2.fill_between(self.x_data, self.y_data, 0.5, where=(self.y_data > 0.70), 
                 interpolate=True, color='orange', alpha=0.95, label='> 70%')
        
        self.ax2.legend( loc='upper right' ) 

        # -------------------------------------  
        # Q Controls
        # -------------------------------------  
        self.CreateControlGroup( "Graph Actions" ) 
        self._CreateGroupI( "Window I" ) 
        self._CreateGroupII( "Window II" ) 
        self._CreateGroupIII( "Stenosis" ) 
        self.ResultsGroup( 'Results' )

        # Layout
        layout = QGridLayout()        
        layout.addWidget( self.canvas,         0, 0, 1, 4 )
        layout.addWidget( self.groupI,         1, 0, 1, 1 )
        layout.addWidget( self.groupII,        1, 1, 1, 1 )        
        layout.addWidget( self.groupIII,       1, 2, 1, 1 )
        layout.addWidget( self.controlGroup,   1, 3, 1, 1 )
        layout.addWidget( self.ResultsGroup,   2, 0, 1, 4 )
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.setAlignment( QtCore.Qt.AlignTop )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)      
        layout.setColumnStretch(3, 1)
        layout.setAlignment( QtCore.Qt.AlignTop )
        self.setLayout( layout )
        
        
    
    
    def CreateAxes(self):
        self.fig.subplots_adjust( hspace = 0.25, top=0.95 )
        # ----------------------------------- 
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        # -----------------------------------         
        # self.ax1.set_title( "Title: --", fontsize=14 )
        self.ax1.set_xlabel('Arc Length, s (mm)', fontsize=12 )
        self.ax1.set_ylabel('Radius, r (mm)', fontsize=12 )
        self.ax1.grid()
        # ----------------------------------- 
        self.ax2.set_xlabel('Arc Length, s (mm)', fontsize=12 )
        self.ax2.set_ylabel('Stenosis, (%)', fontsize=12 )
        self.ax2.grid()
    
    def SetData(self, x, y):
        
        # Set data
        self.x_data = np.asarray( x )
        self.y_data = np.asarray( y )
 
        # Create segments from x, y
        points = np.array([self.x_data, self.y_data]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
        # Update LineCollection segments and colors
        self.lc.set_segments( segments )
        self.lc.set_array( self.y_data )
        self.lc.set_clim(  self.y_data.min(), self.y_data.max() )

    def update_fill(self, ax, fill, x_new, y_new, threshold ):
        # Remove the old fill
        if fill:
            fill.remove()    
        # Create new fill and return it
        return ax.fill_between(x_new, y_new, threshold, where=(y_new > threshold),
                               interpolate=True, color='orange', alpha=0.4)

 
    
    def UpdatePlot(self):
        
        xlim_min, xlim_max = self.ax1.get_xlim()
        
        x1 = self.vline1.get_x()
        x2 = self.vline2.get_x()        
        x3 = self.vline3.get_x()
        x4 = self.vline4.get_x()

        left_I, right_I, left_II, right_II = sorted([x1, x2, x3, x4])
        
        amplitude_I  = right_I  - left_I
        amplitude_II = right_II - left_II
        
        # print( left_I, right_I, left_II, right_II)  
        
        # Update shaded region I between vertical lines
        # self.highlight_span_I.set_xy([
        #     [left_I, self.ax1.get_ylim()[0]], 
        #     [left_I, self.ax1.get_ylim()[1]],
        #     [right_I, self.ax1.get_ylim()[1]],
        #     [right_I, self.ax1.get_ylim()[0]],
        # ])

        # # Update shaded region II between vertical lines
        # self.highlight_span_II.set_xy([
        #     [left_II, self.ax1.get_ylim()[0]],
        #     [left_II, self.ax1.get_ylim()[1]],
        #     [right_II, self.ax1.get_ylim()[1]],
        #     [right_II, self.ax1.get_ylim()[0]],
        # ])
        
        # # UI update
        # # -------------------------------------            
        self.x1_lineEdit.setText(f"{left_I:.2f}")
        self.x2_lineEdit.setText(f"{right_I:.2f}")
        self.spanI_lineEdit.setText(f"{amplitude_I:.2f}")

        self.x3_lineEdit.setText(f"{left_II:.2f}")
        self.x4_lineEdit.setText(f"{right_II:.2f}")
        self.spanII_lineEdit.setText(f"{amplitude_II:.2f}")
        
        # Masks
        mask_I  = ( self.x_data >= left_I)  & (self.x_data <= right_I  )
        mask_II = ( self.x_data >= left_II) & (self.x_data <= right_II )
       
        x_slice_I  = self.x_data[mask_I]
        y_slice_I  = self.y_data[mask_I]        
        x_slice_II = self.x_data[mask_II]
        y_slice_II = self.y_data[mask_II]

        if len(x_slice_I) == 0 or len(x_slice_II) == 0:
        
            print("One of the intervals is empty. Cannot compute trend line.")
            
            #     stenosis1 = 0 * self.y_data
            #     stenosis2 = 0 * self.y_data            
            #     x_maxs = []
            #     y_maxs = []
            
            # # UI update
            # # -------------------------------------  
            # self.RrefI_lineEdit.setText("--")
            # self.RrefII_lineEdit.setText("--")
            # self.steno_loc_mm_lineEdit.setText("--")
            # self.steno_loc_rel_lineEdit.setText("--")
            # self.steno_width_mm_lineEdit.setText("--")
            # self.steno_radius_lineEdit.setText("--")
            # self.steno_degree_R_lineEdit.setText("--")
            # self.steno_degree_A_lineEdit.setText("--")
            
        else:
            
            # Compute Mean x and y values for both intervals
            x_mean_I = x_slice_I.mean()
            y_mean_I = y_slice_I.mean()        
            x_mean_II = x_slice_II.mean()
            y_mean_II = y_slice_II.mean()  
        
            # print( x_mean_I, x_mean_II )
           
            # Compute slope and intercept, based on Mean x and y values
            slope = (y_mean_II - y_mean_I) / (x_mean_II - x_mean_I)
            intercept = y_mean_I - slope * x_mean_I

            # Compute Base line with slope and intercept
            y_trend = slope*self.x_data + intercept

            # Linear fit (trend line) outside interval
            # p = np.polyfit( outside_x, outside_y, 1)
            # p = np.polyfit( [[xI, yI]], [[xII, yII]], 1)
            # m, b = p
            # y_trend = m*self.x_data + b

            ####################   STENOSIS    ########################
               
            
            
            
            # Compute degrees of stenosis
            stenosis1 = np.maximum( 0, 100*(1 - (self.y_data/y_trend)   ) )
            
            # testar:
            # stenosis1 = np.minimum( 100,  np.maximum( 0, 100*(1 - (self.y_data/(y_trend+0.00000001)   ) )))
            
            
            stenosis2 = np.maximum( 0, 100*(1 - (self.y_data/y_trend)**2) )
             
            # Find indices where stenosis is maximal
            max_val = np.max( stenosis1 )
            max_idx = np.where( stenosis1 == max_val )[0][0] # first max index        
            
            x_max   = self.x_data[max_idx]
            y_max   = self.y_data[max_idx]
            y_max_R = stenosis1[max_idx]
            y_max_A = stenosis2[max_idx]           
            # print(max_val, max_idx, x_max )
            
            # Stenosis features
            steno_loc_mm   = x_max
            steno_loc_rel  = 100*((steno_loc_mm - xlim_min)/(xlim_max - xlim_min)) 
            steno_width_mm = left_II - right_I
            steno_radius   = y_max
            steno_degree_R = y_max_R
            steno_degree_A = y_max_A
            

            ############################################################

            # Update plot 1
            # -------------------------------------  
            self.meanI.set_offsets( np.column_stack((x_mean_I, y_mean_I)) )
            self.meanII.set_offsets( np.column_stack((x_mean_II, y_mean_II)) )
            self.trendline.set_data( self.x_data, y_trend )
            
            # Update plot 2
            # -------------------------------------                 
            self.line1.set_data( self.x_data, stenosis1 )
            self.line2.set_data( self.x_data, stenosis2 )
            # self.line3.set_data( self.x_data, stenosis1*2 )
            self.maxima.set_offsets( np.column_stack((x_max, y_max_A)) )           
            self.fill50 = self.update_fill( self.ax2, self.fill50, self.x_data, stenosis2, 50 )
            self.fill70 = self.update_fill( self.ax2, self.fill70, self.x_data, stenosis2, 70 )
            
            # UI update
            # -------------------------------------            
            self.RrefI_lineEdit.setText(f"{y_mean_I:.2f}")
            self.RrefII_lineEdit.setText(f"{y_mean_II:.2f}")
            self.steno_loc_mm_lineEdit.setText(f"{steno_loc_mm:.2f}")
            self.steno_loc_rel_lineEdit.setText(f"{steno_loc_rel:.1f}")
            self.steno_width_mm_lineEdit.setText(f"{steno_width_mm:.2f}")
            self.steno_radius_lineEdit.setText(f"{steno_radius:.2f}")
            self.steno_degree_R_lineEdit.setText(f"{steno_degree_R:.1f}")
            self.steno_degree_A_lineEdit.setText(f"{steno_degree_A:.1f}")
            
        self.canvas.draw()

    # ===========================================================
    # Q Control Groups
    # ===========================================================  
    def _CreateGroupI(self, title ):

        # Widgets
        self.x1_lineEdit = QLineEdit( '' )
        self.x1_lineEdit.setReadOnly(True)
 
        self.x2_lineEdit = QLineEdit( '' )
        self.x2_lineEdit.setReadOnly(True)
        
        self.spanI_lineEdit = QLineEdit( '' )
        self.spanI_lineEdit.setReadOnly(True)
        
        self.RrefI_lineEdit = QLineEdit( '' )
        self.RrefI_lineEdit.setReadOnly(True)
        
        # Layout
        layout = QtWidgets.QGridLayout()        
        layout.addWidget( QLabel( 'x1 (mm)' ),          0, 0 )
        layout.addWidget( self.x1_lineEdit,             0, 1 )
        layout.addWidget( QLabel( 'x2 (mm)' ),          1, 0 )
        layout.addWidget( self.x2_lineEdit,             1, 1 ) 
        layout.addWidget( QLabel( 'Span I (mm)' ),      2, 0 )
        layout.addWidget( self.spanI_lineEdit,          2, 1 ) 
        layout.addWidget( QLabel( 'R mean (mm)' ),      3, 0 )
        layout.addWidget( self.RrefI_lineEdit,          3, 1 )              
        layout.setAlignment( QtCore.Qt.AlignTop )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)        
        
        # Group
        self.groupI = QtWidgets.QGroupBox( title )
        self.groupI.setStyleSheet("QGroupBox { font-weight: bold; } ")
        self.groupI.setLayout( layout )


    def _CreateGroupII(self, title ):

        # Widgets
        self.x3_lineEdit = QLineEdit( '' )
        self.x3_lineEdit.setReadOnly(True)
 
        self.x4_lineEdit = QLineEdit( '' )
        self.x4_lineEdit.setReadOnly(True)
        
        self.spanII_lineEdit = QLineEdit( '' )
        self.spanII_lineEdit.setReadOnly(True)
        
        self.RrefII_lineEdit = QLineEdit( '' )
        self.RrefII_lineEdit.setReadOnly(True)
        
        # Layout
        layout = QtWidgets.QGridLayout()        
        layout.addWidget( QLabel( 'x3 (mm)' ),          0, 0 )
        layout.addWidget( self.x3_lineEdit,             0, 1 )
        layout.addWidget( QLabel( 'x4 (mm)' ),          1, 0 )
        layout.addWidget( self.x4_lineEdit,             1, 1 ) 
        layout.addWidget( QLabel( 'Span II (mm)' ),     2, 0 )
        layout.addWidget( self.spanII_lineEdit,         2, 1 ) 
        layout.addWidget( QLabel( 'R mean (mm)' ),      3, 0 )
        layout.addWidget( self.RrefII_lineEdit,         3, 1 )              
        layout.setAlignment( QtCore.Qt.AlignTop )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)        
        
        # Group
        self.groupII = QtWidgets.QGroupBox( title )
        self.groupII.setStyleSheet("QGroupBox { font-weight: bold; } ")
        self.groupII.setLayout( layout )


    def _CreateGroupIII(self, title ):

        # Widgets
        self.steno_loc_mm_lineEdit = QLineEdit( '' )
        self.steno_loc_mm_lineEdit.setReadOnly(True)
 
        self.steno_loc_rel_lineEdit = QLineEdit( '' )
        self.steno_loc_rel_lineEdit.setReadOnly(True)
        
        self.steno_width_mm_lineEdit = QLineEdit( '' )
        self.steno_width_mm_lineEdit.setReadOnly(True)

        self.steno_radius_lineEdit = QLineEdit( '' )
        self.steno_radius_lineEdit.setReadOnly(True)
        
        self.steno_degree_R_lineEdit = QLineEdit( '' )
        self.steno_degree_R_lineEdit.setReadOnly(True)

        self.steno_degree_A_lineEdit = QLineEdit( '' )
        self.steno_degree_A_lineEdit.setReadOnly(True)
        
        # Layout
        layout = QtWidgets.QGridLayout()        
        layout.addWidget( QLabel( 'Location (mm)' ),   0, 0 )
        layout.addWidget( self.steno_loc_mm_lineEdit,  0, 1 )
        
        layout.addWidget( QLabel( 'Location (%)' ),     1, 0 )
        layout.addWidget( self.steno_loc_rel_lineEdit,  1, 1 )
        
        layout.addWidget( QLabel( 'Width (mm)' ),       2, 0 )
        layout.addWidget( self.steno_width_mm_lineEdit, 2, 1 )

        layout.addWidget( QLabel( 'Radius (mm)' ),      3, 0 )
        layout.addWidget( self.steno_radius_lineEdit,   3, 1 )
        
        layout.addWidget( QLabel( 'Degree R (%)' ),     4, 0 )
        layout.addWidget( self.steno_degree_R_lineEdit, 4, 1 )

        layout.addWidget( QLabel( 'Degree A (%)' ),     5, 0 )
        layout.addWidget( self.steno_degree_A_lineEdit, 5, 1 )
        
        layout.setAlignment( QtCore.Qt.AlignTop )
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        
        # Group
        self.groupIII = QtWidgets.QGroupBox( title )
        self.groupIII.setStyleSheet("QGroupBox { font-weight: bold; } ")
        self.groupIII.setLayout( layout )

    # def _CreateGraphModelGroup(self, title ):
        
        # Check Boxes
    #     self.checkBox1 = QCheckBox("Mean Radius")
    #     self.checkBox2 = QCheckBox("Max Radius")
    #     self.checkBox3 = QCheckBox("Min Radius")
    #     self.checkBox4 = QCheckBox("Trendline")
        
        
    #     self.checkBox1.setChecked( True )
    #     self.checkBox2.setChecked( True )
    #     self.checkBox3.setChecked( True )
    #     self.checkBox4.setChecked( True )
        
    #     self.checkBox1.setEnabled( 0 )
    #     self.checkBox2.setEnabled( 0 )
    #     self.checkBox3.setEnabled( 0 )
    #     self.checkBox4.setEnabled( 0 )
        
    #     # self.checkBox5.setEnabled( 0 )
        
    #     # Layout
    #     layout = QGridLayout()        
    #     layout.addWidget( self.checkBox1, 0, 0 )
    #     layout.addWidget( self.checkBox2, 1, 0 )
    #     layout.addWidget( self.checkBox3, 0, 1 ) 
    #     layout.addWidget( self.checkBox4, 1, 1 )        
        
    #     layout.setColumnStretch(0, 1)
    #     layout.setColumnStretch(1, 2)
    #     layout.setColumnStretch(2, 1)
        
    #     # Group
    #     self.GraphModelGroup = QGroupBox( title )
    #     self.GraphModelGroup.setStyleSheet("QGroupBox { font-weight: bold; } ")
    #     self.GraphModelGroup.setLayout( layout )
        
    #     # Callbacks
    #     # self.checkBox1.clicked.connect( self.SetSceneVisibility )
    #     # self.checkBox2.clicked.connect( self.SetSceneVisibility )
    #     # self.checkBox3.clicked.connect( self.SetSceneVisibility )
    #     # self.checkBox4.clicked.connect( self.SetSceneVisibility )
        
        
        
    def CreateControlGroup(self, title ):

        # Group
        self.controlGroup = QtWidgets.QGroupBox( title )
        self.controlGroup.setStyleSheet("QGroupBox { font-weight: bold; } ")

        # Widgets
        self.button_Save = QtWidgets.QPushButton("   Write to PNG")
        self.button_Export = QtWidgets.QPushButton("   Insert in Table")
        self.button_Reset = QtWidgets.QPushButton("Reset V Lines")
        
        # self.button_Export.setEnabled( 0 )
        
        icon1 = 'SP_DialogResetButton'
        icon2 = 'SP_DialogSaveButton'
        icon3 = 'SP_DialogApplyButton'
        img1 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon1))
        img2 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon2))
        img3 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon3))
        self.button_Reset.setIcon( img1 )
        self.button_Save.setIcon( img2 )
        self.button_Export.setIcon( img3 )

        # Layout
        layout = QtWidgets.QGridLayout()  
        layout.addWidget( self.button_Reset, 0, 0)
        layout.addWidget( self.button_Export,   1, 0) 
        layout.addWidget( self.button_Save,  2, 0)
        layout.setAlignment( QtCore.Qt.AlignTop )
        self.controlGroup.setLayout( layout )
        
        # Callbacks
        self.button_Save.clicked.connect( self.SavePlotter )
        self.button_Export.clicked.connect( self.Insert_row_to_table )      
        self.button_Reset.clicked.connect( self.ResetVlinesPlotter )
        
    def ResultsGroup(self, title):

        # Widgets
        # self.landmark0_Edit_Value = QLineEdit()
        # self.landmark0_Edit_Value.setEnabled( 0 )
        # self.landmark1_Edit_Value = QLineEdit()
        # self.landmark1_Edit_Value.setEnabled( 0 )
        
        self.table1 = QtWidgets.QTableWidget()
        
        
        # labels and tooltip texts
        self.table1.setColumnCount(16)
        self.table1.setHorizontalHeaderLabels(["L(mm)",
            "X1 (mm)", "X2 (mm)", "Span I (mm)",
            "X3 (mm)", "X4 (mm)", "Span II (mm)",
            "Rref I (mm)", "Rref II (mm)",
            "Loc (mm)", "Loc (%)",
            "Width (mm)", "Stenosis R (mm)",
            "Degree R (%)", "Degree A (%)", "Obs"
        ])
        
        tooltips = [
            "Spline Length",
            "Left limit of span I",
            "Right limit of span I",
            "Amplitude of span I",
            "Left limit of span II",
            "Right limit of span II",
            "Amplitude of span II",
            "Reference radius in region I",
            "Reference radius in region II",
            "Stenosis location in mm",
            "Stenosis location (%)",
            "Stenosis width (mm)",
            "Stenosis radius value (mm)", 
            "Stenosis degree (based on radius)",
            "Stenosis degree (based on area)",
            "Observations"
        ]
        
        for i, tip in enumerate(tooltips):
            self.table1.horizontalHeaderItem(i).setToolTip(tip)
        
        for c in range(16):
            self.table1.setColumnWidth(c, 100)

        
        self.deleteRow_Button = QtWidgets.QPushButton("   Delete Row")
        icon1 = 'SP_DialogCancelButton'
        img1 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon1))
        self.deleteRow_Button.setIcon( img1 )
        
        self.exportDat_Button = QtWidgets.QPushButton("   Export Data")
        icon3 = 'SP_DialogSaveButton'
        img3 = self.style().standardIcon(getattr(QtWidgets.QStyle, icon3))
        self.exportDat_Button.setIcon( img3 )


        # Layout
        layout = QtWidgets.QGridLayout()
        # layout.addWidget( QLabel( 'L0' ), 0, 0)
        # layout.addWidget( self.landmark0_Edit_Value, 0, 1)
        # layout.addWidget( QLabel( 'L1' ), 1, 0)
        # layout.addWidget( self.landmark1_Edit_Value, 1, 1)
        layout.addWidget( self.table1, 2, 0, 3, 0)
        layout.addWidget( self.deleteRow_Button, 5, 0)
        layout.addWidget( self.exportDat_Button, 5, 1)
        


        # Group
        self.ResultsGroup = QtWidgets.QGroupBox( title )
        self.ResultsGroup.setStyleSheet("QGroupBox { font-weight: bold; } ") 
        self.ResultsGroup.setLayout( layout ) 

        # Callbacks
        self.deleteRow_Button.clicked.connect(self.deleteSelectedRow)
        # self.exportDat_Button.clicked.connect(self.export_table_to_csv)
    
    def Insert_row_to_table(self):
        values = [
            round(self.length_tot, 2),
            self.x1_lineEdit.text(),
            self.x2_lineEdit.text(),
            self.spanI_lineEdit.text(),
            self.x3_lineEdit.text(),
            self.x4_lineEdit.text(),
            self.spanII_lineEdit.text(),
            self.RrefI_lineEdit.text(),
            self.RrefII_lineEdit.text(),
            self.steno_loc_mm_lineEdit.text(),
            self.steno_loc_rel_lineEdit.text(),
            self.steno_width_mm_lineEdit.text(),
            self.steno_radius_lineEdit.text(),
            self.steno_degree_R_lineEdit.text(),
            self.steno_degree_A_lineEdit.text(),
            ""  # Observações (campo editável)
        ]
    
        row_position = self.table1.rowCount()
        self.table1.insertRow(row_position)
    
        for col, value in enumerate(values):
            item = QtWidgets.QTableWidgetItem(str(value))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
    
            # Permitir edição apenas na última coluna
            if col == 15:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            else:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
    
            self.table1.setItem(row_position, col, item)
        
    def deleteSelectedRow(self, length_tot):
        selected_row = self.table1.currentRow()
        if selected_row >= 0:
            # Remove da tabela
            self.table1.removeRow(selected_row)

            self.canvas.draw()
            self.canvas.flush_events()

    def export_table_to_csv(self, dataset, isovalue):
        # Abre diálogo para escolher caminho
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table as CSV",
            f"{dataset}_{isovalue}",
            "CSV Files (*.csv);; DAT Files (*.dat)"
        )
    
        if not path:
            return  # O utilizador cancelou
    
        try:
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=',')
    
                # Escreve os cabeçalhos da tabela
                headers = [
                    self.table1.horizontalHeaderItem(col).text()
                    for col in range(self.table1.columnCount())
                ]
                writer.writerow(headers)
    
                # Escreve todas as linhas da tabela
                for row in range(self.table1.rowCount()):
                    row_data = [
                        self.table1.item(row, col).text() if self.table1.item(row, col) else ""
                        for col in range(self.table1.columnCount())
                    ]
                    writer.writerow(row_data)
    
            QMessageBox.information(self, "Exportação Concluída", f"Ficheiro CSV guardado em:\n{path}")
    
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Exportar", f"Ocorreu um erro:\n{str(e)}")


    # ===========================================================
    # Q Callbacks
    # ===========================================================  
    def SavePlotter(self):
    
        outputFilename = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save As...', './output/graph.png'  ,
                filter=('*.png'))[0]     
        if ( outputFilename ):
            print ("Saving:", outputFilename)
            self.fig.savefig( outputFilename ) # , bbox_inches='tight' )
            
          
    def ExportData(self):
        print ('ExportData: NOT IMPLEMENTED!')

       
    def ClearPlotter(self):
        # print ('ClearPlotter')
        self.ClearAxes()
        self.SetDefaultAxesLabels()
        self.canvas.draw()
        self.canvas.flush_events()
        
    def ResetVlinesPlotter(self):  
        
        x_min, x_max = self.ax1.get_xlim()
        self.length_tot = x_max
        
        print(self.length_tot)
        # Set vlines based on total length of snake
        self.vline1.set_x( (1/5)*self.length_tot )
        self.vline2.set_x( (2/5)*self.length_tot )
        self.vline3.set_x( (3/5)*self.length_tot )
        self.vline4.set_x( (4/5)*self.length_tot )        
        
        # Refresh the canvas
        self.canvas.flush_events()
        

# ========================================================

if __name__ == "__main__":
    
    app = QApplication( sys.argv )
    
    qplt1 = GraphPlotter()
    # myapp.myapp.Help_About()
    
    
    # Data
    pi = np.pi
    N = 2000
    x = np.linspace(-5, 5, N, endpoint=True)
    y = 1.5 - np.sin(pi*(x - 1))/(pi*(x - 1))
    
    qplt1.ax1.set_xlim( x.min(), x.max() )
    qplt1.ax1.set_ylim( 0, y.max() * 1.5 )
    qplt1.ax2.set_xlim( x.min(), x.max() )
    
    qplt1.vline1.set_x( x.min() + 1*( x.max() - x.min())/5 )
    qplt1.vline2.set_x( x.min() + 2*( x.max() - x.min())/5 )
    qplt1.vline3.set_x( x.min() + 3*( x.max() - x.min())/5 )
    qplt1.vline4.set_x( x.min() + 4*( x.max() - x.min())/5 )
    
    qplt1.SetData( x, y )    
    
    qplt1.UpdatePlot()
    
    # qplt.canvas.draw()
    qplt1.canvas.flush_events()
    
    
    
    
    
    qplt1.show()
    #myapp.showMaximized()
   
    # -----------------------------------------    
    sys.exit( app.exec_() )
    
# ===============================================