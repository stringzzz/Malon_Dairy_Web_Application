function displayJobApplicants() {
	
	let outputHtml = '';
	
	applicantInfo.forEach(applicant => {
	
		if (!applicant.viewing) {
			applicant.viewing = false;
		}

		outputHtml += `
			<div class="applicant">
			<p id="applicant-title" onclick="viewApplicant(${applicant.applicant_id})">${applicant.applicant_id} ${applicant.first_name} ${applicant.last_name} ${applicant.created}</p>
		`;

		if (applicant.viewing) {
	
			outputHtml += `
				<div class="applicant-body">
					<p>Region: ${applicant.region}</p>
					<p>Street Address: ${applicant.street_address}</p>
					<p>City/State/Zip: ${applicant.city}, ${applicant.state} ${applicant.zip_code}</p>
					<p>DOB: ${applicant.dob}</p>
					<p>Phone #: ${applicant.phone_number}</p>
					<p>${applicant.interview_question1}</p>
					<p>${applicant.interview_answer1}</p>
					<p>${applicant.interview_question2}</p>
					<p>${applicant.interview_answer2}</p>
					<p>${applicant.interview_question3}</p>
					<p>${applicant.interview_answer3}</p>				
			`;

			if (applicant.applicant_status == 'Submitted') {
	
				outputHtml += `
						<div class='employee-forms'>
							<label for='position'>Employee Position</label>
							<select name='position' id="position">
								<option value="Manager">Manager</option>
								<option value="Shipping And Receiving">Shipping And Receiving</option>
								<option value="Stocker">Stocker</option>
								<option value="Cashier">Cashier</option>
								<option value="Custodian">Custodian</option>
							</select>
							<br>
							<label for='start-hours'>Start Hour</label>
							<select name='start-hours' id="start-hours">
								<option value="5">5</option>
								<option value="6">6</option>
								<option value="7">7</option>
								<option value="8">8</option>
								<option value="9">9</option>
								<option value="10">10</option>
								<option value="11">11</option>
								<option value="12">12</option>
							</select>
							<br>
							<label for="wage">Wage: $</label><input type="text" name="wage" id="wage">
						</div>
						<button class='hire-or-reject-button' onclick="hireEmployee(${applicant.applicant_id})">Hire Employee</button>
						<button class='hire-or-reject-button' onclick="rejectApplication(${applicant.applicant_id})">Reject Application</button>
					</div>
				`;
	
			}
	
		}

		outputHtml += '</div>';
	
	});

	document.querySelector('.job-applicant-content').innerHTML = outputHtml;
}

function viewApplicant(applicantId) {
	
	applicantInfo.forEach(applicant => {
	
		if (applicant.applicant_id == applicantId) {
	
			if (applicant.viewing) {
				applicant.viewing = false;
			} else if (!applicant.viewing) {
				applicant.viewing = true;
			}
	
		}
	
	});
	
	displayJobApplicants();

}

function hireEmployee(applicantId) {

	let applicantData = {

		'applicant_id': applicantId,
		'position': document.getElementById("position").value,
		'start_hours': document.getElementById("start-hours").value,
		'end_hours': Number(document.getElementById("start-hours").value) + 8,
		'wage': document.getElementById("wage").value,
		'status': 'Hired'

	};

	fetch('/process_hire_or_reject', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(applicantData)

	})
	.then(response => response.json())
	.then(result => {
		if (result === 'HIRE_EMPLOYEE_SUCCESS') {

			applicantInfo.forEach(applicant => {

				if (applicant.applicant_id == applicantId) {
					applicant.applicant_status = 'Hired';
				}

			});

			displayJobApplicants();

		} else {
			console.log(`Error: ${result}`);
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function rejectApplication(applicantId) {

	let applicantData = {
		'applicant_id': applicantId,
		'status': 'Rejected'
	};

	fetch('/process_hire_or_reject', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(applicantData)

	})
	.then(response => response.json())
	.then(result => {
		if (result === 'REJECT_EMPLOYEE_SUCCESS') {

			applicantInfo.forEach(applicant => {

				if (applicant.applicant_id == applicantId) {
					applicant.applicant_status = 'Reject';
				}

			});

			displayJobApplicants();

		} else {
			console.log(`Error: ${result}`);
		}

	})
	.catch(error => {
		console.error('Error:', error);
	});

}

displayJobApplicants();