from models import *
import datetime
import random
from random import randint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

engine = create_engine('sqlite:///kickstarter.db?check_same_thread=False')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

with open('silvermembers.txt') as f:
    silverMembers = f.read().splitlines()
with open('goldmembers.txt') as f:
    goldMembers = f.read().splitlines()
with open('admins.txt') as f:
    admins = f.read().splitlines()

def generateConfCode():
	return str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))

def create_user(first_name,last_name,hometown,email,password,verified=False):
    user = User(first_name=first_name, last_name=last_name, hometown = hometown,email=email, verified=verified)
    user.confirmation_code = generateConfCode()
    user.confirmation_code_expiration = datetime.datetime.now() + datetime.timedelta(minutes = 10)
    user.hash_password(password)
    if email in goldMembers:
        user.group = "gold"
    elif email in silverMembers:
        user.group = "silver"
    else:
        user.group = "bronze"
    session.add(user)
    session.commit()
    return user

def reset_confirmation(user):
    user.confirmation_code = generateConfCode()
    user.confirmation_code_expiration = datetime.datetime.now() + datetime.timedelta(minutes = 10)
    session.add(user)
    session.commit()

def reset_password(user,password):
    user.hash_password(password)
    session.add(user)
    session.commit()
    
def email_available(email):
    users = session.query(User).filter_by(email=email).all()
    return users == []

def get_user_by_email(email):
    user = session.query(User).filter_by(email=email).first()
    return user

def get_users():
    return session.query(User).all()

def get_users_ranked():
        return (session.query(User).filter_by(group = 'bronze').all(),session.query(User).filter_by(group = 'silver').all(),session.query(User).filter_by(group = 'gold').all())

def verify_user(user):
    user.verified = True
    session.add(user)
    session.commit()

def create_wallet(coins, user):
    wallet = Wallet(initial_value = coins, current_value = coins, user = user)
    session.add(wallet)
    session.commit()
        
def get_products():
    return session.query(Product).all()

def get_user_wallet(user_id):
    return session.query(Wallet).filter_by(user_id = user_id).one_or_none()

def add_to_mailing(email):
        newEmail = MailingList(email=email)
        session.add(newEmail)
        session.commit()

def get_user_by_id(user_id):
        return session.query(User).filter_by(id=user_id).first()

def get_team_by_id(team_id):
        return session.query(Team).filter_by(id=team_id).first()

def get_prod_by_team_id(team_id):
        return session.query(Product).filter_by(team_id = team_id).one()

def get_prod_by_id(product_id):
        return session.query(Product).filter_by(id = product_id).one()

def get_comments_by_team_id(team_id):
        return session.query(Comment).filter_by(product_id =product.id).all()

def update_team(team_id, team_name, description_en, description_ar, description_he,website_url, video_url, photo_url):
        team = session.query(Team).filter_by(id=user.team_id).one()
        team.name = team_name
        team.product.description_en = description_en
        team.product.description_ar = description_ar
        team.product.description_he = description_he
        team.product.website_url = website_url
        team.product.video = video_url
        team.product.photo = photo_url
        session.add(team)
        session.commit()

def create_comment(text,team_id):
        product = session.query(Product).filter_by(team_id=team_id).one()
        comment = Comment(text = text, product=product)
        session.add(comment)
        session.commit()

def make_investment(wallet_id, product_id, amount):
        inv = Investment(wallet_id = wallet_id, product_id = product_id, amount = amount)
        wallet.current_value = wallet.current_value - amount
        session.add_all([wallet,inv])
        session.commit()

def get_investments():
        return session.query(Investment).all()
      
        
def create_team(team_name,members):
        newTeam = Team(name=team_name)
        session.add(newTeam)
        newProduct = Product(team_id=newTeam.id, team_members=members)
        print("has team check?",newProduct.team,newTeam.id)
        newProduct.team = newTeam
        session.add(newProduct)
        session.commit()
        print("has team check now?",newProduct.team)
        


class TeamObject:
	def __init__(self, name, members, video, description_he, description_ar, description_en, image):
		self.name=name
		self.members=members
		self.video=video
		self.description_he=description_he
		self.description_ar=description_ar
		self.description_en=description_en
		self.image=image

teams = {
	1: TeamObject(name="Childn’t", members="Warrd, Nisreen, Gilead, Nicole, Lyne",
		video="https://www.youtube.com/embed/gopjiCJ0Y5k",
		description_he="מעל ל-37 ילדים מתים כל שנה בישראל בעקבות שכיחתם או השארתם ברכב חם. אנחנו יצרנו אפליקציה במטרה להזכיר לך לא לשכוח את ילדך ברכב. האפליקציה תתחבר ישירות למערכת הבלוטות' של הרכב וכאשר המנוע יתכבה, היא תזהה את התנתקות הבלוטות' ותשמיע קטע קול האומר \"אל תשכח את ילדך\". חזוננו הוא להפחית את הבעיה הכה שכיחה הזו ואף להכחידה כליל על מנת להבטיח חיים לילדנו.",
		description_ar="هناك أكثر من ٣٧ طفل كل عام يفقدون حياتهم في اسرائيل بسبب نسيانهم في السيارة. تصبح درجات الحرارة مرتفعة جداً في الصيف، وذلك يؤدي إلى مقتل الطفل. قمنا بعمل تطبيق يتصل بشكل تلقائي إلى بلوتوث السيارة، وعندما تطفئ السيارة سيلغى الاتصال بالبلوتوث ويتكلم التطبيق ويقول \"صباح الخير، لا تنسى طفلك\". هدفنا هو مساعدة الوالدين في تنظيم وقتهم لنقلل من هذه الظاهرة لتوفير حياة أفضل لأولادنا.",
		description_en="Over 37 children die every year in Israel due to being forgotten/left in a hot car. We created an app to remind you to not forget your child. The app will automatically connect to the car’s bluetooth. Once the car's engine turns off the app will recognize the bluetooth's disconnection and play an audio message saying \"don't forget your child\". Our vision is reducing, this  unfortunately increasing phenomenon and providing a future for our children.",
		image="/static/team_mockups18/childnt.png"
	)
}

'''
for i in range(1, 2):
                current_team = teams[i]
                newTeam = Team(id=i, name=current_team.name)
                session.add(newTeam)

                newProduct = Product(
                        team_id=i,
                        #product_name=current_team.name,
                        team_members=current_team.members,
                        description_en=current_team.description_en,
                        description_he=current_team.description_he,
                        description_ar=current_team.description_ar,
                        photo=current_team.image,
                        video=current_team.video
                )
                print("has team?",newProduct.team)
                session.add(newProduct)
                session.commit()
                print("has team now?",newProduct.team)
                print("team",i,"already added")
'''

print("teams",[(a.id) for a in session.query(Team).all()])
print("products",[prod.team for prod in get_products()])
    
#create_user("a","a","a","a","a",True)
#a = get_user_by_email("a")
#print("user name",a.email,a.verified)


user = create_user("stud","ent","home","student","student",True)
user.group = "student"
user.team_id = 1
session.add(user)
session.commit()

user = create_user("admin","admin","home","admin","admin",True)
user.group = "administrator"
user.team_id = 1
session.add(user)
session.commit()


#print([(a.email) for a in get_users()])
