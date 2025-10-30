from imports_and_init import *

def admin_log(message, level):

	#Log activity on website, especially suspicious POST data

	#Lowest alert level, just basic activities like logging in
	alert_level = ' ' 	
	
	if level == 2:
		 #Mid alert level, potentially suspicious activities like failed logins
		alert_level = ' (!) '
	
	elif level == 3:
		#Highest alert level, suspicious POST data such as breaking char length limit on forms 
		#and illegal chars that could be sign of fuzzing or SQL injections
		alert_level = ' (!!) '
	
	with open('/your_path_here/admin_log.txt', 'a') as AL:
		AL.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{alert_level}{message}\n")

def get_db_connection():

	#Log in MySQL user for any DB tasks

	mysql_user_info = ''
	with open('/your_path_here/MadCow.txt', 'r') as MC:
		mysql_user_info = MC.read().split(' ')

	return mysql.connector.connect(

		host = mysql_user_info[0],
		user = mysql_user_info[1],
		password = mysql_user_info[2],
		database = mysql_user_info[3]

	)

class User(UserMixin):
	
	#User class for customers

	def __init__(self, customer_id, first_name, last_name, login_email, password_hash, region, street_address, city, state, zip_code, phone_number):
	
		self.customer_id = customer_id
		self.first_name = first_name
		self.last_name = last_name
		self.login_email = login_email
		self.password_hash = password_hash
		self.region = region
		self.street_address = street_address
		self.city = city
		self.state = state
		self.zip_code = zip_code
		self.phone_number = phone_number

	def get_id(self):
		return str(self.login_email)
	
	def get_type(self):
		return 'customer'
	
	def get_name(self):
		return self.first_name
	
	def get_customer_id(self):
		return str(self.customer_id)
	
	def get_pass_hash(self):
		return self.password_hash
	
	def get_user_info(self):
	
		user_info = {
	
			'name': f"{self.first_name} {self.last_name}", 
			'street_address': self.street_address, 
			'city_state_zip': f"{self.city}, {self.state} {self.zip_code}",
			'phone_number': self.phone_number
	
		}
	
		return user_info
	
	def get_user_order_info(self):
	
		user_order_info = {
	
			'customer_id': self.customer_id,
			'to_region': self.region,
			'to_street_address': self.street_address,
			'to_city': self.city,
			'to_state': self.state,
			'to_zip_code': self.zip_code
	
		}
	
		return user_order_info
	
	def get_all_info(self):
	
		all_info = {
	
			'first_name': self.first_name,
			'last_name': self.last_name,
			'street_address': self.street_address,
			'city': self.city,
			'state': self.state,
			'zip_code': self.zip_code,
			'phone_number': self.phone_number
	
		}
	
		return all_info
	
	def update_info(self, first_name, last_name, street_address, city, region, state, zip_code, phone_number):
	
		self.first_name = first_name
		self.last_name = last_name
		self.street_address = street_address
		self.city = city
		self.region = region
		self.state = state
		self.zip_code = zip_code
		self.phone_number = phone_number

		conn = get_db_connection()
		cursor = conn.cursor()
	
		try:
			cursor.execute(f"UPDATE customers SET first_name = '{self.first_name}', last_name = '{self.last_name}', street_address = '{self.street_address}', city = '{self.city}', region = '{self.region}', state = '{self.state}', zip_code = '{self.zip_code}', phone_number = '{self.phone_number}' WHERE customer_id = {self.customer_id}")
			conn.commit()
	
		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

	def update_password(self, old_password, new_password):
	
		if bcrypt.checkpw(old_password.encode('utf-8'), self.password_hash.encode('utf-8')):
	
			new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor()
	
			try:
	
				cursor.execute(f"UPDATE customers SET password_hash = '{new_password_hash}' WHERE customer_id = {self.customer_id}")
				conn.commit()
				self.password_hash = new_password_hash
	
			except(mysql.connector.errors.ProgrammingError) as err:
				print(f"Programming Error: {err}")
				error_found = True

			except(mysql.connector.errors.OperationalError) as err:
				print(f"Operational Error: {err}")
				error_found = True

			except(mysql.connector.errors.Error) as err:
				print(f"General MySQL Error: {err}")
				error_found = True

			finally:
				cursor.close()
				conn.close()	

			if error_found:
				return False
			
			return True
	
		else:
			return False	

