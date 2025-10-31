#By stringzzz, Ghostwarez Co. 2025
#For populating the Malon dairy Store database with randomized sample data

import random
import secrets
import string
import bcrypt
import datetime

print("Inputting base file")

base_input = ''
with open('MDS_DB_Base_File.sql', 'r') as MDS_DB_BASE:
	base_input = MDS_DB_BASE.read()

with open('MDS_DB2.sql', 'w') as ldb:

	ldb.write(base_input + "\n\n")

	print("Base file added")
	
	class PasswordGen:

		def __init__(self):
			self.chars = {
	
				'lowercase_letters': string.ascii_lowercase,
				'uppercase_letters': string.ascii_uppercase,
				'nums': string.digits,
				'special': "!@#$%^&*?<>"
	
			}

		def genPassword(self):
	
			password = []
			combined_chars = ""

			for k in self.chars.keys():
				password.append(secrets.choice(self.chars[k]))
				combined_chars = f"{combined_chars}{self.chars[k]}"

			for _ in range(12):
				password.append(secrets.choice(combined_chars))

			secrets.SystemRandom().shuffle(password)
			password = "".join(password)

			return [password, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')]

	def genPhoneNumber():
	
		area_code = str(random.randrange(0, 999))
	
		if len(area_code) < 3:
			area_code += '0' * (3 - len(area_code))
	
		four_digits = str(random.randrange(0, 9999))
	
		if len(four_digits) < 4:
			four_digits += '0' * (4 - len(four_digits))
	
		return f"{area_code}555{four_digits}"

	class GenName:

		def __init__(self):
	
			self.first_names = []
			with open("first_names.txt", 'r') as fn_file:
	
				self.first_names = (fn_file.read()).split("\n")
				self.first_names.pop()
				
			self.last_names = []
			with open("last_names.txt", 'r') as ln_file:

				self.last_names = (ln_file.read()).split("\n")
				self.last_names.pop()

		def genName(self):
			return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"

	passGen = PasswordGen()
	nameGen = GenName()

	street_names = [
		'Oak Leaf',
		'Township',
		'Red Cactus',
		'Blue Rock',
		'Grove',
		'Red Cliff',
		'River',
		'Green Leaf',
		'Lake View',
		'Twin Palm',
		'Elder',
		'West',
		'East',
		'Autumn',
		'Winter',
		'Waterfall',
		'Candlestick',
		'Palm',
		'Torchwood',
		'Montgomery',
		'Lantern',
		'Quincy',
		'Lodge',
		'Woodland',
		'Canvas'
	]

	street_parts = [
		'Street',
		'Avenue',
		'Boulevard',
		'Lane',
		'Circle',
		'Road',
		'Path',
		'Trail',
		'Drive'
	]

	cities = [
		'Lemon',
		'Green Acres',
		'Flatlands',
		'Twin Palms',
		'Hot Springs',
		'Wetlands',
		'Waterfall',
		'Red Canyon',
		'Baker',
		'Greenwood',
		'River Rock',
		'Silver Falls',
		'Tangerine',
		'Lime',
		'Orangewood',
		'White Sands',
		'Lake Chelsea',
		'Cliff View',
		'Glenwood',
		'Sandwood'
	]

	class Location():

		def __init__(self, location_id, type, region, street_address, city, state, zip_code, phone_number):
	
			self.location_id = location_id
			self.type = type
			self.region = region
			self.street_address = street_address
			self.city = city
			self.state = state
			self.zip_code = zip_code
			self.phone_number = phone_number

		def getInfoList(self):
			return [self.location_id, self.type, self.region, self.street_address, self.city, self.state, self.zip_code, self.phone_number]

	print("Creating list of locations")

	locations = [

		Location(
			1, 
			'Distribution Center', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'California',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			2, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'California',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			3, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'California',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			4, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Arizona',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			5, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Arizona',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			6, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Nevada',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			7, 
			'Store', 
			'West', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Nevada',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			8, 
			'Distribution Center', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Georgia',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			9, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Georgia',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			10, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Georgia',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			11, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Alabama',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			12, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Alabama',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			13, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Florida',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		),
		Location(
			14, 
			'Store', 
			'East', 
			f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
			f"{random.choice(cities)}",
			'Florida',
			str(random.randrange(10000, 99999)),
			f"{genPhoneNumber()}"	
		)
	]

	print("List of locations created")

	#Get list of stores
	ldb.write("INSERT INTO locations (location_id, type, region, street_address, city, state, zip_code, phone_number) VALUES \n")
	eol = ','

	for index in range(len(locations)):

		temp_location = f"{locations[index].getInfoList()}"
		temp_location = temp_location.replace('[', '(')
		temp_location = temp_location.replace(']', ')')

		if index == len(locations) - 1:
			eol = ';'

		ldb.write(f"\t{temp_location}{eol}\n")

	ldb.write("\n")

	print("Creating inventory list")

	ldb.write("INSERT INTO inventory (location_id, item_id, quantity) VALUES \n")

	end_of_line = ','
	for location_index in range(0, len(locations)):

		for item_id in range(1, 29):

			if item_id == 28 and location_index == len(locations) - 1:
				end_of_line = ';'

			quantity = 0

			if locations[location_index].type == 'Store':
				quantity = random.randint(0, 16)

			elif locations[location_index].type == 'Distribution Center':
				quantity = random.randint(10, 50)

			ldb.write(f"\t({locations[location_index].location_id}, {item_id}, {quantity}){end_of_line}\n")

	ldb.write("\n")

	print("Inventory list created")	

	ids_and_prices = [
		[1, 4.35],
		[2, 4.45],
		[3, 4.45],
		[4, 4.45],
		[5, 4.45],
		[6, 7.86],
		[7, 7.95],
		[8, 8.15],
		[9, 8.30],
		[10, 9.35],
		[11, 6.74],
		[12, 6.50],
		[13, 5.78],
		[14, 5.90],
		[15, 6.10],
		[16, 6.12],
		[17, 6.10],
		[18, 8.90],
		[19, 8.80],
		[20, 8.95],
		[21, 8.95],
		[22, 8.95],
		[23, 5.63],
		[24, 8.95],
		[25, 8.95],
		[26, 8.95],
		[27, 6.20],
		[28, 6.05]
	]

	print("Creating sales")

	ldb.write("INSERT INTO sales (order_id, location_id, item_id, quantity, purchase_price, purchase_time) VALUES \n")

	end_of_line = ','
	sales_id = 1
	for location_index in range(0, len(locations)):

		if locations[location_index].type == 'Distribution Center':
			continue

		for sale in range(1, 15):

			sales_id += 1

			if sale == 14 and location_index == len(locations) - 1:
				end_of_line = ';'

			sale_item = random.choice(ids_and_prices)
			quantity = random.randint(1, 10)
			purchase_time = datetime.datetime(2025, 10, random.randint(1, 19), random.randint(6, 19), random.randint(0, 59), random.randint(0, 59))

			ldb.write(f"\t(NULL, {locations[location_index].location_id}, {sale_item[0]}, {quantity}, {sale_item[1]}, '{purchase_time}'){end_of_line}\n")

	ldb.write("\n")

	print("Sales created")

	class DOB:
	
		def __init__(self):
	
			self.months = range(1, 13)
			self.days = range(1, 30)
			self.years = range(1960, 2007)
	
		def getDob(self):

			year = random.choice(self.years)
			month = random.choice(self.months)

			if len(str(month)) < 2:
				month = '0' + str(month)

			day = random.choice(self.days)

			if len(str(day)) < 2:
				day = '0' + str(day)

			return f"{year}-{month}-{day}"

	class Employee:

		def __init__(self, employee_id, location_id, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, position, privilege_level, start_hours, end_hours, wage):

			self.employee_id = employee_id
			self.location_id = location_id
			self.first_name = first_name
			self.last_name = last_name
			self.region = region
			self.street_address = street_address
			self.city = city
			self.state = state
			self.zip_code = zip_code
			self.dob = dob
			self.ssn = ssn
			self.phone_number = phone_number
			self.position = position
			self.privilege_level = privilege_level
			self.start_hours = start_hours
			self.end_hours = end_hours
			self.wage = wage

		def getInfoList(self):
			return [self.employee_id, self.location_id, self.first_name, self.last_name, self.region, self.street_address, self.city, self.state, self.zip_code, self.dob, self.ssn, self.phone_number, self.position, self.privilege_level, self.start_hours, self.end_hours, self.wage]

	positions = {
		'Distribution Center': [
			['Manager', 40, 60, '4'],
			['Shipping And Receiving', 20, 30, '3']
		],
		'Store': [
			['Manager', 40, 60, '4'],
			['Shipping And Receiving', 20, 30, '3'],
			['Stocker', 16, 20, '2'],
			['Cashier', 16, 22, '1'],
			['Custodian', 16, 20, '1']
		]
	}

	print("Creating list of employees")

	employees = []
	for emp_id in range(40):

		selected_store = random.choice(locations)
		fn, ln = nameGen.genName().split(' ')
		dob = DOB()
		pos = random.choice(positions[selected_store.type])
		start_hours = random.randrange(5, 10)
		end_hours = random.randrange(start_hours + 8, start_hours + 10)
		end_minutes = str(random.choice([0, 30]))

		if len(end_minutes) < 2:
			end_minutes += '0'

		employees.append(
			Employee(
				emp_id + 1,
				selected_store.location_id,
				fn,
				ln,
				selected_store.region,
				f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
				f"{random.choice(cities)}",
				selected_store.state,
				str(random.randrange(10000, 99999)),
				dob.getDob(),
				f"{random.randrange(10, 99)}-{random.randrange(1000, 9999)}",
				genPhoneNumber(),
				pos[0],
				pos[3],
				f"{start_hours}:{end_minutes}",
				f"{end_hours}:{end_minutes}",
				float(f"{random.randrange(pos[1], pos[2])}.{random.randrange(0, 99)}")
			)
		)

	print("List of employees created")

	# Get list of employees
	ldb.write("INSERT INTO employees (employee_id, location_id, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, position, privilege_level, start_hours, end_hours, wage) VALUES \n")
	eol = ','
	for index in range(len(employees)):

		temp_employee = f"{employees[index].getInfoList()}"
		temp_employee = temp_employee.replace('[', '(')
		temp_employee = temp_employee.replace(']', ')')

		if index == len(employees) - 1:
			eol = ';'

		ldb.write(f"\t{temp_employee}{eol}\n")

	ldb.write("\n")

	class EmployeeLogin():

		def __init__(self, email, employee_id, password_hash, created):

			self.email = email
			self.employee_id = employee_id
			self.password_hash = password_hash
			self.created = created

		def getInfoList(self):
			return [self.email, self.employee_id, self.password_hash, self.created]

	def generate_random_timestamp(start_dt, end_dt):

		time_difference = (end_dt - start_dt).total_seconds()
		random_seconds = random.uniform(0, time_difference)
		random_datetime = start_dt + datetime.timedelta(seconds=random_seconds)

		return random_datetime.strftime("%Y-%m-%d %H:%M:%S")

	start_date = datetime.datetime(2020, 1, 1, 0, 0, 0)
	end_date = datetime.datetime(2025, 12, 31, 23, 59, 59)


	print("Creating employee timesheets")

	ldb.write("INSERT INTO employee_timesheets (employee_id, hours_worked, wage, pay_period, created) VALUES \n")
	#FLAG
	end_of_line = ','
	for emp_index in range(0, len(employees)):

		for days in range(0, 9):

			if days == 8 and emp_index == len(employees) - 1:
				end_of_line = ';'

			hours_worked = random.randint(7, 10)
			plus_weekend = 0

			if days > 4:
				plus_weekend = 2

			ldb.write(f"\t({employees[emp_index].employee_id}, {hours_worked}, {employees[emp_index].wage}, 1, '2025-10-{13 + days + plus_weekend}'){end_of_line}\n")

	ldb.write("\n")

	print("Employee timesheets created")

	print("Creating list of employee logins")

	# Get list of employee logins:
	employee_logins = []
	with open('employee_login_log.txt', 'w') as emp_log:

		for employee in employees:

			password, password_hash = passGen.genPassword()

			temp_login = EmployeeLogin(
				f"{employee.first_name[0:3]}{employee.last_name[0:3]}{employee.employee_id}@MalonDairy.fake",
				employee.employee_id,
				password_hash,
				generate_random_timestamp(start_date, end_date)
			)

			employee_logins.append(temp_login)
			emp_log.write(f"{temp_login.email} {password} {employee.position} {employee.location_id}\n")

	print("List of employee logins created")

	ldb.write("INSERT INTO employee_logins (email, employee_id, password_hash, created) VALUES \n")
	eol = ','
	for index in range(len(employee_logins)):

		temp_emp_log = f"{employee_logins[index].getInfoList()}"
		temp_emp_log = temp_emp_log.replace('[', '(')
		temp_emp_log = temp_emp_log.replace(']', ')')

		if index == len(employee_logins) - 1:
			eol = ';'	

		ldb.write(f"\t{temp_emp_log}{eol}\n")

	ldb.write("\n")

	region_state = [
		['West', 'California'],
		['West', 'Arizona'],
		['West', 'Nevada'],
		['East', 'Georgia'],
		['East', 'Alabama'],
		['East', 'Florida'] 
	]

	fake_emails = [
		'techmail',
		'electron',
		'mailman',
		'pidgeonmail',
		'tunnelservice',
		'tubemail',
		'bubblecommunications'
	]

	class Customer:

		def __init__(self, customer_id, first_name, last_name, login_email, password, password_hash, region, street_address, city, state, zip_code, phone_number):

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
			self.password = password

		def getInfoList(self):
			return [self.customer_id, self.first_name, self.last_name, self.login_email, self.password_hash, self.region, self.street_address, self.city, self.state, self.zip_code, self.phone_number]

	print("Creating customer accounts")	

	customers = []
	with open('customer_log.txt', 'w') as cust_log:

		for cust_id in range(18):

			fn, ln = nameGen.genName().split(' ')
			password, password_hash = passGen.genPassword()
			region, state = random.choice(region_state)

			temp_customer = Customer(
				cust_id + 1,
				fn,
				ln,
				f"{fn}{ln[0:1]}{random.randrange(100, 99999)}@{random.choice(fake_emails)}.fake",
				password,
				password_hash,
				region,
				f"{random.randrange(100, 99999)} {random.choice(street_names)} {random.choice(street_parts)}", 
				f"{random.choice(cities)}",
				state,
				str(random.randrange(10000, 99999)),
				genPhoneNumber()
			)

			customers.append(temp_customer)
			cust_log.write(f"{temp_customer.login_email} {password}\n")

	print("Customer accounts created")

	# Get list of customer logins:
	ldb.write("INSERT INTO customers (customer_id, first_name, last_name, login_email, password_hash, region, street_address, city, state, zip_code, phone_number) VALUES \n")
	eol = ','

	for index in range(len(customers)):

		temp_cust_log = f"{customers[index].getInfoList()}"
		temp_cust_log = temp_cust_log.replace('[', '(')
		temp_cust_log = temp_cust_log.replace(']', ')')

		if index == len(customers) - 1:
			eol = ';'

		ldb.write(f"\t{temp_cust_log}{eol}\n")

	ldb.write("\n")

	print("Generating sample reviews")

	order_date = datetime.datetime(2024, 1, 1, 0, 0, 0)
	order_date2 = datetime.datetime(2024, 1, 4, 0, 0, 0)
	order_date3 = datetime.datetime(2025, 3, 8, 0, 0, 0)

	ldb.write(f"INSERT INTO orders (order_id, customer_id, credit_card_number, estimated_cost, shipping_cost, tax, final_price, to_region, to_street_address, to_city, to_state, to_zip_code, order_status, given_review, order_time) VALUES \n\
\t(1, {customers[0].customer_id}, '123123', 8.00, 1.50, 0.80, 10.30, 'West', '123 Candy Cane Lane', 'Silver Rock', 'California', '92555', 'Shipped', '1', '{order_date}'),\n\
\t(2, {customers[1].customer_id}, '654321', 7.00, 1.20, 0.70, 9.90, 'West', '587 Good Street', 'Canyon Town', 'California', '94876', 'Shipped', '1', '{order_date2}'),\n\
\t(3, {customers[2].customer_id}, '123456', 5.00, 1.00, 0.50, 6.50, 'West', '55 Orange Circle', 'Citrus', 'California', '98795', 'Shipped', '1', '{order_date3}');\n\n")

	ldb.write(f"INSERT INTO sales (sales_id, order_id, location_id, item_id, quantity, purchase_price, purchase_time) VALUES \n\
\t({sales_id}, 1, 1, 18, 1, 8.00, '{order_date}'),\n\
\t({sales_id + 1}, 2, 1, 6, 4, 7.00, '{order_date2}'),\n\
\t({sales_id + 2}, 3, 1, 1, 1, 5.00, '{order_date3}');\n\n")

	ldb.write(f"INSERT INTO reviews (review_id, order_id, stars, review_comment, created) VALUES \n\
\t(1, 1, '1', 'I ORDERED CHOCOLATE ICE CREAM AND THEY SENT ME VANILLA, THIS WAS THE WORST DAY OF MY LIFE, I WOULD GIVE ZERO STARS IF I COULD!', '{datetime.datetime(2024, 1, 5, 0, 0, 0)}'),\n\
\t(2, 2, '5', 'Best milk ever!', '{datetime.datetime(2024, 1, 7, 0, 0, 0)}'),\n\
\t(3, 3, '4', 'The yogurt was pretty decent, but still just yogurt.', '{datetime.datetime(2025, 3, 11, 0, 0, 0)}');\n\n")

	print("Sample reviews created")