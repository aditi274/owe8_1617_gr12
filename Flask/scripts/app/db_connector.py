from flaskext.mysql import MySQL
from flask import Flask
from datetime import date

app = Flask(__name__)

mysql = MySQL()

#Configers mysql connection
app.config['MYSQL_DATABASE_USER'] = 'owe8_1617_gr12'
app.config['MYSQL_DATABASE_PASSWORD'] = 'blaat1234'
app.config['MYSQL_DATABASE_DB'] = 'owe8_1617_gr12_4'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# opens connection to MySQL server
def createConnection():
    connection = mysql.connect()	    
    return connection
# cursor.connection is bound to the connection for the entire lifetime.
# all the commands are executed in the context of the database session and wrapped by the conenction
def createCursor(connection):
    cursor = connection.cursor()
    return cursor

# infoCursor fetches all or all remaining results of a query result set
# returns a list of tuples with all the remaining results of a query result set
# if no results are available it should actually return a empty list
def infoCursor(cursor,connection):
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
# con.commit() sends a COMMIT statement to the MySQL server - committing the current transaction
# cur.close() resets all results, and ensures that the cursor object has no reference to its original connection object.
# con.close() closes the non-persistent connection to the MySQL server that's associated with the specified link identifier.
def submitCursor(cur,con):
    con.commit()
    cur.close()
    con.close()
# The functions inserts the information of the search tasks linked with the searchWord
# the SubmitSearchWord is meant for the user, who submits a keyword.
# The keywords starts a search in the database related to the given query for retrieving the articles
# once there is a hit the query will be executed by cursor.execute
def SubmitSearchWord(searchWord):
    connection = createConnection()
    cursor = createCursor(connection)
    cursor.execute("INSERT INTO Search VALUES (NULL,%s)",searchWord)
    submitCursor(cursor,connection)

#%c moet de formatting syntax voor een date zijn maar kon niet vinden wat dat voor python is
def SubmitArticle(ListOfArticle):
    print(ListOfArticle[0])
    connection = createConnection()
    cursor = createCursor(connection)
    #Input should be a tuple of article information gathered into a list
    #[(information,etc.)(information,etc.)]
    cursor.executemany("INSERT INTO Article(PubMed_ID,Article_link,Author,Date,Preview_summary) "
                       "VALUES (%s,%s,%s,%s,%s)",ListOfArticle)
    submitCursor(cursor,connection)
# This function links articles with the keywords.
# with the executemany() method it iterates through the sequence of parameters.
# Each time passing the current parameters to the the execute() method.
# In the following function inserts information about the articles.
# The statements are executes as one execute() operation.
def LinkArticelWithSearchWord(Links):
    connection = createConnection()
    cursor = createCursor(connection)
    cursor.executemany("INSERT INTO Search_has_Article(Search_Keywords_ID,Article_PubMed_ID,Article_Search_Keywords_ID)"
                       "VALUES(%s,%s,NULL)",Links)
    submitCursor(cursor,connection)

# with the SearchWordId funtcion the application is able to generate an ID to the keywords and save them in the database
# cursor.execute executes the given database query/command.
# the parameters found in the tuple are bound to the variables in the query/command
# in the following function the data is selected from a table where there is a parameter such as Keywords=%s
def SearchWordId(searchword):
    connection = createConnection()
    cursor = createCursor(connection)
    cursor.execute("SELECT Keywords_ID "
                   "FROM Search "
                   "WHERE Keywords=%s",searchword)
    results = cursor.fetchall()
    searchWordId = results[0][0]
    cursor.close()
    connection.close()
    return searchWordId

def functieViewEntry():
    connection = createConnection()
    cursor = createCursor(connection)
    cursor.execute('select Keywords_ID,Keywords from Search order by Keywords_ID desc')
    entries = cursor.fetchall()
    print(entries)

functieViewEntry()
#SubmitArticle([(420420,'test.nl','ik',date(2005,2,12),'test test',1)])
