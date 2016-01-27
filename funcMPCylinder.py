# ###########################################################
    def CreateSingleton(inFeature, tupleOidN ):
        outdriver = ogr.GetDriverByName("ESRI Shapefile")
        OID, N = tupleOidN
        
        newFolder =  r"Z:\\plot"+str(OID)
        try:
            os.mkdir( newFolder )
        except:
            pass
        
        outSHPPath = newFolder+os.sep+"plot"+str(OID)+"_"+str(N)+".shp"
        
        if os.path.exists(outSHPPath):
            outdriver.DeleteDataSource(outSHPPath)
            
        source = outdriver.CreateDataSource(outSHPPath)
    
        layer = source.CreateLayer("Buffers", geom_type = ogr.wkbPolygon)
        
        field_OID = ogr.FieldDefn("OID", ogr.OFTInteger)
        field_N   = ogr.FieldDefn( "N" , ogr.OFTInteger)
         
        layer.CreateField(field_OID)
        layer.CreateField(field_N)
        feature.SetField("OID" ,  OID )
        feature.SetField( "N"  ,   i  )
        
        layer.CreateFeature(feature)
        
        feature.Destroy()
        source.Destroy()        
# ##########################################   


def CreateSingleton(inFeature, tupleOidN ):
    outdriver = ogr.GetDriverByName("ESRI Shapefile")
    OID, N = tupleOidN
    
    newFolder =  r"Z:\\plot"+str(OID)
    try:
        os.mkdir( newFolder )
    except:
        pass
    
    outSHPPath = newFolder+"plot"+str(OID)+"_"+str(N)+".shp"
    
    if os.path.exists(outSHPPath):
        outdriver.DeleteDataSource(outSHPPath)
        
    source = outdriver.CreateDataSource(outSHPPath)

    layer = source.CreateLayer("Buffers", geom_type = ogr.wkbPolygon)
    
    #field_OID = ogr.FieldDefn("OID", ogr.OFTInteger)
    #field_N   = ogr.FieldDefn( "N" , ogr.OFTInteger)
     
    #layer.CreateField(field_OID)
    #layer.CreateField(field_N)
    #feature.SetField("OID" ,  OID )
    #feature.SetField( "N"  ,   i  )
    
    layer.CreateFeature(feature)
    
    feature.Destroy()
    source.Destroy()
    

    
    
    
    
    #################################
    

    cmdSrc = dictCommands["clippoly"]+" /multifile /verbose "+outSHPPath+" "+newFolder+r"\\output "+clippedBlock
    print "--->"+cmdSrc
    print run_and_return(cmdSrc)

    if os.path.isfile( "Z:\\output"+str(OID)+".csv" ): os.remove("Z:\\output"+str(OID)+".csv")

    cmdSrc = dictCommands["cloudmetrics"]+r" Z:\\output"+str(OID)+".lda Z:\\output"+str(OID)+".csv"
    print run_and_return(cmdSrc)
 
    f = open("Z:\\output"+str(OID)+".csv", "r")
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
            print listLine
        elif k > 1:
            listLine = lines.split(",")
            listLines.append(listLine)
            print listLine
            
    return listLines
