from sqlalchemy import Column,Integer,String, DateTime, ForeignKey, Float, DateTime, Boolean,PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.apps import custom_app_context as pwd_context
import psycopg2
import datetime
import json
import os

Base = declarative_base()

class Timeline(Base):
	__tablename__ = 'timeline'
	id = Column(Integer, primary_key=True)
	start_date = Column(DateTime)
	end_date = Column(DateTime)

class SpecialEmail(Base):
	__tablename__ = 'specialemail'
	id = Column(Integer, primary_key=True)
	email = Column(String(255))
	group = Column(String(255))

class MailingList(Base):
	__tablename__ = 'mailinglist'
	id = Column(Integer, primary_key=True)
	language = Column(String(255))
	email = Column(String(255))
	group = Column(String(255))
	

class User(Base):
	#Everyone in the system is a type of user, Authorization of Student Users, Administrators, and high profile investors will be specified in the 'group' field
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	first_name = Column(String(255))
	last_name = Column(String(255))
	username = Column(String(255))
	group = Column(String(255))
	email = Column(String(255))
	ip_address = Column(String(255))
	password_hash = Column(String(255))
	team = relationship("Team", back_populates = "students")
	team_id = Column(Integer, ForeignKey('team.id'))
	wallet = relationship("Wallet", uselist = False, back_populates = "user")
	comments = relationship("Comment", back_populates="user")
	verified = Column(Boolean)
	confirmation_code = Column(String)
	confirmation_code_expiration = Column(DateTime)
	hometown = Column(String(255))
	def hash_password(self, password):
	    self.password_hash = pwd_context.encrypt(password)
	def verify_password(self, password):
	    return pwd_context.verify(password, self.password_hash)

class Team(Base):
        #Users of the 'Student' group are part of a Team.  Each team can create a profile page.
        __tablename__ = 'team'
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        photo = Column(String(255), unique=False)
        students = relationship("User", back_populates = "team")
        product = relationship("Product",uselist=False, back_populates = "team")
        email = Column(String(255))
        password = Column(String(255))
        def set_photo(self, photo):
                self.photo = photo

class Wallet(Base):
	# Every User is assigned a wallet for investing in the products. The initial value of the wallet is determined based upon their group
	__tablename__ = 'wallet'
	id = Column(Integer, primary_key=True)
	initial_value = Column(Float)
	current_value = Column(Float)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship("User",back_populates="wallet")
	investments = relationship("Investment", back_populates="wallet")

class Comment(Base):
	# Users can leave comments for Product ideas
	__tablename__ = 'comment'
	id = Column(Integer, primary_key=True)
	text = Column(String)
	user =relationship("User", back_populates="comments")
	user_id = Column(Integer, ForeignKey('user.id'))
	product = relationship("Product", back_populates = "comments")
	product_id = Column(Integer, ForeignKey('product.id'))
	timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
	#Each team must create one product to submit
	__tablename__ = 'product'
	id = Column(Integer, primary_key=True)
	comments = relationship("Comment", back_populates = "product") 
	team_id = Column(Integer, ForeignKey('team.id'))
	team = relationship("Team", back_populates="product")
	# product_name = Column(String(255))
	team_members = Column(String(255))
	investments = relationship("Investment", back_populates= "product")
	photo = Column(String(255), unique = False)
	video = Column(String(255), unique = False)
	description_en = Column(String)
	description_ar = Column(String)
	description_he = Column(String)
	website_url = Column(String(255))
	def set_photo(self, photo):
		self.photo = photo
	def set_video(self, video):
		self.video = video


class Investment(Base):
	# If an investor likes a product idea, they can invest in that idea.  Once an investment is made, it cannot be reversed.
	__tablename__ = 'investment'
	id = Column(Integer, primary_key=True)
	wallet = relationship("Wallet", back_populates="investments")
	wallet_id = Column(Integer, ForeignKey('wallet.id'))
	product = relationship("Product", back_populates="investments")
	product_id = Column(Integer, ForeignKey('product.id'))
	amount = Column(Float)
	timestamp = Column(DateTime, default=datetime.datetime.utcnow)


