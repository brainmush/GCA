import argparse
import os
import re

from bs4 import BeautifulSoup
from flask import Flask
from pywebio import STATIC_PATH, start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.flask import webio_view
from pywebio.session import run_js
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )


# %%
def get_webpage(gene):
    try:

        o = driver.get("https://www.genecards.org/cgi-bin/carddisp.pl?gene="+str(gene))
        content = driver.page_source
        soup = BeautifulSoup(content,"lxml")
        r = driver.current_url 

        
        for a in soup.find('span', attrs={'class':'aliasMainName'}):
            gene_aliases.append(a.text)
 
        
        for a in soup.find_all('span', itemprop = 'alternateName'):
            gene_aliases.append(a.text)
        
        for i in range(len(gene_aliases)):
            gene_aliases[i] = gene_aliases[i].upper()

        for a in soup.find_all('span', attrs={'class':'aliasMainName'}):
            gene_description.append(a.text)

        for a in soup.find_all('span', itemprop = 'description'):
            gene_description.append(a.text)

        if str(gene.upper()) not in str(r.upper()):
            put_text("I did not find what you were looking for, but here are the results for " + str(gene_aliases[0])).style('color: purple; font-size: 30px')
            put_text('Please double-check the name of the gene that you are looking for!').style('color: purple; font-size: 30px')
    except Exception as e: 
        put_text("Wrong gene name").style('color: red; font-size: 30px')
        put_button("New gene",onclick=lambda: run_js('window.location.reload()'))
        raise
    put_text("Got the website")
   
def clear(lista):
    lista.clear()

def process_aliases(gene_aliases):
      
    for j in gene_aliases:
        if bool(re.search(r'\d', j)) == True:
            j1 = re.sub("[A-Z]+", lambda ele: "" + ele[0] + "_",j)
        else:
            j1=j
        j1=j1.replace("-", "_")
        j1=j1.replace("/", "_")
        j1=j1.replace("__", "_")
        #replacing I with  [L, i]
        j1=j1.replace("I", "[i,L]")
        #replacing o and zero with 0,o
        j1=j1.replace("O", "%")
        j1=j1.replace("0", "%")
        j1=j1.replace("%", "[0,o]")
        #replacing 1 with [1, L, i]
        j1=j1.replace("1", "[1,L,i]")
        if j1[-1] == '_':
            j1 = j1[:-1]
        else:
            j1 = j1
        marker_aliases.append(j1)
    put_text("Done with aliases")


gene_aliases = []
marker_aliases = []
gene_description = []

app = Flask(__name__)


@app.route("/")

def appy():

    put_markdown('## GeneCard alias generator v1.3')
    gene = input("GeneCards name", type=TEXT, required = True)
    put_text("Please wait")

    get_webpage(gene)
    
    process_aliases(gene_aliases)

    res = [i for n, i in enumerate(marker_aliases) if i not in marker_aliases[:n]]
    put_success("Done")
    put_text(str(gene_aliases[0]) + " aliases:").style('color: black; font-size: 20px')
    put_text(*gene_aliases, sep =', ')
    put_text(' ').style('color: black; font-size: 10px')
    put_text("Markers:").style('color: black; font-size: 20px')
    put_text(*res, sep =', ')
    put_text(' ').style('color: black; font-size: 10px')
    put_text("Gene description:").style('color: black; font-size: 20px')
    put_text(*gene_description[1:], sep =', ')
    put_text(' ').style('color: black; font-size: 10px')
    put_button("New gene",onclick=lambda: run_js('window.location.reload()'))
    put_button("Link to GC",color='info', onclick=lambda: run_js('window.open(r)', r = "https://www.genecards.org/cgi-bin/carddisp.pl?gene=" +str(gene)))
    put_info('v1.1 : added to the markers potential OCR errors for numbers 0 and 1 \nv1.2 : added gene description and some extra buttons\nv1.3 : added to the markers potential OCR errors for letters l and I')
    clear(gene_aliases)
    clear(marker_aliases)
    clear(gene_description)
    
# main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(appy, port=args.port)
