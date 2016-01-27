import logging
import os
from functools import partial
from multiprocessing.pool import Pool
import multiprocessing
from time import time
import ogr
import subprocess
import shlex
import numpy.random as rand
import numpy as np

def colAvg(inA):
    localList = []
    rowList = []
    lenRow = len( inA[0] )
    for i in range( lenRow ):
        for rows in inA:
             localList.append( rows[i] )
        rowList.append(localList)
    return rowList

def run_and_return(cmdSrc, cmdDest = ""):
    """Run a system command and return the output"""
    srcProcess = subprocess.Popen(shlex.split(cmdSrc), stdout=subprocess.PIPE)
    if cmdDest:
        destProcess = subprocess.Popen(shlex.split(cmdDest),
                                       stdin=srcProcess.stdout,
                                       stdout=subprocess.PIPE)
        stdout, stderr = destProcess.communicate()
    else:
        stdout, stderr = srcProcess.communicate()

    return stdout.decode('ascii')

def run_and_grep(cmdSrc, grepTerm):
    """Run a system command and return the output"""

    srcProcess = subprocess.Popen(tuple(cmdSrc.split(" ")), stdout=subprocess.PIPE)
    stdout, stderr = srcProcess.communicate()

    asciiOut = stdout.decode('ascii').splitlines()

    for lines in asciiOut:
        if grepTerm in lines:
            return lines



def ogrPrettyPrintField(feat,feat_defn,index):
    i = index
    field_defn = feat_defn.GetFieldDefn(i)
        # Tests below can be simplified with just :
        # print feat.GetField(i)
    if field_defn.GetType() == ogr.OFTInteger: #or field_defn.GetType() == ogr.OFTInteger64:
        print "%d" % feat.GetFieldAsInteger(i)
    elif field_defn.GetType() == ogr.OFTReal:
        print "%.3f" % feat.GetFieldAsDouble(i)
    elif field_defn.GetType() == ogr.OFTString:
        print "%s" % feat.GetFieldAsString(i)
    else:
        print "%s" % feat.GetFieldAsString(i)   

def ogrTypedFieldVal(feat,feat_defn,index):
    i = index
    field_defn = feat_defn.GetFieldDefn(i)
        # Tests below can be simplified with just :
        # print feat.GetField(i)
    if field_defn.GetType() == ogr.OFTInteger: #or field_defn.GetType() == ogr.OFTInteger64:
        return "%d" % feat.GetFieldAsInteger(i)
    elif field_defn.GetType() == ogr.OFTReal:
        return "%.3f" % feat.GetFieldAsDouble(i)
    elif field_defn.GetType() == ogr.OFTString:
        return "%s" % feat.GetFieldAsString(i)
    else:
        return "%s" % feat.GetFieldAsString(i)   
# from download import <func_A>, <func_B>, <func_C>
def ptWKTtoSHP(inPtWKT,outSHPPath,inOID=-9999,inBuffDist=10):
    import os
    if os.path.exists(outSHPPath): driver.DeleteDataSource(outSHPPath)

    ds = driver.CreateDataSource(outSHPPath)
    layer = ds.CreateLayer("plot",geom_type=ogr.wkbPolygon)
    fieldDef = ogr.FieldDefn("PID",ogr.OFTInteger)
    layer.CreateField(fieldDef)

    featureDfn = layer.GetLayerDefn()
    feat = ogr.Feature(featureDfn)

    pt = ogr.CreateGeometryFromWkt(inPtWKT)
    bufferDist = 10
    poly = pt.Buffer(inBuffDist)  
    feat.SetGeometry(poly)
    feat.SetField("PID",inOID)

    layer.CreateFeature(feat)
    ds.Destroy()




def unpackPtWKT(ptWKT):
    if len(ptWKT) == 2:
        return ptWKT
    afterP1 = ptWKT.split("(")[1]
    beforeP2  = afterP1.split(")" )[0]
    X,Y = beforeP2.split(" ")
    return (X,Y)

def packPtWKT(tupleXY):
    x,y = tupleXY
    ptWKT = "POINT ("+str(x)+" "+str(y)+")"
    return ptWKT

def extractDictFields(layerDefinition):
    dictFields = {}

    for i in range(layerDefinition.GetFieldCount()):
        lyrName = layerDefinition.GetFieldDefn(i).GetName()   
        dictFields[lyrName] = i
        #  print lyrName
    return dictFields

