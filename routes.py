from mds_classes_and_functions import *

#By stringzzz, Ghostwarez Co.
#Project start date: 09-19-2025
#Project Completion (Aside from non-Desktop size CSS): 10-30-2025

@app.route('/', methods=['GET'])
def index():
	return render_template('home_page.html')

@app.route('/locations')
def locations():

	#Show list of all store and distribution center locations

	locations = ''
	conn = get_db_connection()
	cursor = conn.cursor(dictionary=True)

	try:
		cursor.execute(f"SELECT type, street_address, city, state, zip_code, phone_number FROM locations ORDER BY region, type")
		locations = cursor.fetchall()

	except(mysql.connector.errors.ProgrammingError) as err:
		print(f"Programming Error: {err}")

	except(mysql.connector.errors.OperationalError) as err:
		print(f"Operational Error: {err}")

	except(mysql.connector.errors.Error) as err:
		print(f"General MySQL Error: {err}")

	finally:
		cursor.close()
		conn.close()

	return render_template('locations.html', locations=json.dumps(locations))

@app.route('/reviews')
def reviews():

	#Give list of all customer reviews

	reviews = ''
	temp_products = get_products()
	categories = temp_products[1]

	conn = get_db_connection()
	cursor = conn.cursor(dictionary=True)

	try:
		cursor.execute(f"SELECT o.order_id FROM orders o INNER JOIN reviews r ON o.order_id = r.order_id WHERE given_review = '1' ORDER BY created DESC")
		order_ids = cursor.fetchall()

		reviews = []
		for order in order_ids:

			cursor.execute(f"SELECT o.order_id, first_name, last_name, review_comment, stars, created FROM orders o INNER JOIN customers c ON o.customer_id = c.customer_id INNER JOIN reviews r ON o.order_id = r.order_id WHERE o.order_id = {order['order_id']};")
			temp_order = cursor.fetchall()[0]

			review = {
				'order_id': temp_order['order_id'],
				'created': f"{temp_order['created']}",
				'customer_name': f"{temp_order['first_name']} {temp_order['last_name'][0]}.",
				'stars': temp_order['stars'],
				'review_comment': temp_order['review_comment']
			}

			cursor.execute(f"SELECT item_name, purchase_price, quantity, category FROM orders o INNER JOIN sales s ON o.order_id = s.order_id INNER JOIN prices p ON p.item_id = s.item_id WHERE o.order_id = {order['order_id']};")
			review['items'] = cursor.fetchall()
			reviews.append(review)

	except(mysql.connector.errors.ProgrammingError) as err:
		print(f"Programming Error: {err}")

	except(mysql.connector.errors.OperationalError) as err:
		print(f"Operational Error: {err}")

	except(mysql.connector.errors.Error) as err:
		print(f"General MySQL Error: {err}")

	finally:
		cursor.close()
		conn.close()

	return render_template('reviews.html', reviews=json.dumps(reviews, cls=DecimalEncoder), categories=json.dumps(categories))

@app.route('/online_store', methods=['GET'])
def online_store():

	#Prevent employee from viewing store when logged in
	if current_user.is_authenticated and current_user.get_type() == 'employee':
		return redirect(url_for('employee_dashboard'))

	temp_products = get_products()
	products = temp_products[0]
	categories = temp_products[1]

	logged_in = 'false'
	if current_user.is_authenticated:
		logged_in = 'true'

	return render_template('online_store_page.html', products=json.dumps(products, cls=DecimalEncoder), categories=json.dumps(categories), logged_in=json.dumps(logged_in), email=json.dumps(current_user.get_id()))

@app.route('/view_cart', methods=['GET'])
def view_cart():

	#Prevent employee from viewing cart when logged in
	if current_user.is_authenticated and current_user.get_type() == 'employee':
		return redirect(url_for('employee_dashboard'))

	return render_template('view_cart.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():

	if current_user and current_user.is_authenticated:
		if current_user.get_type() == 'customer':
			return redirect(url_for('online_store'))
		elif current_user.get_type() == 'employee':
			return redirect(url_for('employee_dashboard'))

	login_message = ''

	if request.method == 'POST':

		login_email = request.form['username']
		password = request.form['password'].encode('utf-8')

		#Detect bad input
		input_violation_found = False
		if re.search(r'@MalonDairy\.fake', login_email):
			input_violation_found = True

		if len(login_email) > 256:
			input_violation_found = True

		if re.search(r'[^a-zA-Z0-9@._]', login_email):
			input_violation_found = True

		if input_violation_found:

			login_message = 'Invalid email address'
			admin_log(f"Bad input for customer login", 3)
			return render_template('customer_login.html', login_message=login_message)
		
		customer = load_user(login_email)

		#Check hashed password matches one in DB
		if customer and bcrypt.checkpw(password, customer.get_pass_hash().encode('utf-8')):
			
			login_user(customer)
			next_page = session.pop('next_url', None)
			admin_log(f"{customer.get_id()} logged in successfully", 1)
			return redirect(next_page or url_for('online_store'))
		
		else:
			
			login_message = 'Invalid username/password combination'
			admin_log(f"{customer.get_id()} failed login attempt", 2)

	return render_template('customer_login.html', login_message=login_message)

@app.route('/logout')
@login_required
def logout():

	#Logout currently logged in customer

	if current_user.get_type() == 'customer':
		logout_user()
		return redirect(url_for('login'))
	
	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))

@app.route('/checkout')
@login_required
def checkout():

	#Checkout customer with shopping cart

	if current_user.get_type() == 'customer':
		return render_template('checkout.html', user_info=json.dumps(current_user.get_user_info()))
	
	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/process_order', methods=['POST'])
