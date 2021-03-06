# -*- coding: UTF-8 -*-
import MySQLdb,time,os,xlrd,csv,math
from dbsettings import *

# the function to handle excel
def openSH(fName,shName):
    bk = xlrd.open_workbook(fName)
    try:
        sh = bk.sheet_by_name(shName)
        return sh
    except:
        print "no sheet in " + fName + " named " + shName
        return None

print "Start to iterate through excels"
t1 = time.clock()
# the error log
errLog = open("err.log", "w")
outOfRangeLog = open("outofrange.log", "w")
noMatchLog = open("nomatch.log","w")
# the code starts to run from here   
# connect to database
conn = MySQLdb.connect(host=RAW_HOST,user=RAW_USER,passwd=RAW_PASS,db=DB_NAME)
cur = conn.cursor()

yearRepDict = {}
totNum = 0
ricRepeat = 0
ricRepDict = {}
maxVal = 1e24
qFolder = os.listdir(rootDir)

preSql = "INSERT INTO " + str(TB_NAME) + " (ric,ts"
for i in range(1,29):
    preSql += "," + colDict[i]
preSql += ") VALUES('"

for folder in qFolder:
    curDir = os.path.join(rootDir,str(folder))
    docArr = os.listdir(curDir)
    for doc in docArr:
        suf = os.path.splitext(doc)[1]
        if suf.lower() != ".csv":
            continue
        filePath = os.path.join(curDir,doc)
        with open(filePath, 'rb') as csvfile:
            uKeyRec = {}
            fqDict = {}
            extrafqDict = {}
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            cnt = 0
            numCol = 0
            totNum += 1
            for rowArr in spamreader:
                cnt += 1
                # the first row
                if cnt == 1:
                    ric = rowArr[0]
                    if ric in ricRepDict:
                        ricRepeat += 1
                        # this ric has been handled
                        break
                    ricRepDict[ric] = 1  
                    numCol = len(rowArr)
                    continue
                else:
                    uKey = str(ric) + "-" + str(rowArr[1].split(" ")[0])
                    if uKey not in uKeyRec:
                        uKeyRec[uKey] = 1
                        # for one common row
                        if rowArr[1] == "":
                            continue
                        try:
                            tmpTS = time.strftime("%Y-%m-%d",time.strptime(rowArr[1].split(" ")[0],"%m/%d/%Y"))
                        except:
                            print rowArr[1]
                            print filePath
                            exit()
                        """
                        uKey = ric + "-" + str(tmpTS)
                        if uKey in insertRec:
                            continue
                        insertRec[uKey] = 1
                        """
                        valid = 1
                        empty = 1
                        sql = preSql + str(ric) + "','" + str(tmpTS) + "'"
                        for i in range(3,30):
                            try:
                                val = round(float(rowArr[i]),6)
                                # filter out invalid data
                                # nan
                                if math.isnan(val):
                                    val = "NULL"
                                # out of range
                                elif abs(val) > maxVal:
                                    outOfRangeLog.write(sql + "\n" + str(val) + "\n")
                                    valid = 0
                                    break
                                    
                                        
                            except Exception as e:
                                val = "NULL"  
                                
                            if val == "NULL":
                                sql += ",NULL"
                            else:
                                sql += ",'" + str(val) + "'"
                                empty = 0
                                
                        if valid:
                            fqDict[rowArr[2]] = {}
                            fqDict[rowArr[2]]["sql"] = sql
                            fqDict[rowArr[2]]["empty"] = empty
                    
                    # for additional values, exists or nothing
                    valid = 1
                    try:
                        val = round(float(rowArr[31]),6)
                        # filter out invalid data
                        # nan
                        if math.isnan(val):
                            valid = 0
                        # out of range
                        elif abs(val) > maxVal:
                            outOfRangeLog.write(sql + "\n" + str(val) + "\n")
                            valid = 0
                    except Exception as e:
                        valid = 0
                    
                    if valid:
                        extrafqDict[rowArr[30]] = val

            for fq in fqDict:
                # if sql is empty and don't have extra column
                if fqDict[fq]["empty"] and fq not in extrafqDict:
                    continue
                if fq not in extrafqDict:
                    addVal = "NULL"
                else:
                    addVal = extrafqDict[fq]
                sql = fqDict[fq]["sql"] + "," + str(addVal) + ")"
                    
                try:
                    cur.execute(sql)
                    conn.commit()
                except Exception as e:
                    errLog.write(str(e) + "\n" + sql + "\n")
  
        if totNum % 1000 == 0:
            print "Time:" + str(time.clock()) + ", Finish handling " + str(totNum) + ", ric repeat:" + str(ricRepeat)
                
                
                
        
        
        
        
        
        
        