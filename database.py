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

#create_user("a","a","a","a","a",True)
#a = get_user_by_email("a")
#print("user name",a.email,a.verified)

#print([(a.email) for a in get_users()])
