''' Articles downloader

This script connects the database hosting articles, it aggregates
them into a list of articles and it writes the list into a .npy file.
The main function takes as an argument the path to where the output articles.npy file
will be stored.

There are two main collections fetched, articles from the fake_sites 
category and from the real_sites category.

In order to run this script crendentials need to be specified in the 
<root dir>/db_credentials.json file
'''
from counter import Counter 
from collections import Counter as CollCount
import nltk
import psycopg2
import numpy as np
from tqdm import tqdm
import json
import pathlib
import sys

with open("../../db_credentials.json")as f:
    cred = f.read()
    try:
        cred = json.loads(cred)
        print(cred)
    except ValueError:
        print("json file with wrong syntax")
        

def dbconnect(dbname=cred["dbname"],
              user=cred["user"], 
              password=cred["password"],
              host=cred["host"],
              port=cred["port"]):
                        
    conn = psycopg2.connect(f"dbname={dbname} \
                            user={user} \
                            password={password} \
                            host={host} \
                            port={port}")
    cur = conn.cursor()
    return cur

def fetchArticles(site):
    db = dbconnect()
    db.execute("select full_text from artikelen where site = '"+site+"'")
    return db.fetchall()

def download_articles(output_path):
    file = pathlib.Path(output_path)
 
    if not file.exists():
        print("Unexisting output path")
    
    else: 
        db = dbconnect()
        db.execute("select distinct site from artikelen where nepnieuws =1")
        fake_sites = db.fetchall()
        db.execute("select distinct site from artikelen where nepnieuws =0")
        real_sites = db.fetchall()

        articles = []
        for site in fake_sites:
            c = Counter(real=False)
            articles = fetchArticles(site[0])
            for article in articles:
                c.add_article(article[0])
            articles.append(c)

        for site in real_sites:
            c = Counter(real=True)
            articles = fetchArticles(site[0])
            for article in articles:
                c.add_article(article[0])
            articles.append(c)

            np.save(f'{output_path}articles.npy',articles)

if __name__=="__main__":
    path = sys.argv[0]
    download_articles(path)