""" itkThickness3D.py """

# First, install python module of same itk version!
# > pip install itk-thickness3d==5.3 

import itk
import datetime
import numpy as np

tic = datetime.datetime.now()

INPUTDIR = "../../datasets/"

worklistFilename = INPUTDIR + 'STEN_worklist.txt'
worklist = np.loadtxt( worklistFilename, dtype=str )
# print( worklist )
# print( len(worklist) )

for i in range(min(17, len(worklist))):
    dataset = worklist[i]
    
    # dataset = "Sten0031"
    
    res = "025"
    # res = "050"
    
    # threshold = 160
    threshold = 180
    # threshold = 200
    
    morph = "none"
    # morph = "open"
    # morph = "close"
    
    inputFilename   = "../../datasets/stens_isotropic_%s/%s_isotropic_%s.vtk" % ( res, dataset, res )
    
    # outputFilename1 = "./output/%s_%s_%s_%s_mask.vtk" % ( dataset, res, threshold, morph )
    outputFilename2 = './output/%s_%s_%s_%s_skeleton.vtk' % ( dataset, res, threshold, morph )
    # outputFilename3 = './output/%s_isotropic_%s_thickness.vtk' % ( dataset, res )
    
    
    # ITK Image types
    # ------------------------------------------------------------
    Dimension = 3
    PixelType = itk.US
    ImageType = itk.Image[PixelType, Dimension]
    
    ThicknessPixelType = itk.F
    ThicknessImageType = itk.Image[ThicknessPixelType, Dimension]
    
    
    # Read ITK Image (mask)
    # ------------------------------------------------------------
    print ("Reading:", inputFilename)
    reader = itk.ImageFileReader[ImageType].New()
    reader.SetFileName( inputFilename )
    reader.Update()
    
    itkimg = ImageType.New()
    itkimg = reader.GetOutput()
    
    
    # Binary Threshold
    # ------------------------------------------------------------
    print ("Binary Threshold")
    binaryThreshold = itk.BinaryThresholdImageFilter[ImageType, ImageType].New()
    # lower = 160
    # upper = 30000
    binaryThreshold.SetLowerThreshold( threshold )
    # binaryThreshold.SetUpperThreshold( upper )
    binaryThreshold.SetOutsideValue( 0 )
    binaryThreshold.SetInsideValue( 1 )
    binaryThreshold.SetInput( itkimg )
    binaryThreshold.Update()
    
    mask = ImageType.New()
    mask = binaryThreshold.GetOutput()
    
    
    # # Define a structuring element (kernel)
    # StructuringElementType = itk.FlatStructuringElement[Dimension]
    # radius = [1] * Dimension  # raio de 1 voxel em todas as direções
    # kernel = StructuringElementType.Ball(radius)
    
    # # Binary Dilation
    # binaryDilate = itk.BinaryDilateImageFilter[ImageType, ImageType, StructuringElementType].New()
    # binaryDilate.SetKernel(kernel)
    # binaryDilate.SetForegroundValue(1)
    # binaryDilate.SetBackgroundValue(0)
    # binaryDilate.SetInput(mask)
    # binaryDilate.Update()
    
    # # Atualiza a máscara com o resultado da abertura morfológica
    # mask = binaryDilate.GetOutput()
    
    # # Binary Erosion
    # binaryErode = itk.BinaryErodeImageFilter[ImageType, ImageType, StructuringElementType].New()
    # binaryErode.SetKernel(kernel)
    # binaryErode.SetForegroundValue(1)
    # binaryErode.SetBackgroundValue(0)
    # binaryErode.SetInput(mask)
    # binaryErode.Update()
    
    # # Binary Dilation
    # binaryDilate = itk.BinaryDilateImageFilter[ImageType, ImageType, StructuringElementType].New()
    # binaryDilate.SetKernel(kernel)
    # binaryDilate.SetForegroundValue(1)
    # binaryDilate.SetBackgroundValue(0)
    # binaryDilate.SetInput(binaryErode.GetOutput())
    # binaryDilate.Update()
    
    # # Atualiza a máscara com o resultado da abertura morfológica
    # mask = binaryDilate.GetOutput()
    
    
    # Skeleton
    # ------------------------------------------------------------
    print ('Binary Thinning 3D')
    thinningFilter = itk.BinaryThinningImageFilter3D[ImageType, ImageType].New()
    thinningFilter.SetInput( mask )
    thinningFilter.Update()
    
    skeleton = ImageType.New()
    skeleton = thinningFilter.GetThinning()
    
    # Thickness Map
    # ------------------------------------------------------------
    # print ('Thickness Map')
    # thicknessFilter = itk.MedialThicknessImageFilter3D[ImageType, ThicknessImageType].New()
    # thicknessFilter.SetInput( mask )
    # thicknessFilter.Update()
    
    # thickness = ThicknessImageType.New()
    # thickness = thicknessFilter.GetOutput()
    
    
    # Write ITK Image - Mask
    # ------------------------------------------------------------
    # print ( 'Writing:', outputFilename1 )
    # writer1 = itk.ImageFileWriter[ImageType].New()
    # writer1.SetFileName( outputFilename1 )
    # writer1.SetInput( mask )
    # writer1.Update()
    
    # Write ITK Image - Skeleton
    # ------------------------------------------------------------
    print ( 'Writing:', outputFilename2 )
    writer2 = itk.ImageFileWriter[ImageType].New()
    writer2.SetFileName( outputFilename2 )
    writer2.SetInput( skeleton )
    writer2.Update()
    
    # Write ITK Image - Thickness Map
    # ------------------------------------------------------------
    # print ( 'Writing:', outputFilename3 )
    # writer3 = itk.ImageFileWriter[ThicknessImageType].New()
    # writer3.SetFileName( outputFilename3 )
    # writer3.SetInput( thickness )
    # writer3.Update()
    
    toc = datetime.datetime.now()
    print(toc-tic)
    
print ("EOF.")
    
