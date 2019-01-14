# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, url_for, redirect, send_from_directory, jsonify, current_app, Markup
from database import *
import random
from flask import session as login_session
import json 
import string
import os
import datetime
from flask import session as login_session
from validate_email import validate_email
from flask_mail import Mail, Message
import operator
from flask_oauthlib.client import OAuth, OAuthException 


CONFIG = json.loads(open('secrets.json', 'r').read())

## REAL DATES
LAUNCHDATE = datetime.datetime.strptime('26/03/2018', "%d/%m/%Y").date()
DEADLINE = datetime.datetime.strptime('09/04/2019', "%d/%m/%Y").date()

app = Flask(__name__)
mail = Mail(app)
app.secret_key = CONFIG['SECRET_KEY']
app.config['GOOGLE_ID'] = CONFIG['GOOGLE_ID']
app.config['GOOGLE_SECRET'] = CONFIG['GOOGLE_SECRET']
oauth = OAuth(app)

app.config.update(
MAIL_SERVER=CONFIG['MAIL_SERVER'],
MAIL_PORT = CONFIG['MAIL_PORT'],
MAIL_USERNAME = CONFIG['MAIL_USERNAME'],
MAIL_PASSWORD= CONFIG['MAIL_PASSWORD'],
MAIL_USE_TLS = False,
MAIL_USE_SSL = True)

EMAIL_SENDER = CONFIG['MAIL_USERNAME']
mail = Mail(app)



def verify_password(email, password):
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    return True

##################################
#### LOGIN WITH GOOGLE ROUTES ####
##################################

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/loginWithGoogle')
def loginWithGoogle():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/loginWithGoogle/authorized')
def authorized():
        resp = google.authorized_response()
        if resp is None:
                return 'Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description'])
        login_session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        print(me)
        # print(me.data)
        first_name = me.data['given_name']
        last_name = me.data['family_name']
        email = me.data['email']
        query = get_user_by_email(email)
        if query == None:
                dummy_password = random.randint(0,999)
                newUser = create_user(first_name, last_name, "home", email, dummy_password, verified=True)
                if email in goldMembers:
                        newUser.group = "gold"
                elif email in silverMembers:
                        newUser.group = "silver"
                else:
                        newUser.group = "bronze"

                ## Make a Wallet for  newUser
                if email in goldMembers:
                        initial_value = '1000000.00'
                elif email in silverMembers:
                        initial_value = '100000.00'
                else:
                        initial_value = '10000.00'
                create_wallet(initial_value,newUser)

        else:
                newUser = query

        login_session.clear()
        login_session['first_name'] = newUser.first_name
        login_session['id'] = newUser.id
        login_session['last_name'] = newUser.last_name
        login_session['group'] = newUser.group
        login_session['email'] = newUser.email
        # if 'language' in login_session:
        # 	if login_session['language'] == 'ar':
        # 		flash("تم تسجيل الدخول بنجاح ! أهلا و سهلا،  %s!" % newUser.first_name)
        # 	elif login_session['language']== 'he':
        # 		flash("התחברות מוצלחת. ברוכים הבאים, %s!" % newUser.first_name)
        # else:
        # 	flash("Login Successful. Welcome, %s!" % newUser.first_name)
        return redirect(url_for('showProducts'))

@google.tokengetter
def get_google_oauth_token():
    return login_session.get('google_token')

@app.route('/loginWithFacebook')
def loginWithFacebook():
	#Toggle the comments between the two lines below if you are running the app locally.
	#callback = url_for('facebook_authorized', next = request.args.get('next') or request.referrer or None, _external=True)
	#callback = 'https://meetcampaign18.herokuapp.com/loginWithFacebook/authorized'
	return "Not implemented"

@app.route("/")
@app.route("/main")
def showLandingPage():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	now = datetime.datetime.now().date()
	if now < LAUNCHDATE:
		timeline = "before"
	elif now > DEADLINE:
		flash(Markup("The competition has ended. Thank you for your participation! <a href='/viewResults'>Click Here to See Results</a>"))
		timeline = "after"
	else:
		#during the competition
		timeline = "during"
	return render_template("prelaunchlanding.html", timeline=timeline)