@login_required
def process_order():

	#Processes the customer order from checkout

	if current_user.get_type() == 'customer':
		if request.is_json:
			
			cart_data = request.get_json()

			if re.search(r'[^0-9]', cart_data['card_number']) or len(cart_data['card_number']) != 6:
				admin_log(f"{current_user.get_id()} used invalid credit card number for order", 3)
				return json.dumps('Invalid Card Number'), 400

			#Process data to INSERT INTO orders and sales
			order_creator = get_db_connection()
			cursor = order_creator.cursor(dictionary=True)
			user_order_info = current_user.get_user_order_info()
			cursor.execute(f"SELECT location_id FROM locations WHERE region = '{user_order_info['to_region']}' AND type = 'Distribution Center'")
			dist_center_location_id = (cursor.fetchone())['location_id']

			#Calculate costs
			estimated_cost = 0.0
			shipping_cost = 0.0
			for item in cart_data['cart']:
				item_id, quantity = item

				#Filter cart input
				if re.search(r'[^0-9]', str(item_id)) or re.search(r'[^0-9]', str(quantity)):
					admin_log(f"{current_user.get_id()} had invalid items in cart for order", 3)
					return json.dumps('Invalid Cart Input'), 400

				cursor.execute(f"SELECT price, product_weight FROM prices WHERE item_id = {item_id}")
				item_from_db = cursor.fetchone()
				estimated_cost += float(item_from_db['price']) * quantity
				shipping_cost += float(item_from_db['product_weight']) * quantity * 0.20
			
			tax = estimated_cost * 0.10
			final_price = estimated_cost + shipping_cost + tax

			mysql_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			cursor.execute(f"INSERT INTO orders (customer_id, credit_card_number, estimated_cost, shipping_cost, tax, final_price, to_region, to_street_address, to_city, to_state, to_zip_code, order_status, given_review, order_time ) VALUES ({user_order_info['customer_id']}, '{cart_data['card_number']}', {estimated_cost:.2f}, {shipping_cost:.2f}, {tax:.2f}, {final_price:.2f}, '{user_order_info['to_region']}', '{user_order_info['to_street_address']}', '{user_order_info['to_city']}', '{user_order_info['to_state']}', '{user_order_info['to_zip_code']}', 'Ordered', '0', '{mysql_timestamp}')")
			order_creator.commit()

			cursor.execute(f"SELECT order_id FROM orders WHERE order_time = '{mysql_timestamp}'")		
			order_id = (cursor.fetchone())['order_id']
			
			for item in cart_data['cart']:
				item_id, quantity = item
				cursor.execute(f"INSERT INTO sales (order_id, location_id, item_id, quantity, purchase_price, purchase_time) VALUES ({order_id}, {dist_center_location_id}, {item_id}, {quantity}, (SELECT price FROM prices WHERE item_id = {item_id}), '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
			order_creator.commit()

			cursor.close()
			order_creator.close()

			return json.dumps('ORDER_SUCCESS'), 200
		
		else:
			return json.dumps({"error:": 'Request must be JSON'}), 400 
	
	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/customer_info')
@login_required
def customer_info():

	#View customer information

	if current_user.get_type() == 'customer':
		return render_template('customer_info.html', name=json.dumps(current_user.get_name()), email=json.dumps(current_user.get_id()))

	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/view_orders')
@login_required
def view_orders():

	#View the customer's past orders

	if current_user.get_type() == 'customer':

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
		customer_id = current_user.get_customer_id()

		cursor.execute(f"SELECT order_id, DATE_FORMAT(order_time, '%Y-%m-%d %H:%i:%S') AS Date FROM orders WHERE customer_id = {customer_id} ORDER BY order_time DESC")
		order_ids = cursor.fetchall()
		for order in order_ids:
			order['Date'] = f"{order['Date']}"

		orders = []
		reviews = []
		for order in order_ids:

			cursor.execute(f"SELECT credit_card_number, estimated_cost, shipping_cost, tax, final_price, to_region, to_street_address, to_city, to_state, to_zip_code, order_status, given_review FROM orders WHERE order_id = {order['order_id']};")
			order.update(cursor.fetchone())
			order['credit_card_number'] = '***' + order['credit_card_number'][-3:]
			cursor.execute(f"SELECT item_name, purchase_price, quantity FROM orders o INNER JOIN sales s ON o.order_id = s.order_id INNER JOIN prices p ON p.item_id = s.item_id WHERE o.order_id = {order['order_id']};")
			order['items'] = cursor.fetchall()
			orders.append(order)

			cursor.execute(f"SELECT order_id, stars, review_comment, created FROM reviews WHERE order_id = {order['order_id']}")
			review_line = cursor.fetchone()
			if review_line:
				reviews.append(review_line)
				for review in reviews:
					review['created'] = f"{review['created']}"

		return render_template('view_orders.html', orders=json.dumps(orders, cls=DecimalEncoder), email=json.dumps(current_user.get_id()), reviews = json.dumps(reviews))

	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/process_review', methods = ['POST'])
@login_required
def process_review():

	#Process the customer's review of their order only if the order has 'Shipped' status

	if current_user.get_type() == 'customer':

		if request.is_json:
			
			review_data = request.get_json()

			#Detect bad input
			error_found = False
			if re.search(r'[^0-9]', str(review_data['order_id'])):
				admin_log(f"{current_user.get_id()} used invalid order id number", 3)
				return json.dumps('Invalid Order Id Number'), 400 
			
			elif re.search(r'[^1-5]', str(review_data['stars'])):
				admin_log(f"{current_user.get_id()} used invalid star rating number", 3)
				return json.dumps('Invalid Star Rating Number'), 400
			
			review_data['review_comment'] = re.sub(r'[^a-zA-Z0-9 _.?!@#$%&*()[\]+-=/<>:;{},]', '', review_data['review_comment'])

			conn = get_db_connection()
			cursor = conn.cursor()

			try:
				mysql_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				cursor.execute(f"INSERT INTO reviews (order_id, stars, review_comment, created) VALUES ({review_data['order_id']}, '{review_data['stars']}', '{review_data['review_comment']}', '{mysql_timestamp}')")
				cursor.execute(f"UPDATE orders SET given_review = '1' WHERE order_id = {review_data['order_id']}")
				conn.commit()

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
				return json.dumps('Invalid Input'), 400 
			
			else:
				return json.dumps('REVIEW_SUCCESS'), 200
			
		else:
			return json.dumps({"error:": 'Request must be JSON'}), 400 
		
	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/change_info', methods=['GET', 'POST'])
@login_required
def change_info():

	#Change the customer's info, such as address information

	if current_user.get_type() == 'customer':

		messages = []
		form_input = 'None'

		if request.method == 'POST':

			first_name = request.form['first_name']
			last_name = request.form['last_name']
			street_address = request.form['street_address']
			city = request.form['city']
			state = request.form['state']

			region = ''
			if state == 'California' or state == 'Arizona' or state == 'Nevada':
				region = 'West'
			elif state == 'Georgia' or state == 'Alabama' or state == 'Florida':
				region = 'East'

			zip_code = request.form['zip_code']
			phone_number = request.form['phone_number']

			#Detect invalid input lengths and or character sets
			#Note that a real system should allow some different characters for potentially foreign names
			input_violation_found = False
			if len(first_name) > 128:
			
				input_violation_found = True
				messages.append("First name cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the first name field in change customer info: {first_name}", 3)
			
			if re.search(r'[^a-zA-Z\-]', first_name):
			
				input_violation_found = True
				messages.append("First name can only contain letters, and or -")
				admin_log(f"{current_user.get_id()} illegal character in the first name field in change customer info: {first_name}", 3)
			
			if len(last_name) > 128:
			
				input_violation_found = True
				messages.append("Last name cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the last name field in change customer info: {last_name}", 3)
			
			if re.search(r'[^a-zA-Z\-]', last_name):
			
				input_violation_found = True
				messages.append("Last name can only contain letters, and or - ")
				admin_log(f"{current_user.get_id()} illegal character in the last name field in change customer info: {last_name}", 3)
			
			if len(street_address) > 128:
			
				input_violation_found = True
				messages.append("Street address cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the street address field in change customer info: {street_address}", 3)
			
			if re.search(r'[^a-zA-Z0-9 .\-]', street_address):
			
				input_violation_found = True
				messages.append("Street address can only contain alphanumerics, and or space, . -")
				admin_log(f"{current_user.get_id()} illegal character in the street address field in change customer info: {street_address}", 3)
			
			if len(city) > 128:
			
				input_violation_found = True
				messages.append("City cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the city field in change customer info: {city}", 3)
			
			if re.search(r'[^a-zA-Z0-9 \-]', city):
			
				input_violation_found = True
				messages.append("City can only contain alphanumerics, and or space, - ")
				admin_log(f"{current_user.get_id()} illegal character in the city field in change customer info: {city}", 3)
			
			if len(state) > 128:
			
				input_violation_found = True
				messages.append("State cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the state field in change customer info: {state}", 3)
			
			if state != 'California' and state != 'Arizona' and state != 'Nevada' and  state != 'Georgia' and state != 'Alabama' and state != 'Florida':
			
				input_violation_found = True
				messages.append("Invalid state")
				admin_log(f"{current_user.get_id()} illegal state in the state field in change customer info: {state}", 3)
			
			if len(zip_code) > 10:
			
				input_violation_found = True
				messages.append("Zip code cannot exceed 10 digits")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the zip code field in change customer info: {zip_code}", 3)
			
			if re.search(r'[^0-9\-]', zip_code):
			
				input_violation_found = True
				messages.append("Zip code can only contain numeric digits, or -")
				admin_log(f"{current_user.get_id()} illegal character in the zip code field in change customer info: {zip_code}", 3)	
			
			if len(phone_number) > 10:
			
				input_violation_found = True
				messages.append("Phone number cannot exceed 10 digits")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the phone number field in change customer info: {phone_number}", 3)
			
			if re.search(r'[^0-9]', phone_number):
			
				input_violation_found = True
				messages.append("Phone number can only contain numeric digits")
				admin_log(f"{current_user.get_id()} illegal character in the phone number field in change customer info: {phone_number}", 3)
		
			if input_violation_found:
		
				form_input = request.form.to_dict()
				del form_input['state']
				
				return render_template('change_info.html', email=json.dumps(current_user.get_id()), customer_info=json.dumps(current_user.get_all_info()), form_input=json.dumps(form_input), messages=messages)

			current_user.update_info(first_name, last_name, street_address, city, region, state, zip_code, phone_number)
			admin_log(f"{current_user.get_id()} changed their information", 1)
			messages.append('Customer information updated')

		return render_template('change_info.html', email=json.dumps(current_user.get_id()), customer_info=json.dumps(current_user.get_all_info()), form_input=json.dumps(form_input), messages=messages)

	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
	
	#Change customer's password

	if current_user.get_type() == 'customer':

		message = ''

		if request.method == 'POST':

			print("Password change attempt")

			old_password = request.form['old_password']
			new_password = request.form['new_password'] 
			retyped_new_password = request.form['retyped_new_password']

			if new_password == retyped_new_password:

				if current_user.update_password(old_password, new_password):
				
					message = 'Password update successful'
					admin_log(f"{current_user.get_id()} successfully changed password.", 1)
				
				else:
				
					message = 'Password update failed'
					admin_log(f"{current_user.get_id()} failed password change attempt.", 2)

		return render_template('change_password.html', email=json.dumps(current_user.get_id()), message=message)
	
	else:
		admin_log(f"Non-customer {current_user.get_id()} attempted access of customer page", 2)
		return redirect(url_for('unauthorized_access_customer'))
	
@app.route('/customer_registration', methods=['GET', 'POST'])
def customer_registration():

	#Register a new customer

	#Prevent logged in customer or employee from creating an account 
	# that would automatically log in
	if current_user.is_authenticated:

		if current_user.get_type() == 'customer':
			return redirect(url_for('customer_info'))
		
		elif current_user.get_type() == 'employee':
			return redirect(url_for('employee_dashboard'))

	messages = []
	form_input = 'None'

	if request.method == 'POST':

		email = request.form['email']
		password = request.form['password']
		retyped_password = request.form['retyped_password']
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		street_address = request.form['street_address']
		city = request.form['city']
		state = request.form['state']

		region = ''
		if state == 'California' or state == 'Arizona' or state == 'Nevada':
			region = 'West'
		elif state == 'Georgia' or state == 'Alabama' or state == 'Florida':
			region = 'East'

		zip_code = request.form['zip_code']
		phone_number = request.form['phone_number']

		#Detect invalid input lengths and or character sets
		#Note that a real system should allow some different characters for potentially foreign names
		input_violation_found = False
		if '@MalonDairy.fake' in email:
			
			input_violation_found = True
			messages.append("Cannot use employee email to register a customer account")
			admin_log(f"Attempted use of employee email to register a customer account: {email}", 2)
		
		if not(re.match(r'.+@.+', email)):
		
			input_violation_found = True
			messages.append("Invalid email format")
			admin_log(f"Invalid email format in email field: {email}", 2)
		
		if len(email) > 256:
		
			input_violation_found = True
			messages.append("Email cannot exceed 256 characters")
			admin_log(f"Exceeded character limit of 256 in email field: {email}", 3)
		
		if re.search(r'[^a-zA-Z0-9@._]', email):
		
			input_violation_found = True
			messages.append("Email can only contain alphanumerics, and or @ . _")
			admin_log(f"Illegal characters detected in email field: {email}", 3)
		
		if len(first_name) > 128:
		
			input_violation_found = True
			messages.append("First name cannot exceed 128 characters")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the first name field in change customer info: {first_name}", 3)
		
		if re.search(r'[^a-zA-Z\-]', first_name):
		
			input_violation_found = True
			messages.append("First name can only contain letters, and or -")
			admin_log(f"{current_user.get_id()} illegal character in the first name field in change customer info: {first_name}", 3)
		
		if len(last_name) > 128:
		
			input_violation_found = True
			messages.append("Last name cannot exceed 128 characters")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the last name field in change customer info: {last_name}", 3)
		
		if re.search(r'[^a-zA-Z\-]', last_name):
		
			input_violation_found = True
			messages.append("Last name can only contain letters, and or - ")
			admin_log(f"{current_user.get_id()} illegal character in the last name field in change customer info: {last_name}", 3)
		
		if len(street_address) > 128:
		
			input_violation_found = True
			messages.append("Street address cannot exceed 128 characters")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the street address field in change customer info: {street_address}", 3)
		
		if re.search(r'[^a-zA-Z0-9 .\-]', street_address):
		
			input_violation_found = True
			messages.append("Street address can only contain alphanumerics, and or space, . -")
			admin_log(f"{current_user.get_id()} illegal character in the street address field in change customer info: {street_address}", 3)
		
		if len(city) > 128:
		
			input_violation_found = True
			messages.append("City cannot exceed 128 characters")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the city field in change customer info: {city}", 3)
		
		if re.search(r'[^a-zA-Z0-9 \-]', city):
		
			input_violation_found = True
			messages.append("City can only contain alphanumerics, and or space, - ")
			admin_log(f"{current_user.get_id()} illegal character in the city field in change customer info: {city}", 3)
		
		if len(state) > 128:
		
			input_violation_found = True
			messages.append("State cannot exceed 128 characters")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the state field in change customer info: {state}", 3)
		
		if state != 'California' and state != 'Arizona' and state != 'Nevada' and  state != 'Georgia' and state != 'Alabama' and state != 'Florida':
		
			input_violation_found = True
			messages.append("Invalid state")
			admin_log(f"{current_user.get_id()} illegal state in the state field in change customer info: {state}", 3)
		
		if len(zip_code) > 10:
		
			input_violation_found = True
			messages.append("Zip code cannot exceed 10 digits")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the zip code field in change customer info: {zip_code}", 3)
		
		if re.search(r'[^0-9\-]', zip_code):
		
			input_violation_found = True
			messages.append("Zip code can only contain numeric digits, or -")
			admin_log(f"{current_user.get_id()} illegal character in the zip code field in change customer info: {zip_code}", 3)	
		
		if len(phone_number) > 10:
		
			input_violation_found = True
			messages.append("Phone number cannot exceed 10 digits")
			admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the phone number field in change customer info: {phone_number}", 3)
		
		if re.search(r'[^0-9]', phone_number):
		
			input_violation_found = True
			messages.append("Phone number can only contain numeric digits")
			admin_log(f"{current_user.get_id()} illegal character in the phone number field in change customer info: {phone_number}", 3)

	
		if input_violation_found:
	
			form_input = request.form.to_dict()
			del form_input['password']
			del form_input['retyped_password']
			del form_input['state']
			
			return render_template('customer_registration.html', form_input=json.dumps(form_input), messages=messages)

		if password == retyped_password:
		
			conn = get_db_connection()
			cursor = conn.cursor()
		
			try:
		
				cursor.execute(f"SELECT login_email FROM customers WHERE login_email = '{email}'")
				result = cursor.fetchone()
		
				if result:
					messages.append('Email already in use')
		
				else:
		
					password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
					cursor.execute(f"INSERT INTO customers (first_name, last_name, login_email, password_hash, region, street_address, city, state, zip_code, phone_number) VALUES ('{first_name}', '{last_name}', '{email}', '{password_hash}', '{region}', '{street_address}', '{city}', '{state}', '{zip_code}', '{phone_number}')")
					conn.commit()

					customer = load_user(email)

					if customer:
		
						login_user(customer)
						return redirect(url_for('customer_info'))
		
					else:
						print("Failed to load new customer")

			except(mysql.connector.errors.ProgrammingError) as err:
				print(f"Programming Error: {err}")

			except(mysql.connector.errors.OperationalError) as err:
				print(f"Operational Error: {err}")

			except(mysql.connector.errors.Error) as err:
				print(f"General MySQL Error: {err}")

			finally:
				cursor.close()
				conn.close()
				
	return render_template('customer_registration.html', form_input=json.dumps(form_input), messages=messages)

@app.route('/job_applications', methods=['GET'])
def job_applications():

	#Let user apply for a job through a form

	#Prevent employee from viewing job application when logged in
	if current_user.is_authenticated and current_user.get_type() == 'employee':
		return redirect(url_for('employee_dashboard'))

	locations = ''
	conn = get_db_connection()
	cursor = conn.cursor(dictionary=True)

	try:
		cursor.execute(f"SELECT location_id, street_address, city, state, type FROM locations")
		locations = cursor.fetchall()

	except(mysql.connector.errors.ProgrammingError) as err:
		print(f"Programming Error: {err}")

	except(mysql.connector.errors.OperationalError) as err:
		print(f"Operational Error: {err}")

	except(mysql.connector.errors.Error) as err:
		print(f"General MySQL Error: {err}")

	finally:
		cursor.close()
		conn.close()

	return render_template('job_applications.html', locations=json.dumps(locations), interview_questions=json.dumps(get_interview_questions()))

@app.route('/process_submit_application', methods=['POST'])
def process_submit_application():

	#Process the submitted job application

	if request.is_json:

		application_data = request.get_json()
		messages = []

		#Detect invalid input lengths and or character sets
		#Note that a real system should allow some different characters for potentially foreign names
		input_violation_found = False
		if '@MalonDairy.fake' in application_data['email']:
		
			input_violation_found = True
			messages.append("Cannot use employee email to submit a job application")
			admin_log(f"Attempted use of employee email to submit a job application: {application_data['email']}", 1)
		
		if not(re.match(r'.+@.+', application_data['email'])):
		
			input_violation_found = True
			messages.append("Invalid email format")
			admin_log(f"Invalid email format in email field: {application_data['email']}", 2)
		
		if len(application_data['email']) > 256:
		
			input_violation_found = True
			messages.append("Email cannot exceed 256 characters")
			admin_log(f"Exceeded character limit of 256 in email field: {application_data['email']}", 3)
		
		if re.search(r'[^a-zA-Z0-9@._]', application_data['email']):
		
			input_violation_found = True
			messages.append("Email can only contain alphanumerics, and or @ . _")
			admin_log(f"Illegal characters detected in email field: {application_data['email']}", 3)
		
		if len(application_data['first_name']) > 128:
		
			input_violation_found = True
			messages.append("First name cannot exceed 128 characters")
			admin_log(f"Exceeded the char limit of 128 chars in the first name field in job application: {application_data['first_name']}", 3)
		
		if re.search(r'[^a-zA-Z\-]', application_data['first_name']):
		
			input_violation_found = True
			messages.append("First name can only contain letters, and or -")
			admin_log(f"Illegal character in the first name field in job application: {application_data['first_name']}", 3)
		
		if len(application_data['last_name']) > 128:
		
			input_violation_found = True
			messages.append("Last name cannot exceed 128 characters")
			admin_log(f"Exceeded the char limit of 128 chars in the last name field in job application: {application_data['last_name']}", 3)
		
		if re.search(r'[^a-zA-Z\-]', application_data['last_name']):
		
			input_violation_found = True
			messages.append("Last name can only contain letters, and or - ")
			admin_log(f"Illegal character in the last name field in job application: {application_data['last_name']}", 3)
		
		if len(application_data['street_address']) > 128:
		
			input_violation_found = True
			messages.append("Street address cannot exceed 128 characters")
			admin_log(f"Exceeded the char limit of 128 chars in the street address field in job application: {application_data['street_address']}", 3)
		
		if re.search(r'[^a-zA-Z0-9 .\-]', application_data['street_address']):
		
			input_violation_found = True
			messages.append("Street address can only contain alphanumerics, and or space, . -")
			admin_log(f"Illegal character in the street address field in job application: {application_data['street_address']}", 3)
		
		if len(application_data['city']) > 128:
		
			input_violation_found = True
			messages.append("City cannot exceed 128 characters")
			admin_log(f"Exceeded the char limit of 128 chars in the city field in job application: {application_data['city']}", 3)
		
		if re.search(r'[^a-zA-Z0-9 \-]', application_data['city']):
		
			input_violation_found = True
			messages.append("City can only contain alphanumerics, and or space, - ")
			admin_log(f"Illegal character in the city field in job application: {application_data['city']}", 3)
		
		if len(application_data['state']) > 128:
		
			input_violation_found = True
			messages.append("State cannot exceed 128 characters")
			admin_log(f"Exceeded the char limit of 128 chars in the state field in job application: {application_data['state']}", 3)
		
		if application_data['state'] != 'California' and application_data['state'] != 'Arizona' and application_data['state'] != 'Nevada' and  application_data['state'] != 'Georgia' and application_data['state'] != 'Alabama' and application_data['state'] != 'Florida':
		
			input_violation_found = True
			messages.append("Invalid state")
			admin_log(f"Illegal state in the state field in job application: {application_data['state']}", 3)
		
		if len(application_data['zip_code']) > 10:
		
			input_violation_found = True
			messages.append("Zip code cannot exceed 10 digits")
			admin_log(f"Exceeded the char limit of 10 digits in the zip code field in job application: {application_data['zip_code']}", 3)
		
		if re.search(r'[^0-9\-]', application_data['zip_code']):
		
			input_violation_found = True
			messages.append("Zip code can only contain numeric digits, or -")
			admin_log(f"Illegal character in the zip code field in job application: {application_data['zip_code']}", 3)	
		
		if len(application_data['dob']) > 10:
		
			input_violation_found = True
			messages.append("Date of Birth cannot exceed 10 characters")
			admin_log(f"Exceeded the char limit of 10 characters in the Date of Birth field in job application: {application_data['dob']}", 3)
		
		if re.search(r'[^0-9\-]', application_data['dob']):
		
			input_violation_found = True
			messages.append("Date of Birth can only contain numeric digits, or -")
			admin_log(f"Illegal character in the Date of Birth field in job application: {application_data['dob']}", 3)	
		
		if len(application_data['ssn']) > 7:
		
			input_violation_found = True
			messages.append("Social Security # cannot exceed 7 characters")
			admin_log(f"Exceeded the char limit of 7 characters in the Social Security #  field in job application: {application_data['ssn']}", 3)
		
		if re.search(r'[^0-9\-]', application_data['ssn']):
		
			input_violation_found = True
			messages.append("Social Security # can only contain numeric digits, or -")
			admin_log(f"Illegal character in the Social Security # field in job application: {application_data['ssn']}", 3)	
		
		if len(application_data['phone_number']) > 10:
		
			input_violation_found = True
			messages.append("Phone number cannot exceed 10 digits")
			admin_log(f"Exceeded the char limit of 10 digits in the phone number field in job application: {application_data['phone_number']}", 3)
		
		if re.search(r'[^0-9]', application_data['phone_number']):
		
			input_violation_found = True
			messages.append("Phone number can only contain numeric digits")
			admin_log(f"Illegal character in the phone number field in job application: {application_data['phone_number']}", 3)
		
		if len(application_data['interview_question1']) > 256:
		
			input_violation_found = True
			admin_log(f"Exceeded the char limit of 256 chars in the interview question 1 field in job application: {application_data['interview_question1']}", 3)
		
		if re.search(r'[^a-zA-Z,?. ]', application_data['interview_question1']):
		
			input_violation_found = True
			admin_log(f"Illegal character in the interview question 1 field in job application: {application_data['interview_question1']}", 3)
		
		if len(application_data['interview_answer1']) > 1024:
			input_violation_found = True
			messages.append("Interview answer 1 cannot exceed 1024 characters")
			admin_log(f"Exceeded the char limit of 1024 chars in the interview answer 1 field in job application: {application_data['interview_answer1']}", 3)
		
		application_data['interview_answer1'] = re.sub(r'[^a-zA-Z0-9,.?! #$%&*()+-=@;:<>]', '', application_data['interview_answer1'])
		
		if len(application_data['interview_question2']) > 256:
		
			input_violation_found = True
			admin_log(f"Exceeded the char limit of 256 chars in the interview question 2 field in job application: {application_data['interview_question2']}", 3)
		
		if re.search(r'[^a-zA-Z,?. ]', application_data['interview_question2']):
		
			input_violation_found = True
			admin_log(f"Illegal character in the interview question 2 field in job application: {application_data['interview_question2']}", 3)
		
		if len(application_data['interview_answer2']) > 1024:
		
			input_violation_found = True
			messages.append("Interview answer 2 cannot exceed 1024 characters")
			admin_log(f"Exceeded the char limit of 1024 chars in the interview answer 2 field in job application: {application_data['interview_answer2']}", 3)
		
		application_data['interview_answer2'] = re.sub(r'[^a-zA-Z0-9,.?! #$%&*()+-=@;:<>]', '', application_data['interview_answer2'])
		
		if len(application_data['interview_question3']) > 256:
		
			input_violation_found = True
			admin_log(f"Exceeded the char limit of 256 chars in the interview question 3 field in job application: {application_data['interview_question3']}", 3)
		
		if re.search(r'[^a-zA-Z,?. ]', application_data['interview_question3']):
		
			input_violation_found = True
			admin_log(f"Illegal character in the interview question 3 field in job application: {application_data['interview_question3']}", 3)
		
		if len(application_data['interview_answer3']) > 1024:
		
			input_violation_found = True
			messages.append("Interview answer 3 cannot exceed 1024 characters")
			admin_log(f"Exceeded the char limit of 1024 chars in the interview answer 3 field in job application: {application_data['interview_answer3']}", 3)
		
		application_data['interview_answer3'] = re.sub(r'[^a-zA-Z0-9,.?! #$%&*()+-=@;:<>]', '', application_data['interview_answer3'])

		if input_violation_found:
			return json.dumps(messages), 400
		
		application_data['region'] = ''
		if application_data['state'] == 'California' or application_data['state'] == 'Arizona' or application_data['state'] == 'Nevada':
			application_data['region'] = 'West'
		elif application_data['state'] == 'Georgia' or application_data['state'] == 'Alabama' or application_data['state'] == 'Florida':
			application_data['region'] = 'East'

		conn = get_db_connection()
		cursor = conn.cursor()
		
		try:
		
			cursor.execute(f"SELECT email FROM job_applicants WHERE email = '{application_data['email']}'")
			result = cursor.fetchone()
		
			if result:
		
				messages.append('Email already in use')
				return json.dumps(messages), 400
		
			else:

				password_hash = bcrypt.hashpw(application_data['password'].encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
				cursor.execute(f"INSERT INTO job_applicants (email, password_hash, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, interview_question1, interview_answer1, interview_question2, interview_answer2, interview_question3, interview_answer3, applicant_status, apply_location, created) VALUES (\
					'{application_data['email']}',\
					'{password_hash}',\
					'{application_data['first_name']}',\
					'{application_data['last_name']}',\
					'{application_data['region']}',\
					'{application_data['street_address']}',\
					'{application_data['city']}',\
					'{application_data['state']}',\
					'{application_data['zip_code']}',\
					'{application_data['dob']}',\
					'{application_data['ssn']}',\
					'{application_data['phone_number']}',\
					'{application_data['interview_question1']}',\
					'{application_data['interview_answer1']}',\
					'{application_data['interview_question2']}',\
					'{application_data['interview_answer2']}',\
					'{application_data['interview_question3']}',\
					'{application_data['interview_answer3']}',\
					'Submitted',\
					'{application_data['apply_location']}',\
					'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
					
				conn.commit()
				return json.dumps('SUBMIT_APPLICATION_SUCCESS'), 200

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

	else:
		return json.dumps(['Request must be JSON']), 400	

@app.route('/process_check_application', methods=['POST'])
def process_check_application():

	if request.is_json:

		login_data = request.get_json()
		password = (login_data['password']).encode('utf-8')
		messages = []
		hired_messages = []
		applicant_info = ''
		input_violation_found = False

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
		
		try:
		
			cursor.execute(f"SELECT email, password_hash FROM job_applicants WHERE email = '{login_data['email']}'")
			applicant_info = cursor.fetchone()
		
			if not(applicant_info):
				messages.append('Invalid email address')
				return json.dumps(messages), 400

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		if bcrypt.checkpw(password, applicant_info['password_hash'].encode('utf-8')):
			admin_log(f"{login_data['email']} gained access to check job application status", 1)
		
		else:
		
			messages.append('Invalid username/password combination')
			admin_log(f"{login_data['email']} failed access to check job application", 2)
			return json.dumps(messages), 400

		if len(login_data['email']) > 256:
			input_violation_found = True
		
		if re.search(r'[^a-zA-Z0-9@._]', login_data['email']):
			input_violation_found = True
		
		if input_violation_found:
			messages.append('Invalid email address')
			return json.dumps(messages), 400
		
		else:
			applicant_info = ''

			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
		
			try:
		
				cursor.execute(f"SELECT applicant_id, email, first_name, last_name, created, applicant_status FROM job_applicants WHERE email = '{login_data['email']}'")
				applicant_info = cursor.fetchone()

				if applicant_info['applicant_status'] == 'Hired':
					cursor.execute(f"SELECT el.email FROM employees e INNER JOIN employee_logins el ON e.employee_id = el.employee_id INNER JOIN job_applicants ja ON ja.applicant_id = e.application_id WHERE applicant_id = {applicant_info['applicant_id']}")
					employee_email = cursor.fetchone()
					hired_messages.append(f"Congratulations, {applicant_info['first_name']} {applicant_info['last_name']}, you've been hired!")
					hired_messages.append(f"Login from now on using this employee email: {employee_email['email']}")
					hired_messages.append(f"For security reasons, it is recommended that you change your password once you log in.")

				applicant_info['hired_messages'] = hired_messages
				applicant_info['success_message'] = 'CHECK_APPLICATION_SUCCESS'
				applicant_info['created'] = f"{applicant_info['created']}"
				return json.dumps(applicant_info), 200 

			except(mysql.connector.errors.ProgrammingError) as err:
				print(f"Programming Error: {err}")

			except(mysql.connector.errors.OperationalError) as err:
				print(f"Operational Error: {err}")

			except(mysql.connector.errors.Error) as err:
				print(f"General MySQL Error: {err}")

			finally:
				cursor.close()
				conn.close()

	else:
		return json.dumps(['Request must be JSON']), 400

@app.route('/employee_login', methods = ['GET', 'POST'])
def employee_login():

	#Login an employee

	if current_user and current_user.is_authenticated:

		if current_user.get_type() == 'customer':
			return redirect(url_for('online_store'))

		elif current_user.get_type() == 'employee':
			return redirect(url_for('employee_dashboard'))

	login_message = ''

	if request.method == 'POST':

		login_email = request.form['username']
		password = request.form['password'].encode('utf-8')

		#Detect bad input
		input_violation_found = False
		if not(re.search(r'@MalonDairy\.fake', login_email)):
			admin_log(f"Non-employee email address detected in employee login form: {login_email}", 2)
			input_violation_found = True
		
		if len(login_email) > 256:
			admin_log(f"Employee login email with length greater than 256 chars detected: {login_email}", 3)
			input_violation_found = True
		
		if re.search(r'[^a-zA-Z0-9@._]', login_email):
			admin_log(f"Illegal character in employee login email detected: {login_email}", 3)
			input_violation_found = True
		
		if input_violation_found:
	
			login_message = 'Invalid email address'
			return render_template('employee_login.html', login_message=login_message)
		
		employee = load_user(login_email)

		#Check hashed login password with one from DB
		if employee and bcrypt.checkpw(password, employee.get_pass_hash().encode('utf-8')):
	
			login_user(employee)
			next_page = session.pop('next_url', None)
			admin_log(f"{employee.get_id()} logged in successfully", 1)
			return redirect(next_page or url_for('employee_dashboard'))
	
		else:
			login_message = 'Invalid username/password combination'
			admin_log(f"{employee.get_id()} failed login attempt", 2)
	
	return render_template('employee_login.html', login_message=login_message)

@app.route('/employee_dashboard')
@login_required
def employee_dashboard():

	#Employee homepage

	if current_user.get_type() == 'employee':
		return render_template('employee_dashboard.html', name=current_user.get_name(), employee_links=get_employee_links())

	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/announcements')
@login_required
def announcements():

	#View announcements from managers

	if current_user.get_type() == 'employee':

		announcements = ''

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
		
		try:

			cursor.execute(f"SELECT announcement_id, location_id, first_name, last_name, announcement, created FROM announcements a INNER JOIN employees e ON a.employee_id = e.employee_id ORDER BY created DESC")
			temp_announcements = cursor.fetchall()
			announcements = []
		
			for temp_announcement in temp_announcements:
		
				announcement = {
					'announcement_id': temp_announcement['announcement_id'],
					'location_id': temp_announcement['location_id'],
					'name': f"{temp_announcement['first_name']} {temp_announcement['last_name'][0]}.",
					'announcement': temp_announcement['announcement'],
					'created': f"{temp_announcement['created']}"
				}
				announcements.append(announcement)

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		return render_template('announcements.html', employee_links=get_employee_links(), announcements=json.dumps(announcements))

	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/messages', methods = ['GET', 'POST'])
@login_required
def messages():

	#View or send employee messages

	if current_user.get_type() == 'employee':

		if request.method == 'POST':
	
			recipient = request.form['recipient']
			subject = request.form['message_subject']
			body = request.form['body']

			if re.search(r'[^0-9]', recipient):
				return render_template('messages.html', employee_links=get_employee_links(), error_message='Invalid recipient id', inbox=json.dumps([]), sent=json.dumps([]), employees=json.dumps([]), unread_count=json.dumps(0))
			
			#Filter out bad characters
			subject = re.sub(r'[^a-zA-Z0-9 _.?!@#$%&*()[\]+-=/<>:;{},]', '', subject)
			body = re.sub(r'[^a-zA-Z0-9 _.?!@#$%&*()[\]+-=/<>:;{},]', '', body)
			
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)

			try:
				cursor.execute(f"INSERT INTO messages (message_subject, sender, recipient, unread, body, created) VALUES ('{subject}', '{current_user.get_employee_id()}', '{recipient}', '1', '{body}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
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

		inbox = ''
		sent = ''
		employees = ''
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:

			cursor.execute(f"SELECT message_id, message_subject, sender, unread, body, first_name, last_name FROM messages m INNER JOIN employees e ON e.employee_id = m.sender WHERE recipient = {current_user.get_employee_id()} ORDER BY created DESC")
			inbox = cursor.fetchall()

			cursor.execute(f"SELECT message_id, message_subject, recipient, sender, unread, body, first_name, last_name FROM messages m INNER JOIN employees e ON e.employee_id = m.recipient WHERE sender = {current_user.get_employee_id()} ORDER BY created DESC")
			sent = cursor.fetchall()

			cursor.execute(f"SELECT e.employee_id, first_name, last_name, email FROM employees e INNER JOIN employee_logins el ON e.employee_id = el.employee_id ORDER BY first_name, last_name")
			employees = cursor.fetchall()

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		unread_count = 0
		for message in inbox:
			if int(message['unread']):
				unread_count += 1

		return render_template('messages.html', employee_links=get_employee_links(), error_message='', inbox=json.dumps(inbox), sent=json.dumps(sent), employees=json.dumps(employees), unread_count=json.dumps(unread_count))

	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/process_read', methods = ['POST'])
@login_required
def process_read():

	#Process an unread message and mark it as read

	if request.is_json:
		
		if current_user.get_type() == 'employee':

			message_data = request.get_json()

			if re.search(r'[^0-9]', str(message_data)):
				return json.dumps('Invalid Message Number'), 400

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
	
			try:
				cursor.execute(f"UPDATE messages SET unread = '0' WHERE message_id = {message_data}")
				conn.commit()

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
				return json.dumps('Invalid Message Number'), 400
	
			else:
				return json.dumps('READ_SUCCESS'), 200
	
		else:
			admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
			return json.dumps('Invalid Access To Employee Page'), 400

	else:
		admin_log(f"Attempted POST of non-JSON data to process_read", 3)
		return json.dumps('Request must be JSON'), 400

@app.route('/timesheets')
@login_required
def timesheets():

	#View employee timesheets and or add new ones

	if current_user.get_type() == 'employee':

		timesheets = {}
		next_timesheet = {}
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
	
		try:
	
			cursor.execute(f"SELECT hours_worked, wage, pay_period, created FROM employee_timesheets WHERE employee_id = {current_user.get_employee_id()} ORDER BY pay_period DESC")
			temp_timesheets = cursor.fetchall()
	
			for timesheet in temp_timesheets:
				timesheet['created'] = f"{timesheet['created']}"

			for timesheet in temp_timesheets:
				if f"pay_period{timesheet['pay_period']}" not in timesheets:
					timesheets[f"pay_period{timesheet['pay_period']}"] = []
				timesheets[f"pay_period{timesheet['pay_period']}"].append(timesheet)
			
			cursor.execute(f"SELECT MAX(created) AS next_date, DAYNAME(MAX(created)) AS Day FROM employee_timesheets et INNER JOIN employees e ON et.employee_id = e.employee_id WHERE et.employee_id = {current_user.get_employee_id()}")
			next_timesheet = cursor.fetchone()

			new_employee = False
			if next_timesheet['next_date'] == None:
				new_employee = True
				next_timesheet['next_date'] = datetime.now().strftime('%Y-%m-%d')
				next_timesheet['Day'] = datetime.strptime(str(next_timesheet['next_date']), '%Y-%m-%d').strftime("%A")
	
			if next_timesheet['Day'] == 'Friday':
				next_timesheet['next_date'] = f"{(datetime.strptime(str(next_timesheet['next_date']), '%Y-%m-%d') + timedelta(days=3)).date()}"
			else:
				next_timesheet['next_date'] = f"{(datetime.strptime(str(next_timesheet['next_date']), '%Y-%m-%d') + timedelta(days=1)).date()}"

			if not(new_employee):
				cursor.execute(f"SELECT pay_period AS newest_pay_period FROM employee_timesheets WHERE employee_id = {current_user.get_employee_id()} ORDER BY pay_period DESC LIMIT 1")
				newest_pay_period = cursor.fetchone()
				newest_pay_period = int(newest_pay_period['newest_pay_period'])
		
				cursor.execute(f"SELECT COUNT(pay_period) AS num_in_pay_period FROM employee_timesheets WHERE employee_id = {current_user.get_employee_id()} AND pay_period = {newest_pay_period} GROUP BY pay_period")
				num_in_pay_period = cursor.fetchone()
				num_in_pay_period = num_in_pay_period['num_in_pay_period']
	
			else:
				newest_pay_period = 1
				num_in_pay_period = 0

			if (num_in_pay_period == 10):
				next_timesheet['pay_period'] = newest_pay_period + 1
	
			else:
				next_timesheet['pay_period'] = newest_pay_period
	
			cursor.execute(f"SELECT wage FROM employees WHERE employee_id = {current_user.get_employee_id()}")
			temp_wage = cursor.fetchone()
			next_timesheet['wage'] = temp_wage['wage']

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		return render_template('timesheets.html', employee_links=get_employee_links(), timesheets=json.dumps(timesheets, cls=DecimalEncoder), next_timesheet=json.dumps(next_timesheet, cls=DecimalEncoder))

	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/process_timesheet', methods = ['POST'])
@login_required
def process_timesheet():

	#Process a new employee timesheet

	if request.is_json:

		if current_user.get_type() == 'employee':

			timesheet_data = request.get_json()

			#Detect bad input
			if re.search(r'[^0-9.]', str(timesheet_data['hours_worked'])):

				admin_log(f"Invalid hours in employee timesheets detected: {timesheet_data['hours_worked']}", 3)
				return json.dumps('Invalid Hours'), 400

			if not(re.match(r'\d\d\d\d-\d\d-\d\d', timesheet_data['date'])):

				admin_log(f"Invalid date detected in employee timesheets: {timesheet_data['date']}", 3)
				return json.dumps('Invalid Date'), 400

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)

			try:
				cursor.execute(f"SELECT wage FROM employees WHERE employee_id = {current_user.get_employee_id()}")
				wage = cursor.fetchone()
				wage = wage['wage']

				newest_pay_period = ''
				cursor.execute(f"SELECT pay_period AS newest_pay_period FROM employee_timesheets WHERE employee_id = {current_user.get_employee_id()} ORDER BY pay_period DESC LIMIT 1")
				newest_pay_period = cursor.fetchone()
				if newest_pay_period == None:
					newest_pay_period = 1
				else:
					newest_pay_period = int(newest_pay_period['newest_pay_period'])

				cursor.execute(f"SELECT COUNT(pay_period) AS num_in_pay_period FROM employee_timesheets WHERE employee_id = {current_user.get_employee_id()} AND pay_period = {newest_pay_period} GROUP BY pay_period")
				num_in_pay_period = cursor.fetchone()
				if num_in_pay_period == None:
					num_in_pay_period = 0
				else:
					num_in_pay_period = num_in_pay_period['num_in_pay_period']

				if (num_in_pay_period == 10):
					newest_pay_period = newest_pay_period + 1

				cursor.execute(f"INSERT INTO employee_timesheets (employee_id, hours_worked, wage, pay_period, created) VALUES ({current_user.get_employee_id()}, {timesheet_data['hours_worked']}, {wage:.2f}, {newest_pay_period}, '{timesheet_data['date']}')")
				conn.commit()

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
				return json.dumps('Invalid Timesheet'), 400

			else:
				return json.dumps('SUBMIT_TIMESHEET_SUCCESS'), 200

		else:
			admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
			return json.dumps('Invalid Access To Employee Page'), 400	
	else:
		admin_log(f"Attempted POST of non-JSON data to process_timesheet", 3)
		return json.dumps('Request must be JSON'), 400

@app.route('/update_employee_info', methods = ['GET', 'POST'])
@login_required
def update_employee_info():

	#Update the employees info, such as address information

	if current_user.get_type() == 'employee':

		messages = []
		form_input = 'None'

		if request.method == 'POST':
	
			first_name = request.form['first_name']
			last_name = request.form['last_name']
			street_address = request.form['street_address']
			city = request.form['city']
			state = request.form['state']
	
			region = ''
			if state == 'California' or state == 'Arizona' or state == 'Nevada':
				region = 'West'
	
			elif state == 'Georgia' or state == 'Alabama' or state == 'Florida':
				region = 'East'
	
			zip_code = request.form['zip_code']
			phone_number = request.form['phone_number']

			#Detect invalid input lengths and or character sets
			#Note that a real system should allow some different characters for potentially foreign names
			input_violation_found = False
			if len(first_name) > 128:
	
				input_violation_found = True
				messages.append("First name cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the first name field in change customer info: {first_name}", 3)
	
			if re.search(r'[^a-zA-Z\-]', first_name):
	
				input_violation_found = True
				messages.append("First name can only contain letters, and or -")
				admin_log(f"{current_user.get_id()} illegal character in the first name field in change customer info: {first_name}", 3)
	
			if len(last_name) > 128:
	
				input_violation_found = True
				messages.append("Last name cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the last name field in change customer info: {last_name}", 3)
	
			if re.search(r'[^a-zA-Z\-]', last_name):
	
				input_violation_found = True
				messages.append("Last name can only contain letters, and or - ")
				admin_log(f"{current_user.get_id()} illegal character in the last name field in change customer info: {last_name}", 3)
	
			if len(street_address) > 128:
	
				input_violation_found = True
				messages.append("Street address cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the street address field in change customer info: {street_address}", 3)
	
			if re.search(r'[^a-zA-Z0-9 .\-]', street_address):
	
				input_violation_found = True
				messages.append("Street address can only contain alphanumerics, and or space, . -")
				admin_log(f"{current_user.get_id()} illegal character in the street address field in change customer info: {street_address}", 3)
	
			if len(city) > 128:
	
				input_violation_found = True
				messages.append("City cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the city field in change customer info: {city}", 3)
	
			if re.search(r'[^a-zA-Z0-9 \-]', city):
	
				input_violation_found = True
				messages.append("City can only contain alphanumerics, and or space, - ")
				admin_log(f"{current_user.get_id()} illegal character in the city field in change customer info: {city}", 3)
	
			if len(state) > 128:
	
				input_violation_found = True
				messages.append("State cannot exceed 128 characters")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 128 chars in the state field in change customer info: {state}", 3)
	
			if state != 'California' and state != 'Arizona' and state != 'Nevada' and  state != 'Georgia' and state != 'Alabama' and state != 'Florida':
	
				input_violation_found = True
				messages.append("Invalid state")
				admin_log(f"{current_user.get_id()} illegal state in the state field in change customer info: {state}", 3)
	
			if len(zip_code) > 10:
	
				input_violation_found = True
				messages.append("Zip code cannot exceed 10 digits")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the zip code field in change customer info: {zip_code}", 3)
	
			if re.search(r'[^0-9\-]', zip_code):
	
				input_violation_found = True
				messages.append("Zip code can only contain numeric digits, or -")
				admin_log(f"{current_user.get_id()} illegal character in the zip code field in change customer info: {zip_code}", 3)	
	
			if len(phone_number) > 10:
	
				input_violation_found = True
				messages.append("Phone number cannot exceed 10 digits")
				admin_log(f"{current_user.get_id()} exceeded the char limit of 10 digits in the phone number field in change customer info: {phone_number}", 3)
	
			if re.search(r'[^0-9]', phone_number):
				input_violation_found = True
				messages.append("Phone number can only contain numeric digits")
				admin_log(f"{current_user.get_id()} illegal character in the phone number field in change customer info: {phone_number}", 3)
		
			if input_violation_found:
				form_input = request.form.to_dict()
				del form_input['state']
				
				return render_template('update_employee_info.html', employee_info=json.dumps(current_user.get_all_info()), form_input=json.dumps(form_input), messages=messages, employee_links=get_employee_links())

			current_user.update_info(first_name, last_name, street_address, city, region, state, zip_code, phone_number)

			messages.append('Employee information updated')
			admin_log(f"{current_user.get_id()} changed their information", 1)

		return render_template('update_employee_info.html', employee_info=json.dumps(current_user.get_all_info()), form_input=json.dumps(form_input), messages=messages, employee_links=get_employee_links())
	
	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/change_employee_password', methods = ['GET', 'POST'])
@login_required
def change_employee_password():

	#Change the employee password to a new one

	if current_user.get_type() == 'employee':

		message = ''

		if request.method == 'POST':
			print("Password change attempt")

			old_password = request.form['old_password']
			new_password = request.form['new_password'] 
			retyped_new_password = request.form['retyped_new_password']

			if new_password == retyped_new_password:
		
				if current_user.update_password(old_password, new_password):
		
					message = 'Password update successful'
					admin_log(f"{current_user.get_id()} successfully changed password.", 1)
		
				else:
		
					message = 'Password update failed'
					admin_log(f"{current_user.get_id()} failed password change attempt.", 2)

		return render_template('change_employee_password.html', message=message, employee_links=get_employee_links())
	
	else:
		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/inventory')
@login_required
def inventory():

	#View the inventory for different locations (Stockers, Shipping & Receiving, Managers)

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 2:
		
		locations = ''
		inventory = ''
		categories = ''
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:

			cursor.execute(f"SELECT location_id, street_address, city, state FROM locations")
			locations = cursor.fetchall()
			cursor.execute(f"SELECT item_name, category, price, location_id, quantity FROM prices p INNER JOIN inventory i ON p.item_id = i.item_id ORDER BY item_name")
			inventory = cursor.fetchall()
			cursor.execute(f"SELECT DISTINCT category FROM prices")
			categories = cursor.fetchall()

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

		return render_template('inventory.html', employee_links=get_employee_links(), locations=json.dumps(locations), inventory=json.dumps(inventory, cls=DecimalEncoder), categories=json.dumps(categories))

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 2 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/sales')
@login_required
def sales():

	#View sales data (Shipping & Receiving, Managers)

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3:
	
		locations = ''
		sales = ''
		categories = ''
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
	
		try:
	
			cursor.execute(f"SELECT type, location_id, street_address, city, state FROM locations")
			locations = cursor.fetchall()
	
			cursor.execute(f"SELECT item_name, category, purchase_price, location_id, quantity, purchase_time FROM prices p INNER JOIN sales s ON p.item_id = s.item_id ORDER BY purchase_time")
			sales = cursor.fetchall()
			for sale in sales:
				sale['purchase_time'] = str(sale['purchase_time'])
	
			cursor.execute(f"SELECT DISTINCT category FROM prices")
			categories = cursor.fetchall()

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		return render_template('sales.html', employee_links=get_employee_links(), locations=json.dumps(locations), sales=json.dumps(sales, cls=DecimalEncoder), categories=json.dumps(categories))

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/inventory_requests')
@login_required
def inventory_requests():

	#Make inventory requests (Approve if Dist. Center) (Shipping & Receiving, Managers)

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3:

		items = ''
		inventory = ''
		inventory_requests = ''
		location_type = current_user.get_location_type()
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
	
		try:
			cursor.execute(f"SELECT item_id, item_name FROM prices")
			items = cursor.fetchall()
			
			if location_type == 'Store':
	
				cursor.execute(f"SELECT request_id, requesting_location, from_location, request_status, created FROM inventory_requests WHERE requesting_location = {current_user.get_location_id()} ORDER BY created DESC")
				inventory_requests = cursor.fetchall()
	
				for inventory_request in inventory_requests:
					inventory_request['items'] = []
					cursor.execute(f"SELECT ri.item_id, item_name, quantity FROM request_items ri INNER JOIN prices p ON ri.item_id = p.item_id WHERE request_id = {inventory_request['request_id']}")
					inventory_request['items'] = cursor.fetchall()
					inventory_request['created'] = f"{inventory_request['created']}"
	
			elif location_type == 'Distribution Center':
	
				cursor.execute(f"SELECT request_id, requesting_location, from_location, request_status, created FROM inventory_requests ir INNER JOIN locations l ON ir.requesting_location = l.location_id WHERE region = '{current_user.get_region()}' ORDER BY created DESC")
				inventory_requests = cursor.fetchall()
	
				cursor.execute(f"SELECT item_id, quantity FROM inventory WHERE location_id = {current_user.get_location_id()}")
				inventory = cursor.fetchall()
	
				for inventory_request in inventory_requests:
	
					inventory_request['items'] = []
					cursor.execute(f"SELECT ri.item_id, item_name, quantity FROM request_items ri INNER JOIN prices p ON ri.item_id = p.item_id WHERE request_id = {inventory_request['request_id']}")
					inventory_request['items'] = cursor.fetchall()
	
					for request_item in inventory_request['items']:
	
						for item in inventory:
	
							if request_item['item_id'] == item['item_id']:
								request_item['quantity'] = {'inventory': item['quantity'], 'quantity': request_item['quantity']}
								break
	
					inventory_request['created'] = f"{inventory_request['created']}"		
			
		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		return render_template('inventory_requests.html', employee_links=get_employee_links(), items=json.dumps(items), inventory_requests=json.dumps(inventory_requests), location_type=location_type)
	
	else:
		admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))

