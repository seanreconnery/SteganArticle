from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, flash, request, jsonify, render_template, Markup

app = Flask(__name__)
app.secret_key = "Q17the7app7key55x"


def split2chars(theText):
    # Take a string and return a list of individual characters--including spaces and punctuation.
    return list(theText)

def split2words(theText):
    # return a list of the WORDS in the text--stripping out punctuation.
    theText.replace('.', ' ')
    theText.replace(',', ' ')
    theText.replace(';', ' ')
    theText.replace(':', ' ')
    theText.replace('!', ' ')
    theText.replace('?', ' ')
    theText.replace('  ', ' ')
    return list(theText.split(' '))

def GrabTheDigits(theText, theMsg):
    # return a list of integers that correspond to letter locations in the string.
    # currently searches from the end of the string (more obfuscated than searching from the start.. but not much)
    # TO-DO:  iterate thru the string to find the next instance of the needed letter
    decrypt_string = []
    ds = ''
    counter = 0             # counter to help iterate thru letters so each letter doesn't always have to be the same number
    for ltrs in theMsg:
        if theText.find(ltrs, counter) != -1:
            # letter found
            ds += str(theText.find(ltrs, counter)) + ','
            decrypt_string.append(str(theText.find(ltrs, counter)))
            counter +=1
        else:
            # letter NOT found.  start counter over
            counter = 0

    #return decrypt_string      # returns list
    return ds[0:(len(ds) - 1)]  # returns a csv string


def DecodeWithDigits(theText, decrypt_list):
    decoded_msg = ''
    for n in decrypt_list:
        x = theText[int(n)]
        decoded_msg += x

    return decoded_msg


def GetArticleText(nyp_url):
    html = requests.get(nyp_url).text

    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('div', ["entry-content", "entry-content-read-more"])
    p = body.find_all('p')
    coverText = ''
    for tags in p:
        temp = str(tags).strip('<p>')
        temp = temp.strip('</p>')
        coverText += re.sub('<[^<]+?>', '', temp)

    return(coverText)       # returns the text from all the <P> tags in an NYPost article


def CreateSecretMessage(nyp_url, secret_message):
    # grab an article from the NYPost / some NY POST articles:
    #   here are some NYPost example articles you can use:
    #   'https://nypost.com/2020/04/29/north-korea-investigating-after-news-report-claims-kim-jong-un-dead/'
    #   'https://nypost.com/2020/04/28/kim-jong-uns-uncle-emerges-as-possible-successor-in-north-korea/'
    #   'https://nypost.com/2020/04/29/north-korea-investigating-after-news-report-claims-kim-jong-un-dead/'
    NY_Post = str(nyp_url)              # lazily making sure the URL is treated as a string.
    potentialMsg = str(secret_message)  # message needs to be treated as a string as well.

    html = requests.get(NY_Post).text   # grab the article from the NYPost website & convert it to a text string

    soup = BeautifulSoup(html, 'html.parser')                               # it is such a beautiful soup, indeed...
    body = soup.find('div', ["entry-content", "entry-content-read-more"])   # find a specific DIV tag & class
    p = body.find_all('p')              # grab all the <P> takes within that DIV
    coverText = ''          # create an empty string to store the (HTML stripped) article text in
    for tags in p:
        temp = str(tags).strip('<p>')               # iterate thru the P tags and remove them
        temp = temp.strip('</p>')
        coverText += re.sub('<[^<]+?>', '', temp)   # remove any extra HTML like links and spans and such

    b = split2chars(coverText)          # turn the COVER TEXT into a list of characters
    a = split2chars(potentialMsg)       # turn the SECRET MESSAGE into a list of characters as well

    # turn the COVER and SECRET to a SET and check if SECRET is able to be contained within COVER
    anyIntersec = set(a).intersection(b)

    if set(anyIntersec) == set(potentialMsg):
        # the POTENTIAL message is containable within the COVER message
        dec_str = GrabTheDigits(coverText, potentialMsg)

        return(dec_str)     # return a CSV string with the KEY digits

    elif set(anyIntersec) != set(potentialMsg):
        # not enough characters in COVER message to create the SECRET message
        print("Message CAN NOT be embedded in this set of COVER text")
        return("Error - message cannot be created with characters available in chosen NY Post article.")

    else:
        # uh...
        print("some error?")
        return("Some error??")

