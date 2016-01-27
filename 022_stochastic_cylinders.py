import logging
import os
from functools import partial
from multiprocessing.pool import Pool
import multiprocessing
from time import time
import ogr
import subprocess
import shlex

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

def oidCloudMetric(OID,  layerDefinition):
   dictFields = extractDictFields(layerDefinition)   
   geom = feature.GetGeometryRef()
   print geom.Centroid().ExportToWkt()
   featdfn = feature.GetDefnRef
   OID = ogrTypedFieldVal(feature,layerDefinition, dictFields["OBJECTID"])
   fieldDfn = feature.GetFieldDefnRef(dictFields["OBJECTID"])
   
   ptWKT = "POINT ("+str(E)+" "+str(N)+")"
   outSHPPath = r"Z:/poly"+str(OID)+".shp"
   
   testSHP = ptWKTtoSHP(ptWKT, outSHPPath, inOID = OID)
   
   cmdSrc = dictCommands["clippoly"]+" "+outSHPPath+r" Z:\\output"+str(OID)+r" B:\\LASNorm_out\\*.las"
   
   print run_and_return(cmdSrc)
   
   cmdSrc = dictCommands["cloudmetrics"]+r" Z:\\output"+str(OID)+".lda Z:\\output"+str(OID)+".csv"
   print run_and_return(cmdSrc)
   f = open("Z:\\output"+str(OID)+".csv", "r")
   k = 0
   dictHeader = {}
   for lines in f:
      if k == 0 : 
         listLine = lines.replace(" ","_").rstrip().split(",")
         for i in range(len(listLine)):
            dictHeader[i] = listLine[i]
            print listLine[i]
         k= k+1
      elif k == 1:
         listLine = lines.split(",")
         return listLine
   return []



def ptCloudMetric(feature, dictFields, ogrTypedFieldVal, layerDefinition, ptWKTtoSHP, dictCommands):
   geom = feature.GetGeometryRef()
   print geom.Centroid().ExportToWkt()
   featdfn = feature.GetDefnRef
   OID = ogrTypedFieldVal(feature,layerDefinition, dictFields["OBJECTID"])
   fieldDfn = feature.GetFieldDefnRef(dictFields["OBJECTID"])
   N   = ogrTypedFieldVal(feature,layerDefinition, dictFields["Northing"])
   E   =  ogrTypedFieldVal(feature,layerDefinition, dictFields["Easting"])
   
   ptWKT = "POINT ("+str(E)+" "+str(N)+")"
   outSHPPath = r"Z:/poly"+str(OID)+".shp"
   
   testSHP = ptWKTtoSHP(ptWKT, outSHPPath, inOID = OID)
   
   cmdSrc = dictCommands["clippoly"]+" "+outSHPPath+r" Z:\\output"+str(OID)+r" B:\\LASNorm_out\\*.las"
   
   print run_and_return(cmdSrc)
   
   cmdSrc = dictCommands["cloudmetrics"]+r" Z:\\output"+str(OID)+".lda Z:\\output"+str(OID)+".csv"
   print run_and_return(cmdSrc)
   f = open("Z:\\output"+str(OID)+".csv", "r")
   k = 0
   dictHeader = {}
   for lines in f:
      if k == 0 : 
         listLine = lines.replace(" ","_").rstrip().split(",")
         for i in range(len(listLine)):
            dictHeader[i] = listLine[i]
            print listLine[i]
         k= k+1
      elif k == 1:
         listLine = lines.split(",")
         return listLine
   return []
   
def LASNormalizer(inputLAS):
   os.system( r"C:\\Apps\\lasnorm_v2.exe "+sourceDEM+" "+  \
             sourceDir+ os.sep + inputLAS + " "+           \
             destDir  + os.sep + inputLAS[:-4]+"_norm.las"  )   

def myfunc(conn,text):
    conn.send(text)
    conn.close()    
                 

def callFunc(text):
    parent_conn, child_conn=multiprocessing.Pipe()
    proc = multiprocessing.Process(target=myfunc, args=(child_conn,text,))
    proc.start()  
    self.messages.write(parent_conn.recv())
    proc.join() 
    
def main():
   # ##
   # 0 Logging Init
   # ##
   logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   logging.getLogger('requests').setLevel(logging.CRITICAL)
   logger = logging.getLogger(__name__)
   
   dictCommands = { "clippoly" : r"C:\\Apps\\FUSION\\PolyClipData.exe",
                    "cloudmetrics" : r"C:\\Apps\\FUSION\\cloudmetrics.exe"}
   
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
   
   
   
    #create an output datasource in memory
   outdriver=ogr.GetDriverByName('MEMORY')
   source=outdriver.CreateDataSource('memData')

   layerDefinition = layer.GetLayerDefn()
   dictFields = extractDictFields(layerDefinition)  
   #LASNormalizer(listLAS[0])
   ts = time()
    
  
   #listOIDs = getListOIDs(layer,dictFields)
    
   #with Pool(10) as p:
   p = Pool(10)
   # ptCloudMetric(feature, dictFields, ogrTypedFieldVal, layerDefinition, ptWKTtoSHP, dictCommands):
   #partialCM = partial(oidCloudMetric, layerDefinition )
   p.map(oidCloudMetric, listOIDs)
    
   logging.info('Took %s seconds', time() - ts)

if __name__ == '__main__':
   main()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