@app.route('/process_inventory_request', methods = ['POST'])
@login_required
def process_inventory_request():

	#Process an inventory request
	#If Dist. Center, gets inventory update automatically (For sample purposes)

	if request.is_json:
	
		if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3:

			request_data = request.get_json()

			for item in request_data:
	
				if re.search(r'[^0-9]', str(item['item_id'])):
					admin_log(f"Illegal character in inventory request data by employee {current_user.get_id()}: {item['item_id']}", 3)
					return json.dumps('Invalid Inventory Request Number'), 400
	
				if re.search(r'[^0-9]', str(item['quantity'])):
					admin_log(f"Illegal character in inventory request data by employee {current_user.get_id()}: {item['quantity']}", 3)
					return json.dumps('Invalid Inventory Request Number'), 400

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
	
			try:
	
				location_id = current_user.get_location_id()
				location_type = current_user.get_location_type()

				from_location = ''
				request_status = 'Requested'
	
				if location_type == 'Distribution Center':
	
					from_location = 0
					request_status = 'Approved'
	
				elif location_type == 'Store':
	
					region = current_user.get_region()
					cursor.execute(f"SELECT location_id FROM locations WHERE region = '{region}' AND type = 'Distribution Center'")
					from_location = cursor.fetchone()
					from_location = from_location['location_id']

				cursor.execute(f"INSERT INTO inventory_requests (requesting_location, from_location, request_status, created) VALUES ({location_id}, {from_location}, '{request_status}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
				conn.commit()

				cursor.execute(f"SELECT MAX(request_id) AS current_request FROM inventory_requests")
				request_id = cursor.fetchone()
				request_id = request_id['current_request']

				for item in request_data:
					cursor.execute(f"INSERT INTO request_items (request_id, item_id, quantity) VALUES ({request_id}, {item['item_id']}, {item['quantity']})")
					conn.commit()

				#If from_location = 0 (Farm), add all request_items to inventory automatically
				if from_location == 0:
	
					cursor.execute(f"SELECT item_id, quantity FROM inventory WHERE location_id = {location_id}")
					inventory_items = cursor.fetchall()
	
					for item in request_data:
	
						for inventory_item in inventory_items:
	
							if item['item_id'] == inventory_item['item_id']:
								inventory_item['quantity'] = int(inventory_item['quantity']) + int(item['quantity'])

					for inventory_item in inventory_items:
	
						cursor.execute(f"UPDATE inventory SET quantity = {inventory_item['quantity']} WHERE location_id = {location_id} AND item_id = {inventory_item['item_id']}")
						conn.commit()	

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
				return json.dumps('Invalid Inventory Request Number'), 400
	
			else:
				return json.dumps('INVENTORY_REQUEST_SUCCESS'), 200
	
		else:
			admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
			return redirect(url_for('unauthorized_access_employee'))

	else:
		admin_log(f"Attempted POST of non-JSON data to process_inventory_request", 3)
		return json.dumps('Request must be JSON'), 400

@app.route('/approve_inventory_request', methods = ['POST'])
@login_required
def approve_inventory_request():

	#Approve inventory request (Dist. Centers only)

	if request.is_json:

		if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3 and current_user.get_location_type() == 'Distribution Center':

			approve_request_data = request.get_json()

			if re.search(r'[^0-9]', str(approve_request_data)):
				admin_log(f"Illegal character in approve inventory request data by employee {current_user.get_id()}: {approve_request_data}", 3)
				return json.dumps('Invalid Inventory Request Number'), 400
			
			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)

			try:

				cursor.execute(f"SELECT item_id, quantity, requesting_location, from_location FROM inventory_requests ir INNER JOIN request_items ri ON ir.request_id = ri.request_id WHERE ir.request_id = {approve_request_data}")
				request_items = cursor.fetchall()
				from_location = request_items[0]['from_location']
				requesting_location = request_items[0]['requesting_location']
				cursor.execute(f"SELECT item_id, quantity FROM inventory WHERE location_id = {from_location}")
				inventory_items = cursor.fetchall()
				
				for item in request_items:
	
					for inventory_item in inventory_items:
	
						if item['item_id'] == inventory_item['item_id']:
	
							if inventory_item['quantity'] < item['quantity']:
								return json.dumps('Invalid Inventory Request Quantity'), 400
	
							inventory_item['quantity'] = int(inventory_item['quantity']) - int(item['quantity'])

					for inventory_item in inventory_items:
	
						cursor.execute(f"UPDATE inventory SET quantity = {inventory_item['quantity']} WHERE location_id = {from_location} AND item_id = {inventory_item['item_id']}")
						conn.commit()

				cursor.execute(f"SELECT item_id, quantity FROM inventory WHERE location_id = {requesting_location}")
				inventory_items = cursor.fetchall()
	
				for item in request_items:
	
					for inventory_item in inventory_items:
	
						if item['item_id'] == inventory_item['item_id']:
							inventory_item['quantity'] = int(inventory_item['quantity']) + int(item['quantity'])

					for inventory_item in inventory_items:
	
						cursor.execute(f"UPDATE inventory SET quantity = {inventory_item['quantity']} WHERE location_id = {requesting_location} AND item_id = {inventory_item['item_id']}")
						conn.commit()	

				cursor.execute(f"UPDATE inventory_requests SET request_status = 'Approved' WHERE request_id = {approve_request_data}")	
				conn.commit()

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
				return json.dumps('Invalid Inventory Request Number'), 400
	
			else:
				return json.dumps('APPROVE_INVENTORY_REQUEST_SUCCESS'), 200
	
		else:
			admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
			return redirect(url_for('unauthorized_access_employee'))		
	
	else:
		admin_log(f"Attempted POST of non-JSON data to approve_inventory_request", 3)
		return json.dumps('Request must be JSON'), 400