def getListOIDs(inputLayer, dictFields, fieldName = "OBECTID"):
    layer = inputLayer
    layerDefinition = layer.GetLayerDefn()
    listOIDs = []
    for feats in layer:   
        geom = feats.GetGeometryRef()
    #print geom.Centroid().ExportToWkt()
        featdfn = feats.GetDefnRef
        OID = ogrTypedFieldVal(feats,layerDefinition, dictFields["OBJECTID"])   
        listOIDs.append(OID)
    return listOIDs




def mpMetricsCylinder(inTuple):
    '''
    '''
    OID, N = inTuple
    print "starting "+str(inTuple)
    os.chdir(r"Z:\\plot"+str(OID))
    # factor this into module
    dictCommands = { "clippoly" : r"C:\\Apps\\FUSION\\PolyClipData.exe",
                         "cloudmetrics" : r"C:\\Apps\\FUSION\\cloudmetrics.exe",
                         "clipdata" : r"C:\\Apps\\FUSION\\ClipData.exe"        }       
    newFolder =  r"Z:\\plot"+str(OID)
    clippedBlock = newFolder+r"\\clip.lda" 
    thisShp = newFolder+r"\\"+"plot"+str(OID)+"_"+str(N)+".shp"
    thisLDA = newFolder+r"\\"+"plot"+str(OID)+"_"+str(N)+".lda"
    outputCSV = "output"+str(OID)+"_"+str(N)+".csv"
    # ####
    listToClean = [thisLDA,outputCSV]
    for items in listToClean:
        if os.path.isfile( items ): os.remove( items )
    
    if os.path.isfile( outputCSV ): os.remove( outputCSV )
    
    cmdSrc = dictCommands["clippoly"]+r" /index "+" "+thisShp+" "+thisLDA+" "+clippedBlock
    print run_and_return(cmdSrc)          


    cmdSrc = dictCommands["cloudmetrics"]+r" "+ thisLDA +" " + outputCSV
    print run_and_return(cmdSrc)
 
    f = open(outputCSV, "r")
    k = 0
    
    dictHeader = {}
    listLines = []
    
    for lines in f:
        print lines
        if k == 0 : 
            listLine = lines.replace(" ","_").rstrip().split(",")
            for i in range(len(listLine)):
                dictHeader[i] = listLine[i]
                print listLine[i]
            k= k+1
            listLines.append(listLine)
            #print listLine
        elif k == 1:
            listLine = lines.split(",")
            listLines.append(listLine)
            goodLine= listLine
            
    
    return goodLine