###########################################################



####### -- CREATE -- #######
@app.route('/create', methods=['POST'])
def createMessage():
    # create an embedded message from an article link
    if 'nyposturl' in request.form:     # make sure there's an NYPost article
        coverLink = request.form['nyposturl']
    if 'secretmessage' in request.form: # make sure there's a secret message
        sec_message = request.form['secretmessage']

    thenums = CreateSecretMessage(coverLink, sec_message)
    return render_template('index.html', theKey=thenums)     # return CSV string



####### -- EXTRACT -- #######
@app.route('/extract', methods=['POST'])
def extractMessage():
    # extract the message from an NY Post article which used as a cover text
    if 'posturl' in request.form:               # NY Post article URL
        cover_link = request.form['posturl']
    if 'messagenums' in request.form:           # KEY / list of numbers used for extraction
        num_list = request.form['messagenums']

    digit_list = num_list.split(',')
    article_text = GetArticleText(cover_link)

    decoded = DecodeWithDigits(article_text, digit_list)
    return render_template('index.html', xtracted=decoded)  # return CSV string


####### -- MAIN ROUTE -- #######
@app.route('/')
def index():
    return(render_template('index.html'))


####### !! API --> CREATE !! #######
@app.route('/api/create', methods=['POST'])
def api_create():
    # create an embedded message from an article link
    if 'nyposturl' in request.form:     # make sure there's an NYPost article
        coverLink = request.form['nyposturl']
    if 'secretmessage' in request.form: # make sure there's a secret message
        sec_message = request.form['secretmessage']

    thenums = CreateSecretMessage(coverLink, sec_message)
    
    resp = jsonify({'Secret Key': thenums})
    resp.status_code = 201
    return resp
    

####### !! API --> EXTRACT !! #######
@app.route('/api/extract', methods=['POST'])
def api_extract():
    # extract the message from an NY Post article which used as a cover text
    if 'nyposturl' in request.form:               # NY Post article URL
        cover_link = request.form['nyposturl']
    if 'csvkey' in request.form:           # KEY / list of numbers used for extraction
        num_list = request.form['csvkey']

    digit_list = num_list.split(',')
    article_text = GetArticleText(cover_link)

    decoded = DecodeWithDigits(article_text, digit_list)
    
    resp = jsonify({'Secret Message': decoded})
    resp.status_code = 201
    return resp
    
    
####### !! API --> how to use it !! #######
@app.route('/api')
def api_endpoints():
    example_create = "<blocktext>import requests<br><br>r = requests.post('/api/create', data={'nyposturl': NYPost_URL, 'secretmessage': 'your secret message here'})<br><br>print(r.text)</blocktext>"

    example_extract = "<blocktext>import requests<br><br>r = requests.post('/api/create', data={'nyposturl': NYPost_URL, 'csvkey': '1,3,17,55,71,...'})<br><br>print(r.text)</blocktext>"

    html = "<html><br><br><center><div width='50%'><h1>This is not the endpoint you're looking for...</h1><br><h2>You can use:</h2><ul>"
    html += "<li><h3><b>/api/create</b></h3>nyposturl: https://nypost...<br>secretmessage: your secret message<br><br>"
    html += "<h4>Python Code Example:</h4>" + example_create + "</li>"
    html += "<li><h3><b>/api/extract</b></h3>nyposturl: https://nypost...<br>csvkey: 1,3,55,22,..<br>"
    html += "<h4>Python Code Example:</h4>" + example_extract + "</li>"
    html += "</ul><br></div></center>"
    return html
    

# Run Server
if __name__ == '__main__':
    app.run()
