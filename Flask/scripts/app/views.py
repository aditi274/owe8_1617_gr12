from app import app
from db_connector import functieViewEntry
from flask import render_template
app.run(debug=True)
# with this module we will use a function from db_connector
# in order to reach the database for a submit request we will use views.py
# with views.py is the application able to send a request to the database which saved
# all the articles we retrieved from the online database (in this case: PubMed)
@app.route('/')
@app.route('/index')
def index():
    functieViewEntry()
    return render_template('http://cytosine.nl/~owe8_1617_gr12/site/app', entries=entries)