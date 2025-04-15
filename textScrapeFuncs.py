import pdfx
import time

def pdfxFunc(fileType,
             url,
             paperPath,
             yearStr,
             fileID):
    if fileType == 'Abstract':
        fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper.pdf'
    elif fileType == 'Conference':
        fileURL = url+paperPath+yearStr+'/file/'+fileID+'-Paper-Conference.pdf'
    else:
        fileURL = None

    if fileURL is not None:
        failBool = True
        failCount = 0

        while (failBool) & (failCount < 5):
            try:
                pdf = pdfx.PDFx(fileURL)
                failBool = False
            except:
                print('Failed to get pdf!', fileURL)
                failCount += 1
                time.sleep(60)
        
        return pdf.get_text()
        
    else:
        return None

def maxRefNumFunc(refList):
    maxNum = 0
    for ref in refList:
        refNum = int(ref.split('[')[1].split(']')[0])

        if refNum > maxNum:
            maxNum = refNum
    
    return maxNum