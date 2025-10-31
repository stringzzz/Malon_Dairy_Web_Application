-- -----------------------------------------------------
-- Schema MalonDairyStore
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS MalonDairyStore ;
USE MalonDairyStore ;

-- -----------------------------------------------------
-- Table MalonDairyStore.locations" 
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.locations (
	location_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	type VARCHAR(64) NOT NULL,
	region CHAR(4) NOT NULL,
	street_address VARCHAR(128) NOT NULL,
	city VARCHAR(128) NOT NULL,
	state VARCHAR(128) NOT NULL,
	zip_code VARCHAR(10) NOT NULL,
	phone_number VARCHAR(10) NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.employees" 
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.employees (
	employee_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	location_id INT NOT NULL,
	first_name VARCHAR(128) NOT NULL,
	last_name VARCHAR(128) NOT NULL,
	region CHAR(4) NOT NULL,
	street_address VARCHAR(128) NOT NULL,
	city VARCHAR(128) NOT NULL,
	state VARCHAR(128) NOT NULL,
	zip_code VARCHAR(10) NOT NULL, 
	dob DATE NOT NULL,
	ssn CHAR(7) NOT NULL,
	phone_number CHAR(10) NOT NULL,
	position VARCHAR(64) NOT NULL,
	privilege_level CHAR(1) NOT NULL,
	start_hours TIME NOT NULL,
	end_hours TIME NOT NULL,
	wage DECIMAL(10,2) NOT NULL,
	application_id INT
);


-- -----------------------------------------------------
-- Table MalonDairyStore.employee_timesheets"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.employee_timesheets (
	timesheet_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	employee_id INT NOT NULL,
	hours_worked DECIMAL(10,1) NOT NULL,
	wage DECIMAL(10,2) NOT NULL,
	pay_period INT NOT NULL,
	created DATE NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.employee_logins" 
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.employee_logins (
	email VARCHAR(128) PRIMARY KEY NOT NULL,
	employee_id INT NOT NULL,
	password_hash VARCHAR(64) NOT NULL,
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.announcements"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.announcements (
	announcement_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	employee_id INT NOT NULL,
	announcement VARCHAR(1024),
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.messages"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.messages (
	message_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	message_subject VARCHAR(256) NOT NULL,
	sender INT NOT NULL,
	recipient INT NOT NULL,
	unread CHAR(1) NOT NULL,
	body VARCHAR(1024) NOT NULL,
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.job_applicants"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.job_applicants (
	applicant_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	email VARCHAR(128) NOT NULL,
	password_hash VARCHAR(64) NOT NULL,
	first_name VARCHAR(128) NOT NULL,
	last_name VARCHAR(128) NOT NULL,
	region CHAR(4) NOT NULL,
	street_address VARCHAR(128) NOT NULL,
	city VARCHAR(128) NOT NULL,
	state VARCHAR(128) NOT NULL,
	zip_code VARCHAR(10) NOT NULL,  
	dob DATE NOT NULL,
	ssn CHAR(7) NOT NULL,
	phone_number CHAR(10) NOT NULL,
	interview_question1 VARCHAR(256) NOT NULL,
	interview_answer1 VARCHAR(1024) NOT NULL,
	interview_question2 VARCHAR(256) NOT NULL,
	interview_answer2 VARCHAR(1024) NOT NULL,
	interview_question3 VARCHAR(256) NOT NULL,
	interview_answer3 VARCHAR(1024) NOT NULL,		
	applicant_status VARCHAR(64) NOT NULL,
	apply_location INT NOT NULL,
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.prices" 
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.prices (
	item_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	item_name VARCHAR(128) NOT NULL,
	image_url VARCHAR(512) NOT NULL,
	category VARCHAR(128) NOT NULL,
	product_weight DECIMAL(10,2) NOT NULL,
	price DECIMAL(10,2) NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.inventory"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.inventory (
	inventory_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	location_id INT NOT NULL,
	item_id INT NOT NULL,
	quantity INT NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.customers"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.customers (
	customer_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	first_name VARCHAR(128) NOT NULL,
	last_name VARCHAR(128) NOT NULL,
	login_email VARCHAR(256) NOT NULL,
	password_hash VARCHAR(64) NOT NULL,
	region CHAR(4) NOT NULL,
	street_address VARCHAR(128) NOT NULL,
	city VARCHAR(128) NOT NULL,
	state VARCHAR(128) NOT NULL,
	zip_code VARCHAR(10) NOT NULL,
	phone_number CHAR(10) NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.orders"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.orders (
	order_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	customer_id INT NOT NULL,
	credit_card_number CHAR(6) NOT NULL,
	estimated_cost DECIMAL(10, 2) NOT NULL,
	shipping_cost DECIMAL(10, 2) NOT NULL,
	tax DECIMAL(10, 2) NOT NULL,
	final_price DECIMAL(10, 2) NOT NULL,
	to_region CHAR(4) NOT NULL,
	to_street_address VARCHAR(128) NOT NULL,
	to_city VARCHAR(128) NOT NULL,
	to_state VARCHAR(128) NOT NULL,
	to_zip_code VARCHAR(10) NOT NULL,
	order_status CHAR(7) NOT NULL,
	given_review CHAR(1) NOT NULL,
	order_time DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.reviews"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.reviews (
	review_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	order_id INT NOT NULL,
	stars CHAR(1) NOT NULL,
	review_comment VARCHAR(1024),
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.sales"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.sales (
	sales_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	order_id INT,
	location_id INT NOT NULL,
	item_id INT NOT NULL,
	quantity INT NOT NULL,
	purchase_price DECIMAL(10,2) NOT NULL,
	purchase_time DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.inventory_requests"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.inventory_requests (
	request_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	requesting_location INT NOT NULL,
	from_location INT NOT NULL,
	request_status VARCHAR(32),
	created DATETIME NOT NULL
);


-- -----------------------------------------------------
-- Table MalonDairyStore.request_items"
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS MalonDairyStore.request_items (
	request_item_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	request_id INT NOT NULL,
	item_id INT NOT NULL,
	quantity INT NOT NULL
);


INSERT INTO prices (item_name, image_url, category, product_weight, price) VALUES 
	('Vanilla Yogurt', '/static/vanilla_yogurt.png', 'Yogurt', 2, 4.35),
	('Peach Yogurt', '/static/peach_yogurt.png', 'Yogurt', 2, 4.45),
	('Blueberry Yogurt', '/static/blueberry_yogurt.png', 'Yogurt', 2, 4.45),
	('Strawberry Yogurt', '/static/strawberry_yogurt.png', 'Yogurt', 2, 4.45),
	('Mango Yogurt', '/static/mango_yogurt.png', 'Yogurt', 2, 4.45),
	('Milk', '/static/milk.png', 'Milk', 3.5, 7.86),
	('Low Fat Milk', '/static/low_fat_milk.png', 'Milk', 3.5, 7.95),
	('Reduced Fat Milk', '/static/reduced_fat_milk.png', 'Milk', 3.5, 8.15),
	('Non Fat Milk', '/static/non_fat_milk.png', 'Milk', 3.5, 8.30),	
	('Buttermilk', '/static/buttermilk.png', 'Milk', 3, 9.35),
	('Salted Butter', '/static/salted_butter.png', 'Butter', 2.5, 6.74),
	('Unsalted Butter', '/static/unsalted_butter.png', 'Butter', 2.5, 6.50),
	('Provolone Cheese', '/static/provolone_cheese.png', 'Cheese', 3, 5.78),
	('Cheddar Cheese', '/static/cheddar_cheese.png', 'Cheese', 3, 5.90),
	('Mozarella Cheese', '/static/mozarella_cheese.png', 'Cheese', 3, 6.10),
	('Pepperjack Cheese', '/static/pepperjack_cheese.png', 'Cheese', 3, 6.12),
	('Jalapeno Cheese', '/static/jalapeno_cheese.png', 'Cheese', 3, 6.10),
	('Chocolate Ice Cream', '/static/chocolate_ice_cream.png', 'Ice Cream', 4, 8.90),
	('Vanilla Ice Cream', '/static/vanilla_ice_cream.png', 'Ice Cream', 4, 8.80),
	('Mint Chocolate Chip Ice Cream', '/static/mint_chocolate_chip_ice_cream.png', 'Ice Cream', 4, 8.95),
	('Neopolitan Ice Cream', '/static/neopolitan_ice_cream.png', 'Ice Cream', 4, 8.95),
	('Rainbow Sherbert Ice Cream', '/static/rainbow_sherbert_ice_cream.png', 'Ice Cream', 4, 8.95),
	('Sour Cream', '/static/sour_cream.png', 'Cream', 3, 5.63),
	('Vanilla Coffee Creamer', '/static/vanilla_coffee_creamer.png', 'Cream', 3.5, 8.95),
	('Mocha Coffee Creamer', '/static/mocha_coffee_creamer.png', 'Cream', 3.5, 8.95),
	('Caramel Coffee Creamer', '/static/caramel_coffee_creamer.png', 'Cream', 3.5, 8.95),
	('Cream Cheese', '/static/cream_cheese.png', 'Cheese', 2.5, 6.20),
	('Cottage Cheese', '/static/cottage_cheese.png', 'Cheese', 3, 6.05);
