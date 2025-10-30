function displayTimesheetFilter() {
	let outputHtml = "<h1>Employee Filter</h1><select id='employee-filter'>";
	
	employees.forEach(employee => {

		outputHtml += `
			<option value='${employee.employee_id}'>${employee.employee_id} ${employee.name}</option>
		`;

	});

	outputHtml += "</select><br><select id='pay-period'><option value='All' selected>Pay Period: All</option>";
	
	pay_periods.forEach(pay_period => {

		outputHtml += `
			<option value='${pay_period}'>Pay Period: ${pay_period}</option>
		`;

	});

	outputHtml += "</select><br><button id='filter-timesheets-button' onclick='displayTimeSheets()'>Filter Timesheets</button>";
	
	document.querySelector('.timesheet-filter').innerHTML = outputHtml;

}

displayTimesheetFilter();

function displayTimeSheets() {
	
	let employeeId = document.getElementById("employee-filter").value;
	let payPeriod = document.getElementById("pay-period").value;
	let timesheetHtml = '';

	employees.forEach(employee => {

		if (employee.employee_id == employeeId) {
			
			timesheetHtml += `
				<div class='employee-data'>
				<p>Employee ID #${employee.employee_id}</p>
				<p>${employee.name}</p>
			`;

			if (employee.employee_id != selfId) {

				timesheetHtml += `
					$<input type='text' id='raise-wage'>
					<button id='filter-timesheets-button' onclick='raiseWage(${employee.employee_id})'>Raise Wage</button>
					<div class='raise-wage-output'></div>
					</div>
				`;

			}

			return;

		}

	});

	let pay_period = 1;
	while(timesheets['pay_period' + String(pay_period)]) {

			timesheetHtml += `
				<div class='timesheet-group'>
			`;

			let timesheetCount = 0;
			let total = 0.0;

			timesheets['pay_period' + String(pay_period)].forEach(timesheet => {

				if (timesheet.employee_id == employeeId) {

					if (payPeriod == 'All' || timesheet.pay_period == payPeriod) {

						timesheetHtml += `
							<p>${timesheet.created} Pay Period: ${timesheet.pay_period} Hours: ${timesheet.hours_worked} Wage: $${Number(timesheet.wage).toFixed(2)}</p>
						`;

						total += Number(timesheet.hours_worked) * Number(timesheet.wage);
						timesheetCount++;

					}

				}

			});

			if (timesheetCount == 10) {

				timesheetHtml += `
					<div class='pay-data'>
						<p>Total For Pay Period: $${total.toFixed(2)}</p>
						<p>Taxes: $${(total * 0.10).toFixed(2)}</p>
						<p>Final Total For Pay Period: $${(total - (total * 0.10)).toFixed(2)}</p>
					</div>
				`;

			}

			timesheetHtml += '</div>';

		pay_period++;

	}

	document.querySelector('.view-timesheet-content').innerHTML = timesheetHtml;

}

function raiseWage(employeeId) {

	let wageIncrease = {

		'employee_id': employeeId,
		'wage_increase': document.getElementById("raise-wage").value

	}

	fetch('/process_raise_wage', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(wageIncrease)

	})
	.then(response => response.json())
	.then(result => {

		if (result === 'RAISE_WAGE_SUCCESS') {

			document.querySelector('.raise-wage-output').innerHTML = 'Wage Successfully Raised';

		} else {
			document.querySelector('.raise-wage-output').innerHTML = `Error: ${result}`;
		}

	})
	.catch(error => {
		console.error('Error:', error);
	});

}