# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 15:09:22 2018

@author: Saurish
"""
import re
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import operator
from nltk.stem import WordNetLemmatizer,PorterStemmer
import string
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import csv 

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
   


filename = "JavaBasics-notes.pdf"
#file = open(filename,'rb')
#pdf_reader = pdf.PdfFileReader(file)
#text = ""
#for i in range(pdf_reader.numPages):
#    text= text + pdf_reader.getPage(i).extractText()+" "

#removing code
text = convert(filename)
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

#Constructing Phrases
phrases = set(text.split("\n"))
punct = ['.','?',',','!']
for c in punct:
    text = text.replace(c," % ")
punct = list(string.punctuation)
for c in punct:
    if c=='%': continue
    else: text = text.replace(c,"")
stopset = set(stopwords.words('english'))
for w in stopset:
    text = text.replace(" "+w+" "," % ")
    w=list(w)
    w[0]= w[0].capitalize()
    w = "".join(str(x) for x in w)
    text = text.replace(" "+w+" "," % ")

text = re.sub(r'[0-9]',"",text)

#Setting Up lemmatizer
lemmatizer = WordNetLemmatizer()

#split all words
tokenizer = RegexpTokenizer(r'\w+')
keywords = tokenizer.tokenize(text)

phrases = list(phrases)

#Lemmatizing candidate keywords
keywords = [lemmatizer.lemmatize(w) for w in keywords ]

#transforming to lowercase
phrases = [re.sub("[0-9]","",s.lower()) for s in phrases]
keywords = [re.sub("[0-9]","",w.lower()) for w in keywords ]

for word in stopset:
    while word in keywords:
        keywords.remove(word)
#Sanitizing data        
#for w in keywords:
#    if len(w)<=1:
#        keywords.remove(w)

#Removing Outlier(Possibly joint words) 
tlen = 0
for word in keywords:
    tlen += len(word)
mean_len = tlen/len(keywords)
tdev = 0
for word in keywords:
    tdev+= abs(mean_len-len(word))
mean_dev = tdev/len(keywords)
lower_limit = max(1,mean_len-3*mean_dev)
upper_limit = mean_len+3*mean_dev

keywords = [w for w in keywords if len(w)>lower_limit and len(w)<=upper_limit]
unique_words = set(keywords)

#frequency dictionary
freq_dict = {w:0 for w in unique_words}
for word in keywords:
    freq_dict[word]+=1

#degree Dictionary
phrases = [w.split() for w in phrases]
for i in range(len(phrases)):
    phrases[i] = [lemmatizer.lemmatize(w) for w in phrases[i]]
    
    
deg_dict = {w:0 for w in unique_words}
for w in deg_dict:
    for line in phrases:
        for word in line:
            deg_dict[w]+=len(line)
#            if word.find(w)>=0:
#                deg_dict[w]+=len(line)
#                break

#calculating word score
word_score = {w:0 for w in unique_words}        
for w in word_score:
    word_score[w] = deg_dict[w]/freq_dict[w]
#sorting word score   
word_score_tuple = sorted(word_score.items(),key = operator.itemgetter(1))

with open('outputRake.csv','a') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Keyword','Score'])
    for row in reversed(word_score_tuple):
        print(row)
        writer.writerow(list(row))

