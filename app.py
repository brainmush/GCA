
import os
import re
import time

from bs4 import BeautifulSoup
from flask import Flask
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

# %%
def get_webpage(gene):
    try:
        put_processbar('bar', auto_close=True)
        for i in range(1, 11):
            set_processbar('bar', i / 10)
            time.sleep(0.1)
    
        o = driver.get("https://www.genecards.org/cgi-bin/carddisp.pl?gene="+str(gene))
        content = driver.page_source
        soup = BeautifulSoup(content)
        r = driver.current_url 

        
        for a in soup.find('span', attrs={'class':'aliasMainName'}):
            gene_aliases.append(a.text)
 
        
        for a in soup.find_all('span', itemprop = 'alternateName'):
            gene_aliases.append(a.text)
        
        for i in range(len(gene_aliases)):
            gene_aliases[i] = gene_aliases[i].upper()
            
        if str(gene.upper()) not in str(r.upper()):
            put_text("I did not find what you were looking for, but here are results for " + str(gene_aliases[0])).style('color: purple; font-size: 30px')
            
    except Exception as e: 
        put_text("Wrong gene name").style('color: red; font-size: 30px')
        raise
   
def clear(lista):
    lista.clear()

def process_aliases(gene_aliases):
    put_processbar('bar', auto_close=True)
    for i in range(1, 11):
        set_processbar('bar', i / 10)
        time.sleep(0.1)
        
    for j in gene_aliases:
        if bool(re.search(r'\d', j)) == True:
            j1 = re.sub("[A-Z]+", lambda ele: "" + ele[0] + "_",j)
        else:
            j1=j
        j1=j1.replace("-", "_")
        j1=j1.replace("__", "_")
        if j1[-1] == '_':
            j1 = j1[:-1]
        else:
            j1
        marker_aliases.append(j1)


gene_aliases = []
marker_aliases = []


app = Flask(__name__)



@app.route("/")
def app():

    put_markdown('## GeneCard alias generator')
    #put_text("Please enter the gene name:")
    gene = input("GeneCards name", type=TEXT, required = True)
    
    put_processbar('bar', auto_close=True)
    for i in range(1, 11):
        set_processbar('bar', i / 10)
        time.sleep(0.1)
        
    get_webpage(gene)
    
    process_aliases(gene_aliases)

    marker_aliases2 = list(set(marker_aliases))
    res = [i for n, i in enumerate(marker_aliases) if i not in marker_aliases[:n]]
    put_success("Done")
    put_text(str(gene_aliases[0]) + " aliases:").style('color: black; font-size: 20px')
    put_text(*gene_aliases, sep =', ')
    put_text("Markers:").style('color: black; font-size: 20px')
    put_text(*res, sep =', ')
    clear(gene_aliases)
    clear(marker_aliases)
    #clear(gene)

# main function
if __name__ == '__main__':
	start_server(app)


