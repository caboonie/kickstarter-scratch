# KickStarter
Voting Website for Y2 Yearlong Group Projects

## Running Locally:

### Required Packages
All of the packages for this website can be installed using the pip installer.
It's generally good practice to work within a virtual environment which can be created and then activated with the following:
```
virtualenv venv
source venv/Scripts/activate
```
Then, the dependencies can easily be installed by running:
```
pip install -r requirements.txt
```

<ul>
<li>pandas(for database populating)</li>
<li>flask</li>
<li>Flask-HTTPAuth</li>
<li>Jinja2</li>
<li>passlib</li>
<li>python-dateutil</li>
<li>requests</li>
<li>SQLAlchemy</li>
<li>psycopg2</li>
<li>validate_email</li>
<li>flask_mail</li>
<li>flask_oauthlib</li>
<li>Py3DNS</li>
<!-- <li>pyDNS</li>  -->
</ul>


1.  Fill in the values of secrets.json with your own credentials.
	- The Google and Facebook IDs/secrets are for enabling oauth2 log-in using Google and Facebook.
	- The MAIL_USERNAME/PASSWORD are for the email account to send emails out from. I created a gmail last year to send the automatic emails (noreply.meet.mit@gmail.com), but it may be helpful to create an actual meet.mit.edu email address for this.


2. Run python webapp.py to host locally


hopefully it should run on localhost:5000 without any problems.

Important files:  all html in templates folder all templates inherit from layout.html , all css files in static folder,

Ping me if you run into any problems.

Notes - gmail for sending verification emails needs to allow access to less-secure apps
Note - facebook login is not setup yet
