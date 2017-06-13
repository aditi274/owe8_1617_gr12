#!/usr/bin/env python3

import sys
from datetime import datetime
from Bio import Entrez
from Bio import Medline
from db_connector import SubmitArticle,SearchWordId,LinkArticelWithSearchWord

#Main flow trough program
#First sets email for NCBI
#Parses csv query file to dictionarys{dutch:'',english:'',latin:''} in list
#Uses querys to get related papers
#Loops through results and submits to database
def Main(queryFilePath):
    papers = []
    Entrez.email = "aditi.ch2@gmail.com"     # Always tell NCBI who you are
    querysAsDicInList = CsvFileToList(queryFilePath)
    paperResult = RelatedPapers(querysAsDicInList)
    for query in paperResult:
        papers = paperResult[query]
        SubmitPapers(papers,query)

#Loops through all query dictionarys and retrieves papers with english or latin name
#Put results in dictionary with english name as key
def RelatedPapers(querysAsDicInList):
    paperResults = {}
    for query in querysAsDicInList:
        englishQuery = query["English"] 
        latinQuery = query["Latin"]
        dutchQuery = query["Dutch"]
        handle = Entrez.esearch(db="pubmed", term="("+englishQuery+")OR("+latinQuery+")", retmode='xml',retmax=100000)
        records = Entrez.read(handle)
        handle.close()
        idsHit = records["IdList"]
        paperResults[englishQuery] = idsHit
    return paperResults

#Parses paperIds to paper information and makes a sql ready list and submits to database
#After submitting papers links the papers to searchword
def SubmitPapers(paperIds,query):
    submitArticles = []
    submitLinks = []
    paperIdsCsv = ListToCsv(paperIds)
    papers = FetchPaper(paperIds)
    searchWordId = SearchWordId(query)
    
    for paper in papers:
        information = PaperInformation(paper)
        
        paperToAdd = (information['PubMedId'],information['Url'],information['Author'],information['PublicationDate'],information['Summary'])
        linkToAdd = (searchWordId,information['PubMedId'])
        
        submitArticles.append(paperToAdd)
        submitLinks.append(linkToAdd)
    SubmitArticle(submitArticles)
    LinkArticelWithSearchWord(submitLinks)

#Checks if all papers have the right information and puts information in dictionary
def PaperInformation(paper):
    paperInformation = {}
    """
        for number in range(0,10):
            hit = idsHit[number]
            results = fetch_article(hit)
            for result in results:
                papers.append(result)
    """
    paperKeys = paper.keys()
    if 'AU' in paperKeys:
        author = paper['AU']
    else:
        author = "missing"
    if 'PMID' in paperKeys:
        link = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='+paper['PMID']
        pmid = paper['PMID']
    else:
        link = "missing"
        pmid = "missing"
    if 'DP' in paperKeys:
        date = paper['DP']
    else:
        date = 'missing'
    #Always missing?
    if 'AB' in paperKeys:
        summary = paper['AB']
    else:
        summary = 'missing'
    paperInformation["Author"] = "".join(author)
    paperInformation["Url"] = link
    #Hacky
    try:
	paperInformation["PublicationDate"] = datetime.strptime(date,'%Y %b %d')
    except:
	try:
	    paperInformation["PublicationDate"] = datetime.strptime(date,'%Y %b')
    	except:
	    try:
	    	paperInformation["PublicationDate"] = datetime.strptime(date,'%Y')
    	    except:
		paperInformation["PublicationDate"] = None
    paperInformation["Summary"] = summary
    paperInformation["PubMedId"] = pmid
    return paperInformation

#Retrieves paper with id as json and returns list with all papers
def FetchPaper(idToFetch):
    articles = []
    handle = Entrez.efetch(db="pubmed", id=idToFetch, rettype="medline", retmode="json",retmax=100000)
    try:
        article = Medline.parse(handle)
    except:
        print("Error can't retrieve: "+idToFetch)
        article = None
    #TODO find out why for loop is slow, prob pubmed thing
    for results in article:
        articles.append(results)
    print("Done retrieving")
    handle.close()
    return articles

#Parses csv file to list
#Splits every line on , and puts information in dictionary
#First word dutch,Second word English,Third word Latin
def CsvFileToList(filePath):
    querys = []
    fileToUse = open(filePath,'r')
    for line in fileToUse:
        query = {}
        items = line.replace('\n','').split(',')
        query["Dutch"] = items[0]
        query["English"] = items[1]
        query["Latin"] = items[2]
        querys.append(query)
    return querys

#Loops through list and parses to csv format
def ListToCsv(items):
    line = ''
    for item in items:
        line += item + ','
    return line[:-1]

#Takes first file given in command line
#File should be csv file filled with querys
Main(sys.argv[1])
