""" itkResampleImage.py

@author: Carlos Vinhais
cvinhais@gmail.com
Fev 2025


ITK class: ResampleImageFilter

https://examples.itk.org/src/filtering/imagegrid/resampleanimage/documentation

"""
 
import numpy as np
import itk

INPUTDIR = "../../../datasets/"

worklistFilename = INPUTDIR + 'STEN_worklist.txt'
worklist = np.loadtxt( worklistFilename, dtype=str )
# print( worklist )
print( len(worklist) )


# User Parameters
# ------------------------------------------------------------
ISOTROPIC_SPACING = 0.25


# ITK Image types
# ------------------------------------------------------------
Dimension = 3
PixelType = itk.US
ImageType = itk.Image[PixelType, Dimension]


for n in range( len(worklist) ):
# for n in [0]:

    dataset = worklist[n]
    print(dataset)

    inputFilename  = INPUTDIR + "stens_vtk/%s.vtk" % ( dataset )
    outputFilename = INPUTDIR + "stens_isotropic_025/%s_isotropic_025.vtk" % ( dataset )
    
    # Read ITK Image
    # ------------------------------------------------------------
    print ("Reading:", inputFilename)
    reader = itk.ImageFileReader[ImageType].New()
    reader.SetFileName( inputFilename )
    reader.Update()
    
    itkimg = ImageType.New()
    itkimg = reader.GetOutput()
    
    # ITK Image Info
    origin  = itkimg.GetOrigin()
    spacing = itkimg.GetSpacing()
    region  = itkimg.GetRequestedRegion()
    size    = region.GetSize()
    start   = region.GetIndex()
    
    print ("ITK Image Info:")
    print ("  origin  =", origin)
    print ("  spacing =", spacing)
    print ("  size    =", size)
    print ("  start   =", start)
    print ("")
    
    # Resample Image
    # ------------------------------------------------------------
    # output_spacing = [spacing[d]*spacing[d]/spacing[d] for d in range(dimension)]
    # ou ...
    
    outputSpacing = [0.0, 0.0, 0.0]
    for d in range(3):
        outputSpacing[d] = ISOTROPIC_SPACING
    
    outputSize = [0, 0, 0]
    for d in range(3):
        outputSize[d] = int(size[d]*spacing[d]/outputSpacing[d]);
    
    
    transform = itk.IdentityTransform[itk.D,3].New()
    
    # interpolator = itk.ResampleImageFilter[ImageType,ImageType].New()
    
    resampler = itk.ResampleImageFilter[ImageType,ImageType].New()
    resampler.SetInput( reader.GetOutput() )
    resampler.SetTransform( transform )
    # resampler.SetInterpolator(interpolator)
    resampler.SetOutputOrigin( origin )
    resampler.SetOutputSpacing( outputSpacing )
    # resampler.SetOutputDirection(reader->GetOutput()->GetDirection())
    resampler.SetSize( outputSize )
    resampler.Update()
        
    resampled = ImageType.New()
    resampled = resampler.GetOutput()
    
    # RESAMPLED Info
    origin  = resampled.GetOrigin()
    spacing = resampled.GetSpacing()
    region  = resampled.GetRequestedRegion()
    size    = region.GetSize()
    start   = region.GetIndex()
    
    print ("RESAMPLED Image Info:")
    print ("  origin  =", origin)
    print ("  spacing =", spacing)
    print ("  size    =", size)
    print ("  start   =", start)
    print ("")
    
    # Recenter resampled Image
    # ------------------------------------------------------------    
    # new origin, mm
    # World coordinate system (0,0,0) mm is at center of resampled image
    new_origin = itk.Point[itk.F, 3]()
    for d in range(3):
        new_origin[d] = -(size[d]*spacing[d])/2.0
    
    resampled.SetOrigin( new_origin )
    

    # RESAMPLED CENTERED  Info
    origin  = resampled.GetOrigin()
    spacing = resampled.GetSpacing()
    region  = resampled.GetRequestedRegion()
    size    = region.GetSize()
    start   = region.GetIndex()
    
    print ("RESAMPLED CENTERED Image Info:")
    print ("  origin  =", origin)
    print ("  spacing =", spacing)
    print ("  size    =", size)
    print ("  start   =", start)
    print ("")

    
    # Write to VTK format
    print ("Writing:", outputFilename)
    writer = itk.ImageFileWriter[ImageType].New()
    writer.SetInput( resampled )
    writer.SetFileName( outputFilename )
    writer.Update()

print ("EOF.")