class Employee(UserMixin):

	#User class for employee accounts

	def __init__(self, employee_id, location_id, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, position, privilege_level, start_hours, end_hours, wage, login_email, password_hash):

		self.location_id = location_id
		self.employee_id = employee_id
		self.first_name = first_name
		self.last_name = last_name
		self.region = region
		self.street_address = street_address
		self.city = city
		self.state = state
		self.zip_code = zip_code	
		self.dob = dob
		self.ssn = ssn	
		self.position = position
		self.privilege_level = privilege_level
		self.start_hours = start_hours
		self.end_hours = end_hours
		self.wage = wage
		self.login_email = login_email #Come from employee_login table
		self.password_hash = password_hash #Come from employee login table
		self.phone_number = phone_number

	def get_id(self):
		return str(self.login_email)
	
	def get_type(self):
		return 'employee'
	
	def get_privilege_level(self):
		return int(self.privilege_level)
	
	def get_name(self):
		return self.first_name
	
	def get_employee_id(self):
		return str(self.employee_id)
	
	def get_region(self):
		return self.region
	
	def get_location_id(self):
		return self.location_id
	
	def get_location_type(self):

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:
			cursor.execute(f"SELECT type FROM locations WHERE location_id = {self.get_location_id()}")
			location_type = cursor.fetchone()
			location_type = location_type['type']

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")
			error_found = True

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")
			error_found = True

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")
			error_found = True

		finally:
			cursor.close()
			conn.close()

		return location_type
	
	def get_pass_hash(self):
		return self.password_hash
	
	def get_all_info(self):

		all_info = {
			'first_name': self.first_name,
			'last_name': self.last_name,
			'street_address': self.street_address,
			'city': self.city,
			'state': self.state,
			'zip_code': self.zip_code,
			'phone_number': self.phone_number
		}

		return all_info
	
	def update_info(self, first_name, last_name, street_address, city, region, state, zip_code, phone_number):

		self.first_name = first_name
		self.last_name = last_name
		self.street_address = street_address
		self.city = city
		self.region = region
		self.state = state
		self.zip_code = zip_code
		self.phone_number = phone_number

		conn = get_db_connection()
		cursor = conn.cursor()

		try:
			cursor.execute(f"UPDATE employees SET first_name = '{self.first_name}', last_name = '{self.last_name}', street_address = '{self.street_address}', city = '{self.city}', region = '{self.region}', state = '{self.state}', zip_code = '{self.zip_code}', phone_number = '{self.phone_number}' WHERE employee_id = {self.employee_id}")
			conn.commit()

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

	def update_password(self, old_password, new_password):

		if bcrypt.checkpw(old_password.encode('utf-8'), self.password_hash.encode('utf-8')):
			new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor()

			try:
				cursor.execute(f"UPDATE employee_logins SET password_hash = '{new_password_hash}' WHERE employee_id = {self.employee_id}")
				conn.commit()
				self.password_hash = new_password_hash

			except(mysql.connector.errors.ProgrammingError) as err:
				print(f"Programming Error: {err}")
				error_found = True

			except(mysql.connector.errors.OperationalError) as err:
				print(f"Operational Error: {err}")
				error_found = True

			except(mysql.connector.errors.Error) as err:
				print(f"General MySQL Error: {err}")
				error_found = True

			finally:
				cursor.close()
				conn.close()	

			if error_found:
				return False
			
			return True
		else:
			return False		

@login_manager.unauthorized_handler
def unauthorized_callback():

	#Redirect logged out user to login page when attempting access to certain pages

	if 'login' not in request.path:
		session['next_url'] = request.path
	
	return redirect(url_for('login'))

