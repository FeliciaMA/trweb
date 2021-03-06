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

preSql = "UPDATE tr_report_semi SET "

newNum = 0

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
                    continue
                if cnt == 2:
                    continue
                else:
                    uKey = str(ric) + "-" + str(rowArr[7].split(" ")[0])
                    if uKey not in uKeyRec:
                        uKeyRec[uKey] = 1
                        # for one common row
                        valDict = {}
                        if rowArr[7] == "":
                            continue
                        try:
                            tmpTS = time.strftime("%Y-%m-%d",time.strptime(rowArr[7].split(" ")[0],"%m/%d/%Y"))
                        except Exception as e:
                            print str(e)
                            print rowArr[3]
                            print filePath
                            exit()

                        
                        val1 = cell2val(rowArr[8],outOfRangeLog)
                        val2 = cell2val(rowArr[9],outOfRangeLog)
                        
                        if val1 == "NULL" and val2 == "NULL":
                            continue
                         
                        querySql = "SELECT ric FROM tr_report_semi WHERE ric = '" + str(ric) + "' AND ts = '" + str(tmpTS) + "'"
                        exist = cur.execute(querySql)
                        if exist == 0:
                            continue
                        
                        sql = preSql
                        sql += " sga_exp_tot = " + str(val1) + ", netinc_inextra_bedist = " + str(val2) + " WHERE ric = '" + str(ric) + "' AND ts = '" + str(tmpTS) + "'"
                        try:
                            cur.execute(sql)
                            conn.commit()
                            newNum += 1
                        except Exception as e:
                            errLog.write(sql+"\n"+str(e)+"\n")
                                
        if totNum % 1000 == 0:
            print "Time:" + str(time.clock()) + ", Finish handling " + str(totNum) + ", newNum:" + str(newNum)

        
        
        
        
        
        