@app.route('/customer_orders')
@login_required
def customer_orders():

	#View and approve customer orders (Only for Dist. Centers)

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3:

		orders = 'No Valid Orders'
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:
			cursor.execute(f"SELECT DISTINCT type FROM locations l INNER JOIN employees e ON l.location_id = e.location_id WHERE l.location_id = {current_user.get_location_id()}")
			location_type = cursor.fetchone()

			if location_type['type'] == 'Distribution Center':

				cursor.execute(f"SELECT order_id, DATE_FORMAT(order_time, '%Y-%m-%d %H:%i:%S') AS Date FROM orders WHERE to_region = '{current_user.get_region()}' ORDER BY order_time DESC")
				order_ids = cursor.fetchall()

				orders = []
				for order in order_ids:

					cursor.execute(f"SELECT credit_card_number, estimated_cost, shipping_cost, tax, final_price, to_region, to_street_address, to_city, to_state, to_zip_code, order_status, given_review FROM orders WHERE order_id = {order['order_id']};")
					order.update(cursor.fetchone())
					order['credit_card_number'] = '***' + order['credit_card_number'][-3:]
	
					cursor.execute(f"SELECT item_name, purchase_price, quantity FROM orders o INNER JOIN sales s ON o.order_id = s.order_id INNER JOIN prices p ON p.item_id = s.item_id WHERE o.order_id = {order['order_id']};")
					order['items'] = cursor.fetchall()
					orders.append(order)

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()
		
		return render_template('customer_orders.html', employee_links=get_employee_links(), orders=json.dumps(orders, cls=DecimalEncoder))

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))