@app.route("/language/<language>")
def changeLanguage(language):
	login_session['language'] = language
	return redirect(request.referrer)

@app.route("/login", methods = ['GET', 'POST'])
def login():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if request.method == 'GET':
		return render_template('login.html')
	else:
		email = request.form['email']
		password = request.form['password']
		if email is None or password is None:
			if login_session['language'] == 'he':
				flash("צירוף שם משתמש או סיסמא לא נכון")
			elif login_session['language'] == 'ar':
				flash("إسم المستخدم خطأ \ كلمة السر خطأ")
			else:
				flash("Missing Values")
			return redirect(url_for('login'))
		if verify_password(email, password):
			user = get_user_by_email(email)
			if user.verified == False:
                            print("not verified")
                            if login_session['language'] == 'he':
                                    flash("עליך לאשר את חשבונך לפני שאתה ממשיך")
                            elif login_session['language'] == 'ar':
                                    flash("يجب عليك أن تقوم بتفعيل حسابك قبل الإستمرار ")
                            else:
                                    flash("You must verify your account before continuing")
                            return redirect(url_for('verify', email = email))
			# if login_session['language'] == 'he':
			# 	flash("התחברות מוצלחת. ברוכים הבאים,%s!" % user.first_name)
			# elif login_session['language'] == 'ar':
			# 	flash("تم تسجيل الدخول بنجاح ! أهلا و سهلا %s!" % user.first_name)
			# else:
			# 	flash("Login Successful. Welcome, %s!" % user.first_name)
			login_session['first_name'] = user.first_name
			login_session['last_name'] = user.last_name	
			login_session['email'] = email
			login_session['id'] = user.id
			login_session['group'] = user.group
			if user.group == 'student':
				return redirect(url_for('studentPortal'))
			if user.group == 'administrator':
				return redirect(url_for('showDashboard'))
			return redirect(url_for('showProducts'))
			
		else:
			if login_session['language'] == 'he':
				flash("צירוף שם משתמש או סיסמא לא נכון")
			elif login_session['language'] == 'ar':
				flash("إسم المستخدم خطأ \ كلمة السر خطأ")
			else:
				flash("Incorrect email/password combination")
			return redirect(url_for('login'))


@app.route("/signup", methods = ['GET', 'POST'])
def signup():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if request.method == 'GET':
		return render_template('signup.html')
	elif request.method == 'POST':
		first_name = request.form['first_name']
		print("Creating a new user")
		last_name = request.form['last_name']
		hometown = request.form['hometown']
		email = request.form['email']
		password = request.form['password']
		verify_password = request.form['verify_password']
		if password != verify_password:
			if login_session['language'] == 'he':
				flash("הסיסמאות אינן תואמות")
			elif login_session['language'] == 'ar':
				flash("كلمة السر غير متطابقة")
			else:
				flash("Passwords do not match")
			return redirect(url_for('signup'))
		
		
		if not email_available(email):
			if login_session['language'] == 'he':
				flash("משתמש עם כתובת האימייל הנוכחית כבר קיים.")
			elif login_session['language'] == 'ar':
				flash("هناك مستخدم آخر بنفس هذا البريد الإلكتروني")
			else:
				flash("A User already exists with this email address")
			return redirect(url_for('signup'))
		
		if True: #validate_email(email, verify=True)!=False:
                        newUser = create_user(first_name,last_name, hometown,email,password,False)
                        print("Creating a new user")
                        render_template("confirmationemail.html", user=newUser)
                        if login_session['language'] == 'ar':
                                send_email("أكد على بريدك الإلكتروني المستخدم للحملة",EMAIL_SENDER,[newUser.email],render_template("confirmationemail_ar.html", user=newUser),
                                render_template("confirmationemail_ar.html", user=newUser))
                                flash("Please check your email to verify your confirmation code")
                        elif login_session['language'] == 'he':
                                send_email("וודא את חשבון קמפיין המיט שלך",EMAIL_SENDER,[newUser.email],render_template("confirmationemail_he.html", user=newUser),
                                render_template("confirmationemail_he.html", user=newUser))
                                flash("Please check your email to verify your confirmation code")
                        else:
                                send_email("Verify your MEETCampaign Account",EMAIL_SENDER,[newUser.email],render_template("confirmationemail.html", user=newUser),
                                render_template("confirmationemail.html", user=newUser))
                                flash("Please check your email to verify your confirmation code")
                        return redirect(url_for('verify', email = email))
			
		else:
			if login_session['language'] == 'he':
				flash("כתובת האימייל שגויה. אנא נסו שנית.")
			elif login_session['language'] == 'ar':
				flash("البريد الإلكتروني خطأ . من فضلك حاول مرة أخرى")
			else:
				flash("This email is invalid. Please try again")
			return redirect(url_for('signup'))

