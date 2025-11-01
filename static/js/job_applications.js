function displayApplicationForm() {
	
	let outputHtml = `
		<h1>Job Application</h1>
		<div class="application-form">
			<div class="text-input"><label for="email">Email</label><input type="text" name="email" id="email" maxlength=256 required></div>
			<div class="text-input"><label for="password">Password</label><input type="password" name="password" id="password" required></div>			
			<div class="outer-password-bar">
				<div class="inner-password-bar"></div>
			</div>
			<p class="strength"></p>
			<div class="password-policy"></div>
			<div class="text-input"><label for="retyped_password">Retype Password</label><input type="password" name="retyped_password" id="retyped_password"></div>
			<div class="matching-passwords"></div>
			<div class="text-form"><label for="first_name">First Name</label><input type="text" name="first_name" id="first_name" maxlength=128 required></div>
			<div class="text-form"><label for="last_name">Last Name</label><input type="text" name="last_name" id="last_name" maxlength=128 required></div>
			<div class="text-form"><label for="street_address">Street Address</label><input type="text" name="street_address" id="street_address" maxlength=128 required></div>
			<div class="text-form"><label for="city">City</label><input type="text" name="city" id="city" maxlength=128 required></div>
			<div class="select-form"><label for="state">State</label>
			<select name="state" id="state">
				<option value="California">California</option>
				<option value="Arizona">Arizona</option>
				<option value="Nevada">Nevada</option>
				<option value="Georgia">Georgia</option>
				<option value="Alabama">Alabama</option>
				<option value="Florida">Florida</option>
			</select></div>
			<div class="select-applying-to"><label for="applying-to">Applying To Location: </label>
			<select name="applying_to" id="applying_to">
			`;

	locations.forEach(location => {
		outputHtml += `<option value='${location.location_id}'>${location.type}: ${location.street_address} ${location.city}, ${location.state}</option>`;
	});

	outputHtml += `
			</select></div>
			<div class="text-form"><label for="zip_code">Zip Code</label><input type="text" name="zip_code" id="zip_code" maxlength=10 required></div>
			<div class="text-form"><label for="dob">Date of Birth</label><input type="date" name="dob" id="dob" required></div>
			<div class="text-form"><label for="ssn">Social Security #</label><input type="text" name="ssn" id="ssn" maxlength=7 required></div>
			<div class="text-form"><label for="phone_number">Phone Number</label><input type="text" name="phone_number" id="phone_number" maxlength=10 required></div>
			<div class="interview-question">
				<p id="question1">${interviewQuestions[0]}</p>
				<textarea name="answer1" id="answer1" class="interview-answer" maxlength=1024></textarea><br>
			</div>
			<div class="interview-question">
				<p id="question2">${interviewQuestions[1]}</p>
				<textarea name="answer2" id="answer2" class="interview-answer" maxlength=1024></textarea><br>
			</div>	
			<div class="interview-question">
				<p id="question3">${interviewQuestions[2]}</p>
				<textarea name="answer3" id="answer3" class="interview-answer" maxlength=1024></textarea><br>
			</div>		
			<button onclick="submitApplication()" id="submit-application-button">Submit Application</button>
			<div id="error-messages"></div>	
		</div>
	`;

	document.querySelector('.job-application-forms').innerHTML = outputHtml;

	document.getElementById('submit-application-button').disabled = true;

	document.getElementById("password").addEventListener("input", checkPassword);
	document.getElementById("retyped_password").addEventListener("input", checkPassword);

}