@app.route('/confirm_order', methods = ['POST'])
@login_required
def confirm_order():	

	#Confirm customer orders

	if request.is_json:

		if current_user.get_type() == 'employee' and current_user.get_privilege_level() >= 3:

			message_data = request.get_json()

			if re.search(r'[^0-9]', str(message_data)):
				return json.dumps('Invalid Order Number'), 400

			error_found = False
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)

			try:
				cursor.execute(f"UPDATE orders SET order_status = 'Shipped' WHERE order_id = {message_data}")
				conn.commit()

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
				return json.dumps('Invalid Order Number'), 400

			else:
				return json.dumps('READ_SUCCESS'), 200

		else:
			admin_log(f"Non-employee or employee w/ privilege level < 3 {current_user.get_id()} attempted access of employee page", 2)
			return json.dumps('Invalid Access To Employee Page'), 400

	else:
		admin_log(f"Attempted POST of non-JSON data to confirm_order", 3)
		return json.dumps('Request must be JSON'), 400

@app.route('/make_announcement', methods = ['GET', 'POST'])
@login_required
def make_announcement():

	#Make announcements that all employees can see (Managers only)

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() == 4:	
	
		message = ''
	
		if request.method == 'POST':
	
			body = request.form['body']

			#Filter out bad characters
			body = re.sub(r'[^a-zA-Z0-9 _.?!@#$%&*()[\]+-=/<>:;{},]', '', body)
			
			conn = get_db_connection()
			cursor = conn.cursor(dictionary=True)
	
			try:

				cursor.execute(f"INSERT INTO announcements (employee_id, announcement, created) VALUES ('{current_user.get_employee_id()}', '{body}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
				conn.commit()
				message = 'Announcement submitted successfully.'

			except(mysql.connector.errors.ProgrammingError) as err:
				print(f"Programming Error: {err}")

			except(mysql.connector.errors.OperationalError) as err:
				print(f"Operational Error: {err}")

			except(mysql.connector.errors.Error) as err:
				print(f"General MySQL Error: {err}")

			finally:
				cursor.close()
				conn.close()
		
		return render_template('make_announcement.html', employee_links=get_employee_links(), message=message)

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 4 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))
	
