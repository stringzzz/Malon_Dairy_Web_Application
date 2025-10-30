function displayLocations() {

	let html = '';

	locations.forEach(location => {

		html += `
			<div class='location'>
				<p>${location.type}</p>
				<p>${location.street_address}</p>
				<p>${location.city}, ${location.state} ${location.zip_code}</p>
				<p>${location.phone_number}</p>
			</div>
		`;

	});

	document.querySelector('.locations-content').innerHTML = html;

}

displayLocations();