function checkPassword() {

	pass = document.getElementById("password").value;

	checkOutputHtml = '';

	const invalid_special_pattern = /[^a-zA-Z0-9!@$%^&*?<>]/g
	if (invalid_special_pattern.test(pass)) {

		checkOutputHtml += '<p>Must not contain special characters other than: ! @ # $ % ^ & * ? < ></p>';
		bar = document.querySelector('.inner-password-bar');
		strength = document.querySelector('.strength');
		bar.style.width = "0";
		strength.innerHTML = "Invalid";	
		document.querySelector('.password-policy').innerHTML = checkOutputHtml;	

		return;

	}
	
	pass_score = 0;

	pass_len = pass.length;
	if (pass_len >= 16) {
		pass_score++;
	} else {
		checkOutputHtml = "<p>Must be at least 16 characters</p>";
	}

	const lowercase_pattern = /[a-z]/g;
	if (lowercase_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 lowercase letter</p>";
	}

	const uppercase_pattern = /[A-Z]/g;
	if (uppercase_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 uppercase letter</p>";
	}

	const digit_pattern = /[0-9]/g;
	if (digit_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 digit</p>";
	}

	const special_pattern = /[!@$%^&*?<>]/g;
	if (special_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 special character: ! @ # $ % ^ & * ? < ></p>";
	}

	bar = document.querySelector('.inner-password-bar');
	strength = document.querySelector('.strength');
	if (pass_score == 0) {
		bar.style.width = "0";
		strength.innerHTML = "Very Weak";
	}

	else if (pass_score == 1) {
		bar.style.width = "20%";
		bar.style.backgroundColor = "red";
		strength.innerHTML = "Weak";
	}

	else if (pass_score == 2) {
		bar.style.width = "40%";
		bar.style.backgroundColor = "orange";
		strength.innerHTML = "Somewhat Weak";
	}

	else if (pass_score == 3) {
		bar.style.width = "60%";
		bar.style.backgroundColor = "yellow";
		strength.innerHTML = "Moderate";
	}

	else if (pass_score == 4) {
		bar.style.width = "80%";
		bar.style.backgroundColor = "yellowgreen";
		strength.innerHTML = "Less Weak";
	}

	else if (pass_score == 5) {
		bar.style.width = "100%";
		bar.style.backgroundColor = "green";
		strength.innerHTML = "Strong";
	}

	retypedPass = document.getElementById('retyped_password').value;
	if (pass != retypedPass) {
		document.querySelector('.matching-passwords').innerHTML = '<p>Retyped password must match password</p>';
	} else {
		document.querySelector('.matching-passwords').innerHTML = '';
	}


	document.querySelector('.password-policy').innerHTML = checkOutputHtml;
	if (checkOutputHtml.length > 0 || pass != retypedPass) {
		document.getElementById('submit-application-button').disabled = true;
	} else {
		document.getElementById('submit-application-button').disabled = false;
	}

}

function displayCheckStatus() {

	let outputHtml = `
		<div class='login-form'>
			<input type="text" name="email" id="email" placeholder="Email" maxlength=256><br>
			<input type="password" name="password" id="password" placeholder="Password"><br>
			<button id="check-status-button" onclick="checkApplicationStatus()">Check Application Status</button>
			<div id="error-messages" class=""></div>
		</div>
	`;

	document.querySelector('.job-application-forms').innerHTML = outputHtml;
}

function submitApplication() {

	let applicationData = {

		'email': document.getElementById('email').value,
		'password': document.getElementById('password').value,
		'first_name': document.getElementById('first_name').value,
		'last_name': document.getElementById('last_name').value,
		'street_address': document.getElementById('street_address').value,
		'city': document.getElementById('city').value,
		'state': document.getElementById('state').value,
		'apply_location': document.getElementById('applying_to').value,
		'zip_code': document.getElementById('zip_code').value,
		'dob': document.getElementById('dob').value,
		'ssn': document.getElementById('ssn').value,
		'phone_number': document.getElementById('phone_number').value,
		'interview_question1': document.getElementById('question1').innerHTML,
		'interview_answer1': document.getElementById('answer1').value,
		'interview_question2': document.getElementById('question2').innerHTML,
		'interview_answer2': document.getElementById('answer2').value,
		'interview_question3': document.getElementById('question3').innerHTML,
		'interview_answer3': document.getElementById('answer3').value,				

	};

	fetch('/process_submit_application', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(applicationData)

	})
	.then(response => response.json())
	.then(result => {

		if (result === 'SUBMIT_APPLICATION_SUCCESS') {

			displayApplicationForm();
			document.getElementById('error-messages').innerHTML = 'Job Application Successfully Submitted';
			document.getElementById('error-messages').className = 'error-messages';

		} else {

			errorMessages = '';
			result.forEach(message => {
				errorMessages += `<p>${message}</p>`;
			});

			document.getElementById('error-messages').innerHTML = errorMessages;
			document.getElementById('error-messages').className = 'error-messages';	

		}

	})
	.catch(error => {
		console.error('Error:', error);
	});

}

function checkApplicationStatus() {

	let loginInfo = {
		'email': document.getElementById('email').value,
		'password': document.getElementById('password').value
	};

	fetch('/process_check_application', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(loginInfo)

	})
	.then(response => response.json())
	.then(result => {
		if (result['success_message'] === 'CHECK_APPLICATION_SUCCESS') {

			let outputHtml = `
				<p>Applicant ID#${result.applicant_id} ${result.created}</p>
				<p>${result.first_name} ${result.last_name}</p>
				<p>${result.email}</p>
				<p>Application status: ${result.applicant_status}</p>
			`;

			result.hired_messages.forEach(message => {
				outputHtml += `<p>${message}</p>`
			});

			document.querySelector('.job-application-forms').innerHTML = outputHtml;

		} else {

			errorMessages = '';
			result.forEach(message => {
				errorMessages += `<p>${message}</p>`;
			});

			document.getElementById('error-messages').innerHTML = errorMessages;
			document.getElementById('error-messages').className = 'error-messages';	

		}

	})
	.catch(error => {
		console.error('Error:', error);
	});
	
}

displayApplicationForm();
