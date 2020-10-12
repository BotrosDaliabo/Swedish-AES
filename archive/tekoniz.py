import textract
import os
from nltk.tokenize import word_tokenize
from os import path
from pathlib import Path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO

#en funktion som läser pdf och returnerar innehåll som text. Hämtad från Stackoverflow länk: https://stackoverflow.com/questions/48749789/reading-pdf-using-pypdf2-with-polish-characters
def pdf_to_text(pdfname):
    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    device = TextConverter(rsrcmgr, sio, codec='utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
      # get text from file
    fp = open(pdfname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()
      # Get text from StringIO
    text = sio.getvalue()
      # close objects
    device.close()
    sio.close()

    return text

#skapar en katalog som innehåller tokeniserad text om den inte existerar
tokenizedDirectory = 'tokenized'

if not path.exists(tokenizedDirectory):
    os.mkdir(tokenizedDirectory)

#tekoniserar filer i unprocessed-katalogen och sparar tekoniserad text i en textfil
directory = Path("unprocessed")
for filename in os.listdir(directory):
        f = open(tokenizedDirectory +"/"+ os.path.splitext(filename)[0] + ".txt", "w+")
        filePath1 = "unprocessed/"+filename
        if filename.endswith(".PDF"):
            f.write(str(word_tokenize(pdf_to_text(filePath1))))
        else:
            f.write(str(word_tokenize(textract.process(filePath1).decode('ISO-8859-1'))))