@app.route('/job_applicants')
@login_required
def job_applicants():

	#View job application info and either 'Hire' or 'Reject'
	
	if current_user.get_type() == 'employee' and current_user.get_privilege_level() == 4:

		applicant_info = ''

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
	
		try:

			cursor.execute(f"SELECT applicant_id, first_name, last_name, region, street_address, city, state, zip_code, dob, phone_number, interview_question1, interview_answer1, interview_question2, interview_answer2, interview_question3, interview_answer3, applicant_status, apply_location, created FROM job_applicants WHERE apply_location = {current_user.get_location_id()} AND applicant_status = 'Submitted' ORDER BY created DESC")
			applicant_info = cursor.fetchall()
			for applicant in applicant_info:
				applicant['created'] = f"{applicant['created']}"
				applicant['dob'] = f"{applicant['dob']}"

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		return render_template('job_applicants.html', employee_links=get_employee_links(), applicant_info=json.dumps(applicant_info))

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 4 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))

@app.route('/process_hire_or_reject', methods = ['POST'])
@login_required
def process_hire_or_reject():

	#Process the request to either hire or reject the job applicant	

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() == 4:

		hire_or_reject_data = ''

		if request.is_json:
			hire_or_reject_data = request.get_json()
	
		else:
			admin_log(f"Attempted POST of non-JSON data", 3)
			return json.dumps("POST data must be JSON"), 400

		#Detect bad input
		if re.search(r'[^0-9]', str(hire_or_reject_data['applicant_id'])):

			admin_log(f"{current_user.get_id()} gave invalid applicant ID in process_hire_or_reject {hire_or_reject_data['applicant_id']}", 3)
			return json.dumps('Invalid Applicant Id'), 400

		if hire_or_reject_data['status'] != 'Hired' and hire_or_reject_data['status'] != 'Rejected':

			admin_log(f"{current_user.get_id()} gave invalid applicant status in process_hire_or_reject {hire_or_reject_data['status']}", 3)
			return json.dumps('Invalid applicant status'), 400

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:

			if hire_or_reject_data['status'] == 'Rejected':

				cursor.execute(f"UPDATE job_applicants SET applicant_status = 'Rejected' WHERE applicant_id = {hire_or_reject_data['applicant_id']}")
				conn.commit()
				return json.dumps('REJECT_EMPLOYEE_SUCCESS'), 200
			
			elif hire_or_reject_data['status'] == 'Hired':

				#Detect more bad input
				if hire_or_reject_data['position'] != 'Manager' and hire_or_reject_data['position'] != 'Shipping And Receiving' and hire_or_reject_data['position'] != 'Stocker' and hire_or_reject_data['position'] != 'Cashier' and hire_or_reject_data['position'] != 'Custodian':
	
					admin_log(f"{current_user.get_id()} gave invalid applicant position in process_hire_or_reject {hire_or_reject_data['status']}", 3)
					return json.dumps('Invalid applicant position'), 400
	
				if re.search(r'[^0-9]', str(hire_or_reject_data['start_hours'])):
	
					admin_log(f"{current_user.get_id()} gave invalid applicant start hours in process_hire_or_reject {hire_or_reject_data['start_hours']}", 3)
					return json.dumps('Invalid Applicant Start Hours'), 400
	
				if re.search(r'[^0-9]', str(hire_or_reject_data['end_hours'])):
	
					admin_log(f"{current_user.get_id()} gave invalid applicant end hours in process_hire_or_reject {hire_or_reject_data['end_hours']}", 3)
					return json.dumps('Invalid Applicant End Hours'), 400
	
				if re.search(r'[^0-9.]', str(hire_or_reject_data['wage'])):
					admin_log(f"{current_user.get_id()} gave invalid applicant wage in process_hire_or_reject {hire_or_reject_data['wage']}", 3)
					return json.dumps('Invalid Applicant Wage'), 400

				privilege_level = ''
				if hire_or_reject_data['position'] == 'Manager':
					privilege_level = '4'
	
				elif hire_or_reject_data['position'] == 'Shipping And Receiving':
					privilege_level = '3'
	
				elif hire_or_reject_data['position'] == 'Stocker':
					privilege_level = '2'
	
				elif hire_or_reject_data['position'] == 'Cashier':
					privilege_level = '1'
	
				if hire_or_reject_data['position'] == 'Custodian':
					privilege_level = '1'

				if len(str(hire_or_reject_data['start_hours'])):
					hire_or_reject_data['start_hours'] = f"0{hire_or_reject_data['start_hours']}"
	
				if len(str(hire_or_reject_data['end_hours'])):
					hire_or_reject_data['end_hours'] = f"0{hire_or_reject_data['end_hours']}"	

				cursor.execute(f"UPDATE job_applicants SET applicant_status = 'Hired' WHERE applicant_id = {hire_or_reject_data['applicant_id']}")
				conn.commit()
				
				cursor.execute("SELECT MAX(employee_id) AS employee_id FROM employees")
				temp_employee_id = cursor.fetchone()
				employee_id = temp_employee_id['employee_id'] + 1
				
				cursor.execute(f"SELECT password_hash, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, apply_location FROM job_applicants WHERE applicant_id = {hire_or_reject_data['applicant_id']}")
				applicant_info = cursor.fetchone()

				cursor.execute(f"INSERT INTO employees (employee_id, location_id, first_name, last_name, region, street_address, city, state, zip_code, dob, ssn, phone_number, position, privilege_level, start_hours, end_hours, wage, application_id) VALUES (\
					{employee_id},\
					{applicant_info['apply_location']},\
					'{applicant_info['first_name']}',\
					'{applicant_info['last_name']}',\
					'{applicant_info['region']}',\
					'{applicant_info['street_address']}',\
					'{applicant_info['city']}',\
					'{applicant_info['state']}',\
					'{applicant_info['zip_code']}',\
					'{applicant_info['dob']}',\
					'{applicant_info['ssn']}',\
					'{applicant_info['phone_number']}',\
					'{hire_or_reject_data['position']}',\
					'{privilege_level}',\
					'{hire_or_reject_data['start_hours']}:00:00',\
					'{hire_or_reject_data['end_hours']}:00:00',\
					{float(hire_or_reject_data['wage']):.2f},\
					'{hire_or_reject_data['applicant_id']}')\
				")
				conn.commit()

				cursor.execute(f"INSERT INTO employee_logins (email, employee_id, password_hash, created) VALUES ('{applicant_info['first_name'][0:3]}{applicant_info['last_name'][0:3]}{employee_id}@MalonDairy.fake', {employee_id}, '{applicant_info['password_hash']}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')")
				conn.commit()
	
				return json.dumps('HIRE_EMPLOYEE_SUCCESS'), 200

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()
	
	else:
		admin_log(f"Non-employee or employee w/ privilege level < 4 {current_user.get_id()} attempted access of employee page", 2)
		return json.dumps('Invalid Access To Employee Page'), 400

