import requests
from bs4 import BeautifulSoup
import re
import time
import json

from textScrapeFuncs import *

yearsList = range(2023,2025)#range(1987,2025)
yearStrList = [str(x) for x in yearsList]
url = 'https://papers.nips.cc'
paperPath = '/paper_files/paper/'

dataDict = {}
failList = []
# counts of "visualization" and "IEEE Transactions on Visualization and Computer Graphics" in the fullText
visualizationCount = 0
ieeeCount = 0

for yearStr in yearStrList:
    dataDict[yearStr] = []
    
    requestBool = True
    while requestBool:
        try:
            output = requests.get(url+paperPath+yearStr)
            statusCode = output.status_code
        except:
            statusCode = 429

        if statusCode == 200:
            requestBool = False
        elif statusCode == 429:
            time.sleep(60)
        else:
            print('Failed to get '+str(yearStr)+' year info!')
            requestBool = False

    if not requestBool:
        soup = BeautifulSoup(output.text)
        for link in soup.findAll('a'):
            paredPath = link.get('href').split('/')
            print(paredPath)
            if len(paredPath) > 1:
                if paredPath[1] == 'paper_files':
                    fileIDList = paredPath[5].split('-')
                    fileID = fileIDList[0]
                    
                    if len(fileIDList) == 2:
                        fileType = fileIDList[1].split('.')[0]
                    else:
                        fileType = fileIDList[2].split('.')[0]
                    
                    if int(yearStr) <= 2019:
                        fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Metadata.json'
                        
                        requestBool = True
                        while requestBool:
                            try:
                                response = requests.get(fileURL)
                                statusCode = response.status_code
                            except:                                
                                statusCode = 429
                    
                            if statusCode == 200:
                                requestBool = False
                            elif statusCode == 429:
                                time.sleep(60)
                            else:
                                print('Failed to get '+fileID+' metadata!')
                                requestBool = False
                        
                        if not requestBool:
                            data = response.json()
                            print(data.keys())
                            
                            abstract = data['abstract']
                            fullText = data['full_text']
                            if (abstract is not None)&(fullText is not None):
                                print(len(fullText.split('References\n')))
                                print(len(fullText.split('Acknowledgements\n')))
                                if len(fullText.split('References\n')) == 2:
                                    mainText = fullText.split('References\n')[0]
                                    refText = fullText.split('References\n')[1]

                                    # search a "visualization" in the fullText
                                    visualizationExists = re.search(r'visualization', fullText, re.IGNORECASE)
                                    if visualizationExists:
                                        print('visualization found!')
                                        visualizationCount += 1
                                        # skip this paper if "visualization" is already found
                                        continue

                                    # search a "IEEE Transactions on Visualization and Computer Graphics" in the fullText
                                    ieeeExists = re.search(r'IEEE Transactions on Visualization and Computer Graphics', fullText, re.IGNORECASE)
                                    if ieeeExists:
                                        print('IEEE Transactions on Visualization and Computer Graphics found!')
                                        ieeeCount += 1
                                        # skip this paper if "IEEE Transactions on Visualization and Computer Graphics" is already found
                                        continue
                                
                                    abstractWords = re.findall(r'[^\W_]+',
                                                               abstract,
                                                               re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                    print(len(abstractWords))
                                    mainTextWords = re.findall(r'[^\W_]+',
                                                               mainText,
                                                               re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                    print(len(mainTextWords))
                                    refTextNums = re.findall(r'\[[0-9]+\]',
                                                             refText)
                                    print(len(refTextNums),maxRefNumFunc(refTextNums))
                                    dataDict[yearStr].append({'abstract':abstract,
                                                              'fullText':fullText,
                                                              'fileID':fileID,
                                                              'refCount':[len(refTextNums),maxRefNumFunc(refTextNums)],
                                                              'wordCount':len(abstractWords)+len(mainTextWords)})
                                elif len(fullText.split('Acknowledgements\n')) == 2:
                                    mainText = fullText.split('Acknowledgements\n')[0]
                                    refText = fullText.split('Acknowledgements\n')[1]

                                    abstractWords = re.findall(r'[^\W_]+',
                                                               abstract,
                                                               re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                    print(len(abstractWords))
                                    mainTextWords = re.findall(r'[^\W_]+',
                                                               mainText,
                                                               re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                    print(len(mainTextWords))
                                    refTextNums = re.findall(r'\[[0-9]+\]',
                                                             refText)
                                    print(len(refTextNums),maxRefNumFunc(refTextNums))
                                    dataDict[yearStr].append({'abstract':abstract,
                                                              'fullText':fullText,
                                                              'fileID':fileID,
                                                              'refCount':[len(refTextNums),maxRefNumFunc(refTextNums)],
                                                              'wordCount':len(abstractWords)+len(mainTextWords),
                                                              'visualization': visualizationExists,
                                                              'ieee': ieeeExists})
                                else:
                                    print('pdfx now used...')
                                    try:
                                        fullText = pdfxFunc(fileType,
                                                            url,
                                                            paperPath,
                                                            yearStr,
                                                            fileID)
                                        if fullText is not None:
                                            splitOnIntro = fullText.split('\nIntroduction\n') 
                                            abstract = splitOnIntro[0].split('\nAbstract\n')[1]
                                            mainText = splitOnIntro[1].split('References\n')[0]
                                            refText = splitOnIntro[1].split('References\n')[1]

                                            # search a "visualization" in the fullText
                                            visualizationExists = re.search(r'visualization', fullText, re.IGNORECASE)
                                            if visualizationExists:
                                                print('visualization found!')
                                                visualizationCount += 1
                                                # skip this paper if "visualization" is already found
                                                continue

                                            # search a "IEEE Transactions on Visualization and Computer Graphics" in the fullText
                                            ieeeExists = re.search(r'IEEE Transactions on Visualization and Computer Graphics', fullText, re.IGNORECASE)
                                            if ieeeExists:
                                                print('IEEE Transactions on Visualization and Computer Graphics found!')
                                                ieeeCount += 1
                                                # skip this paper if "IEEE Transactions on Visualization and Computer Graphics" is already found
                                                continue

                                            abstractWords = re.findall(r'[^\W_]+',
                                                                       abstract,
                                                                       re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                            print(len(abstractWords))
                                            mainTextWords = re.findall(r'[^\W_]+',
                                                                       mainText,
                                                                       re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                            print(len(mainTextWords))
                                            refTextNums = re.findall(r'\[[0-9]+\]',
                                                                     refText)
                                            print(len(refTextNums),maxRefNumFunc(refTextNums))

                                            dataDict[yearStr].append({'abstract':abstract,
                                                                      'fullText':fullText,
                                                                      'fileID':fileID,
                                                                      'refCount':[len(refTextNums),maxRefNumFunc(refTextNums)],
                                                                      'wordCount':len(abstractWords)+len(mainTextWords),
                                                                      'visualization': visualizationExists,
                                                                      'ieee': ieeeExists})
                                    except:
                                        if fileType == 'Abstract':
                                            fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper.pdf'
                                        elif fileType == 'Conference':
                                            fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper-Conference.pdf'
                                        else:
                                            fileURL = ''
                                        
                                        failList.append(fileURL)
                        else:
                            failList.append(fileURL)
                    else:
                        try:
                            fullText = pdfxFunc(fileType,
                                                url,
                                                paperPath,
                                                yearStr,
                                                fileID)
                            if fullText is not None:
                                splitOnIntro = fullText.split('\nIntroduction\n') 
                                abstract = splitOnIntro[0].split('\nAbstract\n')[1]
                                mainText = splitOnIntro[1].split('References\n')[0]
                                refText = splitOnIntro[1].split('References\n')[1]

                                # search a "visualization" in the fullText
                                visualizationExists = re.search(r'visualization', fullText, re.IGNORECASE)
                                if visualizationExists:
                                    print('visualization found!')
                                    visualizationCount += 1
                                    # skip this paper if "visualization" is already found
                                    continue

                                # search a "IEEE Transactions on Visualization and Computer Graphics" in the fullText
                                ieeeExists = re.search(r'IEEE Transactions on Visualization and Computer Graphics', fullText, re.IGNORECASE)
                                if ieeeExists:
                                    print('IEEE Transactions on Visualization and Computer Graphics found!')
                                    ieeeCount += 1
                                    # skip this paper if "IEEE Transactions on Visualization and Computer Graphics" is already found
                                    continue
                                
                                abstractWords = re.findall(r'[^\W_]+',
                                                           abstract,
                                                           re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                print(len(abstractWords))
                                mainTextWords = re.findall(r'[^\W_]+',
                                                           mainText,
                                                           re.MULTILINE) # regex demo and explanation - https://regex101.com/r/U7WMSA/1
                                print(len(mainTextWords))
                                refTextNums = re.findall(r'\[[0-9]+\]',
                                                         refText)
                                print(len(refTextNums),maxRefNumFunc(refTextNums))

                                dataDict[yearStr].append({'abstract':abstract,
                                                          'fullText':fullText,
                                                          'fileID':fileID,
                                                          'refCount':[len(refTextNums),maxRefNumFunc(refTextNums)],
                                                          'wordCount':len(abstractWords)+len(mainTextWords),
                                                          'visualization': visualizationExists,
                                                          'ieee': ieeeExists})
                        except:
                            if fileType == 'Abstract':
                                fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper.pdf'
                            elif fileType == 'Conference':
                                fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper-Conference.pdf'
                            else:
                                fileURL = ''
                            
                            failList.append(fileURL)
        
    with open('neuripsWord+RefCount.json', 'w') as f:
        json.dump(dataDict,f)

with open('neuripsWord+RefCount.json', 'w') as f:
    json.dump(dataDict,f)

failDict = {}
for url in failList:
    urlList = url.split('/')
    year = urlList[5]
    
    if year in failDict.keys():
        failDict[year] += 1
    else:
        failDict[year] = 1

neuripsFailDict = {'counts':failDict,
                   'urls':failList}

with open('neuripsFailURLs.json', 'w') as f:
    json.dump(neuripsFailDict,f)

neuripsCountDict = {'visualization':visualizationCount,
                    'ieee':ieeeCount}
with open('neuripsCounts.json', 'w') as f:
    json.dump(neuripsCountDict,f)
