from datetime import datetime
from app import db


def auto_repr(self):
	""" Автоматическое REPR форматирование для обьектов """
	base_repr = "<{}(".format(self.__class__.__name__)
	for name in self.__dict__:
		if name[0] == "_":
			continue
		value = self.__dict__[name]
		base_repr += "{}='{}',".format(name,value)
	base_repr = base_repr[:-1]
	base_repr += ")>"
	return base_repr


class WordList(db.Model):
	""" Модель юзеров """
	__tablename__ = "word list"
	id = db.Column(db.Integer(), primary_key=True)  
	word1 = db.Column(db.String())
	annotation1 = db.Column(db.String(), default="")
	word2 = db.Column(db.String())
	annotation2 = db.Column(db.String(), default="")


	def __repr__(self):
		return auto_repr(self)
	


class UsersTraining(db.Model):
	""" Модель юзеров """
	__tablename__ = "users training"
	id = db.Column(db.Integer(), primary_key=True)  
	user_id = db.Column(db.String())
	success_words = db.Column(db.Integer())
	invalid_words = db.Column(db.Integer())
	training_id = db.Column(db.Integer())
	# created = db.Column(db.DateTime, default=datetime.now())

	def __repr__(self):
		return auto_repr(self)



class Users(db.Model):
	""" Модель юзеров """
	__tablename__ = "users"
	id = db.Column(db.Integer(), primary_key=True)  
	user_id = db.Column(db.String())
	user_name = db.Column(db.Integer())
	created = db.Column(db.DateTime, default=datetime.now())

	def __repr__(self):
		return auto_repr(self)



db.create_all()
db.session.commit()