@app.route('/view_timesheets')
@login_required
def view_timesheets():

	#View the timesheets for all employees at same location (Managers only)
	#Can give the employee a raise

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() == 4:
		
		timesheets = {}
		employees = []
		pay_periods = []
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)
	
		try:
	
			cursor.execute(f"SELECT et.employee_id, hours_worked, et.wage, pay_period, created FROM employee_timesheets et INNER JOIN employees e ON et.employee_id = e.employee_id WHERE et.employee_id = {current_user.get_employee_id()} OR (location_id = {current_user.get_location_id()} AND position != 'Manager') ORDER BY pay_period DESC")
			temp_timesheets = cursor.fetchall()
	
			for timesheet in temp_timesheets:
				timesheet['created'] = f"{timesheet['created']}"

			for timesheet in temp_timesheets:
	
				if f"pay_period{timesheet['pay_period']}" not in timesheets:
					timesheets[f"pay_period{timesheet['pay_period']}"] = []
	
				timesheets[f"pay_period{timesheet['pay_period']}"].append(timesheet)

			cursor.execute(f"SELECT employee_id, CONCAT(first_name, ' ', last_name) AS name FROM employees WHERE employee_id = {current_user.get_employee_id()} OR (location_id = {current_user.get_location_id()} AND position != 'Manager')")
			employees = cursor.fetchall()

			cursor.execute(f"SELECT DISTINCT pay_period FROM employee_timesheets et INNER JOIN employees e ON et.employee_id = e.employee_id WHERE et.employee_id = {current_user.get_employee_id()} OR (location_id = {current_user.get_location_id()} AND position != 'Manager') ORDER BY pay_period DESC")
			temp_pay_periods = cursor.fetchall()
	
			for pay_period in temp_pay_periods:
				pay_periods.append(pay_period['pay_period'])

		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

		self_id = current_user.get_employee_id()

		return render_template('view_timesheets.html', employee_links=get_employee_links(), timesheets=json.dumps(timesheets, cls=DecimalEncoder), self_id=int(self_id), employees=json.dumps(employees), pay_periods=json.dumps(pay_periods))
	
	else:
	
		admin_log(f"Non-employee or employee w/ privilege level < 4 {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))

@app.route('/process_raise_wage', methods = ['POST'])
@login_required
def process_raise_wage():	

	#Manager can give employee a raise by a specified amount

	if current_user.get_type() == 'employee' and current_user.get_privilege_level() == 4:

		raise_wage_data = ''
		if request.is_json:
			raise_wage_data = request.get_json()
		else:
			admin_log(f"Attempted POST of non-JSON data", 3)
			return json.dumps("POST data must be JSON"), 400

		#Detect bad input
		if re.search(r'[^0-9]', str(raise_wage_data['employee_id'])):

			admin_log(f"{current_user.get_id()} gave invalid employee ID in process_raise_wage {raise_wage_data['employee_id']}", 3)
			return json.dumps('Invalid Employee ID'), 400

		if re.search(r'[^0-9.]', str(raise_wage_data['wage_increase'])):

			admin_log(f"{current_user.get_id()} gave invalid character in wage increase in process_raise_wage {raise_wage_data['wage_increase']}", 3)
			return json.dumps('Invalid Wage Increase'), 400

		if float(raise_wage_data['wage_increase']) < 0:
			admin_log(f"{current_user.get_id()} gave negative wage increase in process_raise_wage {raise_wage_data['wage_increase']}", 3)
			return json.dumps('Invalid Wage Increase'), 400

		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		try:

			cursor.execute(f"SELECT wage FROM employees WHERE employee_id = {raise_wage_data['employee_id']}")
			current_wage = cursor.fetchone()
			new_wage = float(current_wage['wage']) + float(raise_wage_data['wage_increase'])

			cursor.execute(f"UPDATE employees SET wage = {new_wage:.2f} WHERE employee_id = {raise_wage_data['employee_id']}")
			conn.commit()

			return json.dumps('RAISE_WAGE_SUCCESS'), 200
		
		except(mysql.connector.errors.ProgrammingError) as err:
			print(f"Programming Error: {err}")

		except(mysql.connector.errors.OperationalError) as err:
			print(f"Operational Error: {err}")

		except(mysql.connector.errors.Error) as err:
			print(f"General MySQL Error: {err}")

		finally:
			cursor.close()
			conn.close()

	else:
		admin_log(f"Non-employee or employee w/ privilege level < 4 {current_user.get_id()} attempted access of employee page", 2)
		return json.dumps('Invalid Access To Employee Page'), 400

@app.route('/employee_logout')
@login_required
def employee_logout():

	#Logout the currently logged in employee

	if current_user.get_type() == 'employee':

		logout_user()
		return redirect(url_for('employee_login'))

	else:

		admin_log(f"Non-employee {current_user.get_id()} attempted access of employee page", 2)
		return redirect(url_for('unauthorized_access_employee'))

@app.route('/unauthorized_access_customer')
def unauthorized_access_customer():

	#This page is for when either an employee or a logged out user 
	# tries to access a customer specific page

	return render_template('unauthorized_access_page.html', type='Customer')

@app.route('/unauthorized_access_employee')
def unauthorized_access_employee():

	#This page is for when either a customer or a logged out user 
	# tries to access an employee specific page

	return render_template('unauthorized_access_page.html', type='Employee')	