def oidCloudMetric(inTuple, BufferDist = 10, sdX = 1., sdY = 1., nSamples = 100, dist = "Normal" ):
    
    import csv
    import matplotlib
    import scipy as sp
    import numpy as np
    
    
    dictCommands = { "clippoly" : r"C:\\Apps\\FUSION\\PolyClipData.exe",
                     "cloudmetrics" : r"C:\\Apps\\FUSION\\cloudmetrics.exe",
                     "clipdata" : r"C:\\Apps\\FUSION\\ClipData.exe"        }   
    
    #outdriver=ogr.GetDriverByName('MEMORY')
    #source=outdriver.CreateDataSource('memData')
    OID = inTuple[0]
    ptWKT = inTuple[1]
    
    outdriver = ogr.GetDriverByName("ESRI Shapefile")
    
    outSHPPath = r"Z:\\poly"+str(OID)+".shp"
    
    if os.path.exists(outSHPPath):
        outdriver.DeleteDataSource(outSHPPath)
        
    source = outdriver.CreateDataSource(outSHPPath)

    layer = source.CreateLayer("Buffers", geom_type = ogr.wkbPolygon)
    
    field_OID = ogr.FieldDefn("OID", ogr.OFTInteger)
    field_N   = ogr.FieldDefn( "N" , ogr.OFTInteger)
     
    layer.CreateField(field_OID)
    layer.CreateField(field_N)
    
    (X,Y) = unpackPtWKT(ptWKT)
    Xs = rand.normal( X, sdX, nSamples )
    Ys = rand.normal( Y, sdY, nSamples )
    
    maxX = Xs.max() + 15
    minX = Xs.min() - 15
    maxY = Ys.max() + 15
    minY = Ys.min() - 15
 
    
    for i in range(nSamples):
        feature = ogr.Feature(layer.GetLayerDefn() )
        thisPtWKT = packPtWKT( (Xs[i], Ys[i]) )
        feature.SetField("OID" ,  OID )
        feature.SetField( "N"  ,   i  )
        point = ogr.CreateGeometryFromWkt(thisPtWKT)
        poly = point.Buffer( BufferDist )
        
        feature.SetGeometry(poly)
        
        #CreateSingleton(feature, (OID,i) )
        
        layer.CreateFeature(feature)
        feature.Destroy()
        

    source.Destroy()
    
    newFolder =  r"Z:\\plot"+str(OID)
    try:
        os.mkdir( newFolder )
    except:
        pass
    
    
    #  Generate the SHP of each sampled cylinder
    for i in range(nSamples):
        listSHP = os.listdir(newFolder)#+r"\\plot"+str(OID)+"_"+str(i) )
        match = r"plot"+str(OID)+"_"+str(i)
        for items in listSHP:
            if match in items: os.remove(newFolder+r"\\"+items)
        thisShp = newFolder+r"\\"+"plot"+str(OID)+"_"+str(i)+".shp"
        cmdSrc = '''ogr2ogr -f "ESRI Shapefile" -fid '''+str(i)+" "+thisShp+" "+outSHPPath
        print run_and_return(cmdSrc)
        
    #Subset the lidar data for the family of cylinder
    maxMin = str(minX)+" "+str(minY)+" "+str(maxX)+" "+str(maxY)
    clippedBlock = newFolder+r"\\clip.lda"    
    cmdSrc = dictCommands["clipdata"]+r" /index B:\\LASNorm_out\\*.las "+clippedBlock+" "+maxMin
    print run_and_return(cmdSrc)    
    
    #Call MP on   
    
    

    
    os.chdir(newFolder)
    
    # prep the list
    listRun = []
    for items in range(nSamples):
        listRun.append( (OID,items) )   
    
    print listRun
    #now run the pool
    p = Pool(10)
    #res = p.map(mpMetricsCylinder, [(1,1),(1,2),(1,3),(1,4)] )    
    res = p.map(mpMetricsCylinder, listRun)
    outputs = [result for result in res]
    print outputs
    
    #print mpMetricsCylinder( tupleOidN )
    #listToClean = [thisShp,thisLDA,outputCSV,clippedBlock]
    #for items in listToClean:
    #    if os.path.isfile( items ): 
    #        try:
    #            os.remove( items ) 
    #        except:
    #            pass
    os.chdir(r"..")
    
    return outputs
    
def main():
    # ##
    # 0 Logging Init
    # ##
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logger = logging.getLogger(__name__)


    listCloudMetrics = []   

    sourceLAS = r"B:\\LASNorm_out"
    sourceSHP = r"A:\\AllPlotCenters_fromEditedSSF.shp"
    destDir   = r"B:\\LASNorm_out"

    listGrid = []

    listMetrics2 = []

    inSHP  = r"A:\AllPlotCenters_fromEditedSSF.shp"
    driver = ogr.GetDriverByName('ESRI Shapefile')

    dataSource = driver.Open(inSHP, 0) # 0 means read-only. 1 means writeable.      


    if dataSource is None:
        print 'Could not open %s' % (inSHP)
    else:
        print 'Opened %s' % (inSHP)
        layer = dataSource.GetLayer()
        featureCount = layer.GetFeatureCount()
        lyrDefn = layer.GetLayerDefn()
        fieldCount = lyrDefn.GetFieldCount()
        dictFields = extractDictFields(lyrDefn)
        print "Number of features in %s: %d" % (os.path.basename(inSHP),featureCount)
        listOIDs = []
        listOIDs = getListOIDs(layer, dictFields)

    print listOIDs
    
    layer.ResetReading()
    
    ptWKTs = []
    feat = layer.GetNextFeature()
    while feat:
        geom = feat.GetGeometryRef()
        ptWKT = geom.ExportToWkt()
        OID = feat.GetFieldAsInteger(0)
        inTuple = (OID,ptWKT)
        ptWKTs.append(inTuple)
        del ptWKT
        feat = layer.GetNextFeature()

    print ptWKTs

    ts = time()


    #listOIDs = getListOIDs(layer,dictFields)
    
    thisPlot = 0    
    
    #with Pool(10) as p:
    p = Pool(10)
    # ptCloudMetric(feature, dictFields, ogrTypedFieldVal, layerDefinition, ptWKTtoSHP, dictCommands):
    #partialCM = partial(oidCloudMetric, layerDefinition )
    res = oidCloudMetric( ptWKTs[thisPlot] )
    
    #print outputs
    print res
    
    outfile = open(r"Z://output"+str(ptWKTs[thisPlot]))    
    
    
    #p.map(oidCloudMetric, ptWKTs)

    logging.info('Took %s seconds', time() - ts)

if __name__ == '__main__':
    main()