@login_manager.user_loader
def load_user(login_email):

	#Load either customer or employee user

	try:

		if '@MalonDairy.fake' in login_email:

			#This is currently the only way to determine if account is an employee
			#There is likely a better way, but this does work for now

			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
	
			cursor.execute(f"SELECT employee_id, email, password_hash FROM employee_logins WHERE email = '{login_email}'")
			employee_login_data = cursor.fetchone()

			cursor.execute(f"SELECT location_id, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, position, privilege_level, start_hours, end_hours, wage FROM employees WHERE employee_id = '{employee_login_data['employee_id']}'")
			employee_data = cursor.fetchone()
			employee_data.update(employee_login_data)

			cursor.close()
			conn.close()

			return Employee(employee_data['employee_id'], employee_data['location_id'], employee_data['first_name'], employee_data['last_name'], employee_data['region'], employee_data['street_address'], employee_data['city'], employee_data['state'], employee_data['zip_code'], employee_data['dob'], employee_data['ssn'], employee_data['phone_number'], employee_data['position'], employee_data['privilege_level'], employee_data['start_hours'], employee_data['end_hours'], employee_data['wage'], employee_data['email'], employee_data['password_hash'])

		else:

			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
	
			cursor.execute(f"SELECT customer_id, first_name, last_name, login_email, password_hash, region, street_address, city, state, zip_code, phone_number FROM customers WHERE login_email = '{login_email}'")
			user_data = cursor.fetchone()
	
			cursor.close()
			conn.close()

			return User(user_data['customer_id'], user_data['first_name'], user_data['last_name'], user_data['login_email'], user_data['password_hash'], user_data['region'], user_data['street_address'], user_data['city'], user_data['state'], user_data['zip_code'], user_data['phone_number'])
					
	except(mysql.connector.errors.ProgrammingError) as err:
		print(f"Programming Error: {err}")

	except(mysql.connector.errors.OperationalError) as err:
		print(f"Operational Error: {err}")

	except(mysql.connector.errors.Error) as err:
		print(f"General MySQL Error: {err}")
		
	return None

class DecimalEncoder(json.JSONEncoder):
	#Converts Decimal objects from DB into strings

	def default(self, obj):
	
		if isinstance(obj, Decimal):
			return str(obj)
	
		return json.JSONEncoder.default(self, obj)

def get_products():

	all_from_prices = []
	distinct_categories = []

	try:

		my_db = get_db_connection()
		my_cursor = my_db.cursor()

		my_cursor.execute('SELECT * FROM prices')
		my_result = my_cursor.fetchall()
	
		for x in my_result:
			all_from_prices.append(x)

		my_cursor.execute('SELECT DISTINCT category FROM prices')
		my_result = my_cursor.fetchall()
		for x in my_result:
			distinct_categories.append(x[0])

	except(mysql.connector.errors.ProgrammingError) as err:
		print(f"Programming Error: {err}")

	except(mysql.connector.errors.OperationalError) as err:
		print(f"Operational Error: {err}")

	except(mysql.connector.errors.Error) as err:
		print(f"General MySQL Error: {err}")

	finally:
		my_cursor.close()
		my_db.close()

	return [all_from_prices, distinct_categories]

def get_employee_links():

	privilege_level = current_user.get_privilege_level()

	employee_links = [

		[url_for('employee_dashboard'), 'Dashboard'],
		[url_for('announcements'), 'Announcements'],
		[url_for('messages'), 'Messages'],
		[url_for('timesheets'), 'Timesheets'],
		[url_for('update_employee_info'), 'Update Info'],
		[url_for('change_employee_password'), 'Change Password']

	]

	if privilege_level >= 2:
		employee_links.extend([[url_for('inventory'), 'Inventory']])

	if privilege_level >= 3:

		employee_links.extend([

			[url_for('sales'), 'Sales'],
			[url_for('inventory_requests'), 'Inventory Requests'],
			[url_for('customer_orders'), 'Customer Orders']

		])
	if privilege_level == 4:

		employee_links.extend([

			[url_for('make_announcement'), 'Make Announcement'],
			[url_for('job_applicants'), 'Job Applicants'],
			[url_for('view_timesheets'), 'View Timesheets']

		])

	return employee_links

def get_interview_questions():

	questions = [

		'Why did you apply for this job?',
		'What are some of your strengths?',
		'What are a few of your weaknesses?',
		'In your opinion, what is the ideal company?',
		'What makes you want to work for this company?',
		'What makes you the best candidate for this job?',
		'Why should we hire you?',
		'What do you know about our company?',
		'What do you know about our industry?',
		'Tell me about the most difficult decision you have had to make recently. How did you reach a decision?',
		'Give me an example of a time when you made a mistake at work. How did you handle it?',
		'Tell me about a time that you failed. What did you learn from it?',
		'How do you manage stress?',
		'Describe your perfect work environment?',
		'What is your work style?'

	]

	return random.sample(questions, 3)