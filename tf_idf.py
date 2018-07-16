# -*- coding: utf-8 -*-
"""
Created on Sat Jul 14 19:07:35 2018

@author: Saurish
"""

from nltk.tokenize import sent_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
import operator
import re
import csv
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

#Convers PDF to text (Returns text)
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text 



filename ="JavaBasics-notes.pdf"
#file = open(filename,'rb')
#pdf_reader = PyPDF2.PdfFileReader(file)
#text = ""
#for i in range(pdf_reader.numPages):
#    text+=pdf_reader.getPage(i).extractText()
#text = text.lower()
text = convert(filename)

#Removing code present in the text
temp = list(text)
text = ""
symbols = ['[',']','(',')','{','}']
for c in temp:
    if len(symbols)==6:
       if c in ['{','(','[']: symbols.remove(c)
       else : text += c
    else : 
        if c == ']' and '[' not in symbols: symbols.append('[')
        elif c == ')' and '(' not in symbols: symbols.append('(')
        elif c == '}' and '{' not in symbols: symbols.append('{')
        else : continue

para_tokenizer = RegexpTokenizer('\n')
sent_token = [text]#sent_tokenize(text)
tokenizer = RegexpTokenizer(r'\w+')
lemmatizer = WordNetLemmatizer()
stwords = set(stopwords.words('english'))
stwords = list(stwords)
#stwords.append("new")

#preparing data
data = []
unique_words =  set()
word_dict = []
tfDict = []
for line in sent_token:
    word_token = tokenizer.tokenize(line)
    filtered_words = [lemmatizer.lemmatize(re.sub("[0-9]","",w)) for w in word_token if not w.lower() in stwords]
    for i in range(len(filtered_words)):
        if len(filtered_words[i])==1:
            filtered_words[i] = re.sub("[a-z]","",filtered_words[i])
    while '' in filtered_words:
            filtered_words.remove('')
    filtered_words = [w.lower() for w in filtered_words]
    for word in stwords:
        if word in filtered_words:
            filtered_words.remove(word)
    data.append(filtered_words)
    unique_words = unique_words.union(set(filtered_words))
    word_dict.append({w:0 for w in filtered_words})

#counting Data
for i in range(len(data)):
    for word in data[i]:
        word_dict[i][word]+=1
    #Normalizing
    tfDict.append({w:word_dict[i][w]/len(data[i]) for w in word_dict[i]})


#Computing IDF
N = len(data)
IDF_dict = {}
for word in unique_words:
    n = 1
    for lis in word_dict:
        try:
            n+=lis[word]
        except:
            pass
    IDF_dict.update({word:N/n})
    
#Computing TF-IDF
tf_idf = []
for line in tfDict:
    tf_idf.append({w:line[w]*IDF_dict[w] for w in line})
dataframe = pd.DataFrame([dic for dic in tf_idf]).fillna(0) 


#Combining scores of keywords
score = {w:0 for w in unique_words}
for w in unique_words:
    for line in tf_idf:
        if w in line:
            score[w]+=line[w]
#sorting             
score = sorted(score.items(),key = operator.itemgetter(1))
    
#Writing to csv        
with open('outputMain.csv','a') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Keyword','Score'])
    for row in reversed(score):
        print(row)
        writer.writerow(list(row))
        

