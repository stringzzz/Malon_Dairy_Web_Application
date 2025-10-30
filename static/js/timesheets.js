function displayTimeSheets() {

	let outputHtml = `
		<p>${nextTimesheet.next_date} Pay Period: ${nextTimesheet.pay_period} Wage: $${Number(nextTimesheet.wage).toFixed(2)}</p>
		<label for='new-timesheet'>Hours Worked: </label>
		<input type='text' name='new-timesheet' id='new-timesheet'>
		<button id='submit-timesheet-button' onclick='submitTimesheet()'>Submit Timesheet</button>
	`;

	let pay_period = 1;
	while(timesheets['pay_period' + String(pay_period)]) {

			outputHtml += `
				<div class='timesheet-group'>
			`;
	
			timesheets['pay_period' + String(pay_period)].forEach(timesheet => {

				outputHtml += `
					<p>${timesheet.created} Pay Period: ${timesheet.pay_period} Hours: ${timesheet.hours_worked} Wage: $${Number(timesheet.wage).toFixed(2)}</p>
				`;

			});

			outputHtml += '</div>';

		pay_period++;

	}

	document.querySelector('.timesheets').innerHTML = outputHtml;

}

function submitTimesheet() {

	let timesheetInfo = {

		'hours_worked':	document.getElementById('new-timesheet').value,
		'date': nextTimesheet.next_date,

	};

	fetch('/process_timesheet', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(timesheetInfo)

	})
	.then(response => response.json())
	.then(result => {

		if (result === 'SUBMIT_TIMESHEET_SUCCESS') {

			window.location.href = window.location.href;

		} else {
			console.log(`Error: ${result}`);
		}

	})
	.catch(error => {
		console.error('Error:', error);
	});

}

displayTimeSheets();