@app.route("/verify/<email>", methods = ['GET', 'POST'])
def verify(email):
	if 'language' not in login_session:
		login_session['language'] = 'en'
	user = session.query(User).filter_by(email=email).one()
	if user.confirmation_code_expiration < datetime.datetime.now():
		if login_session['language'] == 'he':
			flash("קוד האישור הזה פג תוקף. אנא בקש קוד חדש.")
		elif login_session['language'] == 'ar':
			flash("لقد إنتهت مدة إستعمال كود التفعيل هذا . من فضلك أطلب كود جديد")
		else:
			flash("This confirmation code has expired. Please request a new code.")
		return redirect(url_for('resendCode', email = user.email))
	if request.method == 'GET':
		return render_template('verifyAccount.html', user=user)
	elif request.method == 'POST':
                code = request.form['code']
                if user.confirmation_code == code:
                        verify_user(user)
                else:
                        if login_session['language'] == 'he':
                                flash("קוד ווידוא שגוי")
                        elif login_session['language'] == 'ar':
                                flash("كود التفعيل المدخل خطأ")
                        else:
                                flash("Verification code incorrect. Please try again")
                        return redirect(url_for('verify', email = email))
                ## Make a Wallet for verified user
                ## Make a Wallet for  newUser
                if email in goldMembers:
                    usersWallet = create_wallet('1000000.00',user)
                elif email in silverMembers:
                    usersWallet = create_wallet('50000.00',user)
                else:
                    usersWallet = create_wallet('10000.00',user)

                if login_session['language']=='he':
                        flash("ווידוא חשבונך נעשה בהצלחה")
                elif login_session['language'] == 'ar':
                        flash("تم تفعيل الحساب بنجاح")
                else:
                        flash("Account Verified Successfully")
                return redirect(url_for('login'))

@app.route("/resendCode/<email>", methods = ['GET', 'POST'])
def resendCode(email):
	if 'language' not in login_session:
		login_session['language'] = 'en'
	user = get_user_by_email(email)
	if request.method == 'GET':
		return render_template('resendCode.html', email=email)
	if request.method == 'POST':
		reset_confirmation(user)
		if login_session['language'] == 'he':
			send_email("איפוס קוד חשבון קמפיין המיט שלך",EMAIL_SENDER,[user.email],render_template("confirmationemail_he.txt", user=user),
               render_template("confirmationemail_he.html", user=user))
			flash("קוד אישור חדש נשלח אל כתובת האימייל שלך.")
		elif login_session['language'] == 'ar':
			send_email("إعادة ضبط الكود الخاص بحساب الحملة",EMAIL_SENDER,[user.email],render_template("confirmationemail_ar.txt", user=user),
               render_template("confirmationemail_ar.html", user=user))
			flash("تم إرسال كود تفعيل جديد إلى بريدك الإلكتروني")
		else:
			send_email("Resetting your MEETCampaign Account Code",EMAIL_SENDER,[user.email],render_template("confirmationemail.txt", user=user),
               render_template("confirmationemail.html", user=user))
			flash("A new verification code has been sent to your email address")

		return redirect(url_for('verify', email = email))
		
