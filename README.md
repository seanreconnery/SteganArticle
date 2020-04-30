# SteganArticle
Utilize NY Post articles as "cover text" to encode secret messages by means of a "digital grille cipher" and provide a 'key list' for deciphering.

Long ago, the CIA was known for using newspaper articles to send secret messages to operatives.  This is well known "spycraft".  A method that often was employed is referred to as a "Grille Cipher".  Basically, a Grille is created to cover a majority of the article text, but exposing "random" letters and/or words.  Putting these letters/words together would create a message that only could be deciphered with the specific grille used to create it.

This is a quick & dirty "digital grille" cipher.

Created with Python, Flask, and BeautifulSoup.

Run:  python3 main.py
and open up your browser to 127.0.0.1:5000
Enter an NYPost article link & a message you want to encode.

To retrieve, enter the same NYPost article link & the key string of numbers.


Twitter:  @_Luke_Slytalker
