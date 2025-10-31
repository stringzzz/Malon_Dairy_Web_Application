--By stringzzz, Ghostwarez Co.

--Project start date: 09-19-2025

--Project Completion (Aside from non-Desktop size CSS): 10-30-2025


This is a Full Stack application for a sample website.


It has HTML/CSS/JavaScript for the frontend, and Python and MySQL for the backend. Further below will be an explanation on what to install and what to run to get it set up and running. Note that this whole setup is intended for Linux, specifically it has only been tested on Ubuntu.


The website is for a fictional dairy store chain called Malon Dairy Store.


It includes customer login/registration, the ability to load up a shopping cart
and place an order with a fictional credit card #. Once the order is set to 'Shipped' by an employee, the customer can place a review on the order.


Additionally, the user can put in a job application. There is an employee login, once logged in employees with certain positions have access to a certain amount of features. Managers have full access, and can hire job applicants. Other employee actions are to put in inventory requests, approve orders, send messages to each other, and much more.


There are many more details I'm not mentioning, but the website does fully work with all of the features one might want for a mostly realistic store chain website. Also, to point out, there are certain security flaws in the system. Keeping in mind that this is just for sample purposes, obviously you would not
want to be sending passwords and user information in cleartext, but to keep it simple this is done in this system. While all form input is checked for bad characters and any of this activity is logged in a file, there may also be plenty of flaws involving this that I overlooked.


Note: The only part currently incomplete is the CSS. It works for desktop-sized screens, but currently it does not have code for other screen sizes, such as for phone and tablet sized screens. This too will be finished soon enough.


---------------------------------------------------

Dependencies:

apache2

mysql

venv (Used to install Flask and mysql-connector-python under a virtual environment)

python3-flask

mysql-connector-python


Some .conf files for apache2 may need to be edited in order for this to work properly, especially if using the '/var/www/html/' directory on your system.


----------------------------------------------------

Setup:

//Install apache2:

$ sudo apt-get install apache2


//Install mysql:

$ sudo apt install mysql-server

$ sudo mysql

mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '************';

mysql> FLUSH PRIVILEGES;


//Install python modules:

$ python3 -m venv myenv

$ source myenv/bin/activate

$ pip3 install flask

$ pip3 install mysql-connector-python

$ deactivate


//Generate the SQL code for setting up the DB:

//This also generates the list of sample customer and employee login info in 2 separate files

(cd to the correct directory 'DB_Gen_Code')

$ python3 MDS_Table_Gen.py


$ mysql -u root -p

(Log in as your MySQL user, while in the correct directory)

MySQL: source MDS_DB2.sql

MySQL: source MadCow.sql


Replace 'your_path_here' in 'mds_classes_and_functions.py' and 
'copy_and_run.sh' with your own path on your system to the files for this application.


//Finally, copy all the files to /var/www/html/ and run the application with one script:

$ bash copy_and_run.sh