@app.route("/forgotPassword", methods = ['GET', 'POST'])
def forgotPassword():
        if 'language' not in login_session:
                login_session['language'] = 'en'
        if request.method == 'GET':
                return render_template('passwordReset.html')
        elif request.method == 'POST':
                email = request.form['email']
                user = get_user_by_email(email)
                if user == None:
                        if login_session['language'] == 'he':
                                flash("לא קיים משתמש עם כתובת האימייל הזו. צור חשבון חדש.")
                        elif login_session['language'] == 'ar':
                                flash("لا يوجد مستخدم بهذا البريد الإلكتروني , من فضلك إعمل حساب جديد ")
                        else:
                                flash("No user exists with this email address.  Please create a new account")
                        return redirect(url_for('signup'))
                else:
                        reset_confirmation(user)
                        if login_session['language'] == 'he':
                                send_email("איפוס סיסמת קמפיין המיט שלך",EMAIL_SENDER,[user.email],render_template("resetpassword_he.html", user=user),
                                render_template("resetpassword_he.html", user=user))
                                flash("קוד אישור חדש נשלח אל כתובת האימייל שלך.")
                        elif login_session['language'] == 'ar':
                                send_email("إعادة ضبط كلمة السر الخاصة بحساب الحملة ",EMAIL_SENDER,[user.email],render_template("resetpassword_ar.html", user=user),
                                render_template("resetpassword_ar.html", user=user))
                                flash("تم إرسال كود تفعيل جديد إلى بريدك الإلكتروني")
                        else:
                                send_email("Resetting your MEETCampaign Password",EMAIL_SENDER,[user.email],render_template("resetpassword.html", user=user),
                                render_template("resetpassword.html", user=user))
                                flash("A new confirmation code has been sent to your email")
                        return redirect(url_for('resetPassword', email=email))


@app.route("/resetPassword/<email>", methods = ['GET','POST'])
def resetPassword(email):
	if 'language' not in login_session:
		login_session['language'] = 'en'
	user = get_user_by_email(email)
	if request.method == 'GET':
		return render_template('resetpasswordverificationcode.html', user = user)
	elif request.method == 'POST':
		code = request.form['code']
		password = request.form['password']
		verify_password = request.form['verify_password']
		if user.confirmation_code_expiration < datetime.datetime.now():
			if login_session['language'] == 'he':
				flash("קוד האישור הזה פג תוקף. אנא בקש קוד חדש.")
			elif login_session['language'] == 'ar':
				flash("لقد إنتهت مدة إستعمال كود التفعيل هذا . من فضلك أطلب كود جديد")
			else:
				flash("This confirmation code has expired. Please request a new code.")
			return redirect(url_for('passwordReset', email = user.email))
		if user.confirmation_code == code:
			if password == verify_password:
				reset_password(user,password)
				
				if login_session['language'] == 'he':
					flash("ווידוא חשבונך נעשה בהצלחה")
				elif login_session['language'] == 'ar':
					flash("تم تفعيل الحساب بنجاح")
				else:
					flash("Account Verfied Successfully")
				return redirect(url_for('login'))
			else:
				if login_session['language'] == 'he':
					flash("הסיסמאות אינן תואמות")
				elif login_session['language'] == 'ar':
					flash("كلمة السر غير متطابقة")
				else:
					flash("Passwords do not match")
				return redirect(url_for('resetPassword', email = email))
		else:
			if login_session['language'] == 'he':
				flash("קוד ווידוא שגוי")
			elif login_session['language'] == 'ar':
				flash("كود التفعيل المدخل خطأ")
			else:
				flash("Incorrect verifcation code")
			return redirect(url_for('resetPassword', email = email))

