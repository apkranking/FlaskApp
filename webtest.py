#libraries for Webdriver that require to crawl the web page
from __future__ import print_function
from werkzeug import secure_filename
from bs4 import BeautifulSoup
import time
import os
import urllib
#import input
from subprocess import call
import shutil
import sys, io

import sys
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

#library for regualr expression
import re

#library for web app developement - Flask
from jinja2 import Template
from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__, static_folder='analysisReport')
UPLOAD_FOLDER = '/home/mitu/Downloads/pythonWeb-Flask/apkFiles'
ALLOWED_EXTENSIONS = set(['apk', 'xapk'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    with open('prototype.html.jinja') as f:
        tmpl = Template(f.read())
    return tmpl.render()



@app.route("/apkCrawler", methods=['GET', 'POST'])
def apkCrawler(pckgName):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    chromedriver_loc = "/home/mitu/Downloads/pythonWeb-Flask/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver_loc
    
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("prefs", {
        "download.default_directory": "/home/mitu/Downloads/pythonWeb-Flask/downloadedApks",
        "download.prompt_for_download": False,
    })
    
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(executable_path=chromedriver_loc, chrome_options=options)
    #driver = webdriver.Chrome(executable_path=chromedriver_loc)
    wait = WebDriverWait( driver, 10 )

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': "/home/mitu/Downloads/pythonWeb-Flask/downloadedApks"}}
    command_result = driver.execute("send_command", params)
    
    driver.get('https://m.apkpure.com/search')

    sbox = driver.find_element_by_xpath('//*[@id="so"]/div/div[2]/input')
    sbox.send_keys(pckgName)

    submit = driver.find_element_by_xpath('//*[@id="so"]/div/div[4]')
    submit.click()
    time.sleep(5)
    appLocation = driver.find_element_by_xpath('//*[@id="search-res"]/li[1]/dl/a/div[2]')
    appLocation.click()
    time.sleep(5)
    try:
        download = driver.find_element_by_xpath('//*[@id="down_btns"]/div/a[1]')
    except Exception:
        download = driver.find_element_by_xpath('//*[@id="down_btns"]/a')
    download.click()
    time.sleep(10)
    driver.quit()


@app.route("/dex2jar", methods=['GET', 'POST'])
def dex2jar(apkName, pckgName):
    
    inputFilename = apkName
    outputFilename = pckgName + '.jar'
    try:
        absInputpath = "/home/mitu/Downloads/pythonWeb-Flask/apkFiles/"
        absOutputPath = "/home/mitu/Downloads/pythonWeb-Flask/bytecodes/"
        InputPath = absInputpath + inputFilename
        OutputPath =  absOutputPath + outputFilename
        #print(InputPath)
        #print(OutputPath)
        if(os.path.exists(InputPath)):
            call(['sh', '/home/mitu/Downloads/finalizeCode-INTERNAL-EVIDENCES/allAlgoIn1platform/dex2jar/d2j-dex2jar.sh', '-f', InputPath, '-o', OutputPath])
    except Exception:
        print("Exception!!")
        

@app.route("/runFindbugs", methods=['GET', 'POST'])
def runFindbugs(pckgName):
    inputFilename = pckgName +'.jar'
    outputFilename = pckgName + '.xml'
    try:
        absInputpath = "/home/mitu/Downloads/pythonWeb-Flask/bytecodes/"
        absOutputPath = "/home/mitu/Downloads/pythonWeb-Flask/analysisReport/"
        InputPath = absInputpath + inputFilename
        OutputPath =  absOutputPath + outputFilename
        #print(InputPath)
        #print(OutputPath)
        if(os.path.exists(InputPath)):
            call(['/home/mitu/Downloads/findbugs-3.0.1/bin/./findbugs', '-low', '-xml', '-output', OutputPath, InputPath])
    except Exception:
        print("Exception!!")


@app.route("/parseAnalysisReport", methods=['GET', 'POST'])
def parseAnalysisReport(pckgName):
    myFile2 = open('inputMultiAppData.txt', 'w')
    try:
        inputFilename = pckgName + '.xml'
        absInputPath = "/home/mitu/Downloads/pythonWeb-Flask/analysisReport/"
        InputPath = absInputPath + inputFilename
        root = ET.parse(InputPath)
        bugInstances = root.findall('.//BugInstance')

        a = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
        for bug in bugInstances:
            i = int(bug.attrib['priority'])
            j = int(bug.attrib['rank'])
            #print(i,j)
            #print(a[i-1][j-1])
            a[i-1][j-1] = a[i-1][j-1] + 1
        #print(a)

        for j in xrange(0, 20):
            sum = 0
            for i in xrange(0, 3):
                sum = sum + a[i][j]
                myFile2.write(str(a[i][j]))
                myFile2.write("\t")
            myFile2.write("\n")
                
            #print(i+1, sum)
        myFile2.cloes()
    except:
        time.sleep(1)



def freopen(f,option,stream):
    oldf = open(f,option)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)

def calc_b(k, alpha, beta, upre, u, bpre, b):
    return float (((k - (upre*u)) * ((alpha * bpre * u) + (beta * b * upre))/(k * ((alpha * u) + (beta * upre) - ((alpha + beta)*(upre*u))))))

def calc_d(k, alpha, beta, upre, u, dpre, d):
    return float (((k - upre*u) * ((alpha * dpre * u) + (beta * d * upre))/(k * ((alpha * u) + (beta * upre) - ((alpha + beta)*(upre*u))))))

def calc_u(k, upre, u):
    return float((upre * u ) / k)

def calc_weight(alpha, beta, upre, u):
    return float(((alpha*(u- (upre*u))) + (beta*(upre- (upre*u))))/((upre + u) - 2* (upre * u)))   

def raw_input():
    return input()

@app.route("/trustTuppleCalc", methods=['GET', 'POST'])
def trustTuppleCalc(pckgName):
    f = open("inputMultiAppData.txt","r")
    freopen("InputDataForOrder.txt","w",sys.stdout)

    high = []
    medium = []
    low = []

    for line in f:
        try:
            #line = raw_input()
            high.append(float(line.split("	")[0]))
            medium.append(float(line.split("	")[1]))
            low.append(float(line.split("	")[2])*2)
        except EOFError:
            break

    n = 2
    b = []
    d = []
    u = []

    for i1 in range (0, len(high)):
        #app.logger.warning("\n\nIm here ......\n\n")
        #print('This is standard output', file=sys.stderr)
        if (high[i1] + medium[i1] + low[i1]) == 0:
            b.append(0.95)
            d.append(0.01)
            u.append(0.04)
        else:
            m1 = float(medium[i1] / 2)
            size = high[i1] + medium[i1] + low[i1] + n
            b.append(float((low[i1] + m1 ) / size))
            d.append(float((high[i1] + m1 ) / size))
            u.append(float(n / size))
        #print ("%0.2f %0.2f %0.2f" % (b[i], d[i], u[i]), file=sys.stderr)
        
    """
    Individual B, D, U create ends here
    """

    """
    aggregate B, D, U into single B,D,U starts here
    """
    alpha = 0
    beta = 0
    weight = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    #weight = [5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1]

    b_aggregate = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    d_aggregate = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    u_aggregate = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    temp_index = 0
    
    #print("line 236", file=sys.stderr)
    for appNum in range(0, len(b)):
        b_aggregate[temp_index] = b[appNum]
        d_aggregate[temp_index] = d[appNum]
        u_aggregate[temp_index] = u[appNum]
    
        temp_index = temp_index + 1
    
        if temp_index % 20 == 0:
            #print("line 242", file=sys.stderr)
            N = len(b_aggregate)
            #print "N = ", N
            for j in range(0, 5):
                l = 1
                for i in range(1, N, 2):
                    alpha = weight [i-1]
                    beta = weight [i]
                    sum_u = u_aggregate[i] + u_aggregate[i-1]
                    mul_u = u_aggregate[i] * u_aggregate[i-1]
                    k = sum_u - mul_u

                    temp = i
                    temp = temp - l

                    b_aggregate[temp] = calc_b(k, alpha, beta, u_aggregate[i-1], u_aggregate[i], b_aggregate[i-1], b_aggregate[i])
                    d_aggregate[temp] = calc_d(k, alpha, beta, u_aggregate[i-1], u_aggregate[i], d_aggregate[i-1], d_aggregate[i])
                    
                    weight [temp] = calc_weight(alpha, beta, u_aggregate[i-1], u_aggregate[i])
                    u_aggregate[temp] = calc_u(k, u_aggregate[i-1], u_aggregate[i])

                    l = l + 1
                #print("line 263", file=sys.stderr)
                if N % 2 ==0:
                    N = N /2
                else:
                    if N != 1:
                        N = N / 2 + 1

            #print "%0.2f %0.2f %0.2f" % (b_aggregate[i-1], d_aggregate[i-1], u_aggregate[i-1]) 
            print ("%0.2f %0.2f %0.2f" % (b_aggregate[i-1], d_aggregate[i-1], u_aggregate[i-1]), file=sys.stderr)
            temp_index = 0
        
    
    return b_aggregate[i-1], d_aggregate[i-1], u_aggregate[i-1]
        
@app.route("/extractReview", methods=['GET', 'POST'])
def extractReview(pckgName):
    #print(pckgName, file=sys.stderr)
    #app.logger.warning(pckgName)
    return "Check your console"

@app.route("/urlInsert", methods=['GET', 'POST'])
def urlInsert():
    appurl = request.args.get('appurl')

    if (appurl == ""):
        f = request.files.get('file')
    
        f.save(secure_filename(f.filename))
        #f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        #return redirect(url_for('uploaded_file', filename=filename))
        #pckgName = fname
    else:
        pckg = re.search('(?<=[?&]id=)[^&]+', appurl)
        pckgName = pckg.group(0)

    ''''----Internal Evidence Collection-------------'''
    apkCrawler(pckgName) #1 - Download apk file
    
    dirpath = '/home/mitu/Downloads/pythonWeb-Flask/apkFiles/'
    downloadDirPath = '/home/mitu/Downloads/pythonWeb-Flask/downloadedApks/'
    filename = os.listdir(downloadDirPath)[0]
    
    new_file = pckgName
    old_file = os.path.join(downloadDirPath, filename)
    if filename.endswith('.apk'):
        apkName = pckgName+".apk"
        new_file = os.path.join(dirpath, apkName)
    elif filename.endswith('.xapk'):
        apkName = pckgName+".xapk"
        new_file = os.path.join(dirpath, apkName)
    os.rename(old_file, new_file) 
    
    dex2jar(apkName, pckgName) #2 - Preprocess the apk file to bytecode
    runFindbugs(pckgName) #3 - run static analysis tool ; generate internal evidance
    parseAnalysisReport(pckgName) #4
    its = trustTuppleCalc(pckgName) #5 - will return internal evidance based trust score
    rating = ((its[0] + its[2]) / (its[0] + its[1] + 2 * its[2]))*5
    #print(its,file=sys.stderr)
    
    ''''----External Evidence Collection-------------'''
    ets = extractReview(pckgName) #extract reviews from google play store

    return "<html> <head> <title>APK Preprocessing</title></head> <body> <a  href='http://127.0.0.1:5000/'> Submit new job </a> <p>Download APK file from APKPure --- Done <br> Convert to bytecode --- Done <br> Static Analysis --- Done </p> <br> <br> <a href='/analysisReport/"+pckgName+".xml'>See the bug warning report (generated by FindBugs)</a> <br> <br><p>App package Name : "+pckgName+"<br><br>Internal evidance based Trust Score (B, D, U) = "+str(its)+"<br><br>Internal evidance based Rating (out of 5) = "+str(rating)+" </p></body> </html>"

    
if __name__ == "__main__":
    #app.static_folder = 'static'
    app.run(host="127.0.0.1", port =5000, debug=True)

