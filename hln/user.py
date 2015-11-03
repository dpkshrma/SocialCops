"""User Module to authenticate user credentials"""
import config
import pymysql.cursors
import hashlib

class User():
	"""User Class"""
	uname = ''
	pwd = ''
	def __init__(self, cred):
		"""sets username and hashed password in User object
		
		Args:
		    cred (dict): user login credentials
		"""
		self.uname = cred['username']
		self.pwd = hashlib.md5(cred['password'].encode('utf-8')).hexdigest()

	def authenticate(self):
		"""Authenticates user from mysql db stored user credentials
		
		Returns:
		    bool: authentication result
		"""
		db_cred = config.mysqldb
		db = pymysql.connect(db_cred['host'], db_cred['user'], db_cred['password'], db_cred['dbname'])
		with db.cursor() as cursor:
			sql = 'SELECT count(*) from users where username="{0}" and password="{1}"'.format(self.uname, self.pwd)
			cursor.execute(sql)
			data = cursor.fetchone()
		db.close()

		if data[0]:
			return True
		else:
			return False