@app.route('/logout')
def logout():
	if 'id' not in login_session:
		if login_session['language'] == 'he':
			flash("עליך להיות מחובר בכדי להתנתק")
		elif login_session['language'] == 'ar':
			flash("يجب أن تسجل الدخول من أجل تسجيل الخروج")
		else:
			flash("You must be logged in in order to log out")
		return redirect(request.referrer)
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if login_session['language'] == 'he':
		logout_sentence = "התנתקות מוצלחת"
	elif login_session['language'] == 'ar':
		logout_sentence = "تم تسجيل الخروج بنجاح"
	else:
		logout_sentence = "Logged Out Successfully"
	login_session.clear()
	flash(logout_sentence)
	return redirect(url_for('showLandingPage'))

@app.route('/notify', methods = ['POST'])
def notifyList():
	email = request.form['email']
	add_to_mailing(email)
	if login_session['language'] == 'ar':
		flash("شكرا جزيلا ! سوف يتم إعلامك عندما تبدأ الحملة")
	elif login_session['language'] == 'he':
		flash("תודה רבה! ניצור אתכם קשר כשהקמפיין יתחיל.")
	else:
		flash("Thank You! You will be notified when the campaign begins")
	return redirect(url_for('showLandingPage'))

@app.route("/studentPortal")
def studentPortal():
	if 'group' not in login_session:
		return redirect(url_for('login'))
	if login_session['group'] != 'student':
		if login_session['language'] == 'he':
			flash("הדף הזה נגיש רק לתלמידים")
		elif login_session['language'] == 'ar':
			flash("هذه الصفحة الدخول إليها من قبل الطلاب فقط")
		else:
			flash("This page is only accessible to students")
		return redirect(url_for('login'))
	user = get_user_by_id(login_session['id'])
	print("team id:",user.team_id)
	team = get_team_by_id(user.team_id)
	product = get_prod_by_team_id(team.id)
	comments = session.query(Comment).filter_by(product_id =product.id).all()
	total_investments = 0.0
	for inv in product.investments:
		total_investments += inv.amount
	return render_template('teamPortal.html', user=user, team=team, comments = comments, total_investments = total_investments)

@app.route("/updateSubmission", methods = ['POST'])
def updateSubmission():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	team_name = request.form['team_name']
	description_en = request.form['description_en']
	description_ar = request.form['description_ar']
	description_he = request.form['description_he']
	website_url = request.form['website_url']
	video_url = request.form['video_url']
	photo_url = request.form['photo_url']
	user = get_user_by_id(login_session['id'])
	update_team(user.team_id, team_name, description_en, description_ar, description_he,
                    website_url, video_url, photo_url)
	flash("Team Info Updated Successfully!")

	return redirect(url_for('studentPortal'))

@app.route('/addComment/<int:team_id>', methods = ['POST'])
def addComment(team_id):
	if 'language' not in login_session:
		login_session['language'] = 'en'
	
	comment = create_comment(request.form['commentary'], team_id)
	
	if login_session['language'] == 'he':
		flash("תודה על משובך!")
	elif login_session['language'] == 'ar':
		flash("شكرا لك على ملاحظاتك!")
	else:
		flash("Thank you for your feedback!")
	return redirect(request.referrer)

@app.route('/brandClick')
def brandClick():
	if 'id' not in login_session:
		return redirect(url_for('showLandingPage'))
	else:
		return redirect(url_for('showProducts'))

@app.route("/policies")
def showPoliciesPage():
	return render_template("policies.html")

@app.route("/products")
def showProducts():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if 'id' not in login_session:
		if login_session['language'] == 'he':
			flash("עליך להיות מחובר על מנת לצפות בדף זה.")
		elif login_session['language'] == 'ar':
			flash("يجب عليك تسجيل الدخول من أجل عرض هذه الصفحة")
		else:
			flash("You must be logged in to view this page.")
		return redirect(url_for('login'))
	products = get_products()
	wallet = get_user_wallet(login_session['id']) 
	return render_template('productsPage.html', products = products, wallet = wallet)

@app.route("/product/<int:product_id>")
def showProduct(product_id):
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if 'id' not in login_session:
		return redirect(url_for('login'))
	product = get_prod_by_id(product_id)
	wallet = get_user_wallet(login_session['id'])
	return render_template('productPage.html', product = product, wallet = wallet)

