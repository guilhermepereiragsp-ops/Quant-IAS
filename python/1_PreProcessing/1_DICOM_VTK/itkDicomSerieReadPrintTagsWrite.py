""" itkDicomSerieReadPrintTagsWrite.py 

https://examples.itk.org/src/io/gdcm/readdicomseriesandwrite3dimage/documentation
https://examples.itk.org/src/io/gdcm/readandprintdicomtags/documentation

"""

import numpy as np
import itk

INPUTDIR = "../../../datasets/"

worklistFilename = INPUTDIR + 'STEN_worklist.txt'
worklist = np.loadtxt( worklistFilename, dtype=str )
# print( worklist )
print( len(worklist) )


# ITK Image types
# ------------------------------------------------------------
Dimension = 3
PixelType = itk.US
ImageType = itk.Image[PixelType, Dimension]


# for n in range( len(worklist) ):
for n in [0]:

    dataset = worklist[n]
    print(dataset)

    dicomDirectory = INPUTDIR + "stens_dcm/%s/" % dataset    
    outputFilename = INPUTDIR + "stens_vtk/%s.vtk" % dataset

    # Generate the names of DICOM files
    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(True)
    namesGenerator.SetGlobalWarningDisplay(True)
    namesGenerator.SetDirectory( dicomDirectory )

    # Get DICOM Series 
    seriesUID = namesGenerator.GetSeriesUIDs()
    
    print("DICOM directory: " + dicomDirectory)
    if len(seriesUID) < 1:
        print("No DICOMs in: " + dicomDirectory)
        # sys.exit(1)
    else:
        print("DICOM Series: " , len(seriesUID) )
        for uid in seriesUID:
            print(uid)
    print ("")
    
    # Get the names of files of the first image serie    
    dicomSerie = seriesUID[0]
    fileNames = namesGenerator.GetFileNames( dicomSerie )


    # Setup the image series reader using GDCMImageIO
    dicomIO = itk.GDCMImageIO.New()
    # dicomIO.LoadPrivateTagsOn()
    
    # Read DICOM Image Serie
    reader = itk.ImageSeriesReader[ImageType].New()
    reader.SetImageIO( dicomIO )
    reader.SetFileNames( fileNames )
    reader.Update()

    # ITK Image
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

    # Write ITK Image to VTK format
    print ("Writing:", outputFilename)
    writer = itk.ImageFileWriter[ImageType].New()
    writer.SetInput( itkimg )
    writer.SetFileName( outputFilename )
    writer.Update()
    print ("")


    # DICOM tags from file headers - GetMetaDataDictionary()
    # Print the key value pairs from the metadadictionary
    
    metadata = dicomIO.GetMetaDataDictionary()
    tagkeys = metadata.GetKeys()

    for tagkey in tagkeys:
        try:
            tagvalue = metadata[tagkey]
            print(tagkey , str(tagvalue))        
            # label = itk.GDCMImageIO.GetLabelFromTag(tagkey, "")
            # print( tagkey + " " + label[1] + " " + str(tagvalue) )        
        except RuntimeError:
            print("Cannot pass " + tagkey + "into metadadictionary")
    print ("")              
    
    # Access metadata (label and tagvalue) of some tagkeys
    entryIDs = []
    entryIDs.append( '0010|0020' ) # Patient ID
    entryIDs.append( '0010|0040' ) # Patient's Sex
    entryIDs.append( '0010|1010' ) # Patient's Age
    entryIDs.append( '0032|4000' ) # Study Comments

    for entryID in entryIDs:
        if not metadata.HasKey(entryID):
            print("tag: " + entryID + " not found in series")
        else:
            # The second parameter is mandatory in python 
            # to get the string label value
            label = itk.GDCMImageIO.GetLabelFromTag(entryID, "")
            tagvalue = metadata[entryID]
            print( entryID + "\t" + label[1] + "\t" + str(tagvalue))
    print ("")


print ("EOF.") 