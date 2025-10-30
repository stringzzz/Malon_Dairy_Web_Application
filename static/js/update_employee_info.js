function displayEmployeeInfo(employeeInfo) {

	document.getElementById('first_name').value = employeeInfo.first_name;
	document.getElementById('last_name').value = employeeInfo.last_name;
	document.getElementById('street_address').value = employeeInfo.street_address;
	document.getElementById('city').value = employeeInfo.city;
	document.getElementById('state').value = employeeInfo.state;
	document.getElementById('zip_code').value = employeeInfo.zip_code;
	document.getElementById('phone_number').value = employeeInfo.phone_number;

}

if (formInput != 'None') {
	//Reload employee info if mistake in input found, so they can fix it before resubmitting
	document.getElementById('first_name').value = formInput.first_name;
	document.getElementById('last_name').value = formInput.last_name;
	document.getElementById('street_address').value = formInput.street_address;
	document.getElementById('city').value = formInput.city;
	document.getElementById('zip_code').value = formInput.zip_code;
	document.getElementById('phone_number').value = formInput.phone_number;

} else {
	displayEmployeeInfo(employeeInfo);
}