@app.route("/makeAnInvestment/<int:product_id>", methods = ['POST'])
def makeAnInvestment(product_id):
	now = datetime.datetime.now().date()
	if now > DEADLINE:
		flash("The competition has ended, no more investments are being accepted.")
		return redirect(request.referrer)
	if 'language' not in login_session:
		login_session['language'] = 'en'
	try:
		amount = float(request.form['amount'])
	except ValueError:
		flash("Invalid Amount. Please only use numbers")
		return redirect(url_for('showProduct', product_id = product_id))
	if amount < 0:
		flash("No negative values please")
		return redirect(url_for('showProduct', product_id = product_id))
	wallet = get_user_wallet(login_session['id'])
	product = get_prod_by_id(product_id)
	if wallet.current_value >= amount:
		make_investment(wallet.id, product.id, amount)
		if 'language' not in login_session:
			login_session['language'] = 'en'
		if login_session['language'] == 'he':
			flash("הושקעו %s ל%s בהצלחה. תודה רבה על ההשקעה!"% (str(amount), product.team.name))
		elif login_session['language'] == 'ar':
			flash("تمت عملية الإستثمار بنجاح %s في فكرة %s شكرا جزيلا لقيامك بالإستثمار" % (str(amount), product.team.name))
		else:
			flash("Successfully invested %s for %s. Thank you for your investment!" % (str(amount), product.team.name))
		return redirect(url_for('showProducts'))
	else:
		if login_session['language'] == 'he':
			flash("אין לך מספיק כסף בכדי לבצע השקעה זו")
		elif login_session['language'] == 'ar':
			flash("ليس لديك نقود لعمل هذا الإستثمار")
		else:
			flash("You do not have enough money to make this investment")
		return redirect(url_for('showProduct', product_id = product_id))

@app.route("/viewResults")
def viewResults():
	products = get_products()
	totals = []
	rankdict = dict()
	investorsdict = dict()
	for product in products:
		total_investments = 0.0
		for inv in product.investments:
			total_investments += inv.amount
		totals.append(total_investments)
		rankdict[product.team.name] = total_investments
		investorsdict[product.team.name] = len(product.investments)
	rankings = sorted(rankdict.items(), key=operator.itemgetter(1),reverse=True)
	return render_template('publicdashboard.html', totals = totals, products = products, rankings = rankings, investorsdict = investorsdict)

@app.route("/showDashboard", methods = ['GET','POST'])
def showDashboard():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if 'id' not in login_session:
		flash("You do not have access to this page")
		return redirect(url_for('showLandingPage'))
	elif get_user_by_id(login_session['id']).email not in admins:
		flash("You do not have access to this page")
		return redirect(url_for('showLandingPage'))
	if request.method == 'POST':
            create_team(request.form["team_name"],request.form["members"])
            
	products = get_products()
	bronze_investors, silver_investors, gold_investors = get_users_ranked()
	totals = []
	rankdict = dict()
	investorsdict = dict()
	for product in products:
		total_investments = 0.0
		for inv in product.investments:
			total_investments += inv.amount
		totals.append(total_investments)
		rankdict[product.team.name] = total_investments
		investorsdict[product.team.name] = len(product.investments)
	rankings = sorted(rankdict.items(), key=operator.itemgetter(1),reverse=True)
	return render_template('dashboard.html', totals = totals, products = products, bronze_investors = bronze_investors, silver_investors = silver_investors, gold_investors = gold_investors, rankings = rankings, investorsdict = investorsdict)

@app.route("/teamActivity")
def showTeamActivity():
	if 'language' not in login_session:
		login_session['language'] = 'en'
	if 'id' not in login_session:
		flash("You do not have access to this page")
		return redirect(url_for('showLandingPage'))
	elif get_user_by_id(login_session['id']).email not in admins:
		flash("You do not have access to this page")
		return redirect(url_for('showLandingPage'))
	investments = get_investments()
	return render_template('teamActivity.html', investments = investments)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    with app.app_context():
    	mail.send(msg)

if __name__ == '__main__':
	app.run(debug=True)
