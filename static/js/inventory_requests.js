function displayRequestForm() {

	outputHtml = '';

	items.forEach(item => {

		outputHtml += `
		<div class='request-item'>
			<p>${item.item_id} ${item.item_name}</p>
			<input type='text' id='request-input${item.item_id}' value=0>
		</div>`; 		

	});

	outputHtml += '<button class="send-request-button" onclick="sendInventoryRequest()">Submit Request</button>';
	outputHtml += '<button class="send-request-button" onclick="clearForm()">Clear Form</button>';
	outputHtml += '<p class="result-message"></p>'
	
	document.querySelector('.request-content').innerHTML = outputHtml;

}

displayRequestForm();

function sendInventoryRequest() {

	requestItems = [];

	items.forEach(item => {

		if (document.getElementById(`request-input${item.item_id}`).value > 0) {

			item = {
				'item_id': item.item_id,
				'quantity': Number(document.getElementById(`request-input${item.item_id}`).value)
			};

			requestItems.push(item);
		}

	});

	fetch('/process_inventory_request', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},

		body: JSON.stringify(requestItems)
	})
	.then(response => response.json())
	.then(result => {
		if (result === 'INVENTORY_REQUEST_SUCCESS') {
			document.querySelector('.result-message').innerHTML = 'Inventory Request Successfully Submitted';
			clearForm();
		} else if (result === 'Invalid Inventory Request Number') {
			document.querySelector('.result-message').innerHTML = 'Inventory Request Input Error';	
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});

}

function clearForm() {

	items.forEach(item => {
		document.getElementById(`request-input${item.item_id}`).value = 0;
	});

}

function displayInventoryRequests() {

	let outputHtml = '';

	if (locationType == 'Store') {

		requests.forEach(request => {

			outputHtml += `
				<div class='inventory-request'>
				<p>Request ID#${request.request_id} ${request.created}</p>
				<p>Locations: TO: #${request.requesting_location} FROM: #${request.from_location}</p>
				<p>Status ${request.request_status}</p>
					<table>
						<thead>
							<tr>
								<td>Item ID</td>
								<td>Name</td>
								<td>Quantity</td>
							</tr>
						</thead>
						<tbody>
			`;

			request.items.forEach(item => {

				outputHtml += `
					<tr>
						<td>${item.item_id}</td>
						<td>${item.item_name}</td>
						<td>${item.quantity}</td>
					</tr>
				`;

			});

			outputHtml += '</tbody></table></div>';

		});

	} else if (locationType == 'Distribution Center') {

		requests.forEach(request => {

			outputHtml += `
				<div class='inventory-request'>
				<p>Request ID#${request.request_id} ${request.created}</p>
				<p>Locations: TO: #${request.requesting_location} FROM: #${request.from_location}</p>
				<p>Status ${request.request_status}</p>
					<table>
						<thead>
							<tr>
								<td>Item ID</td>
								<td>Name</td>
								<td>Inventory</td>
								<td>Quantity</td>
							</tr>
						</thead>
						<tbody>
			`;

			insufficientInventory = false;

			request.items.forEach(item => {

				if (item.quantity.inventory < item.quantity.quantity) {

					outputHtml += `
						<tr>
							<td>${item.item_id}</td>
							<td>${item.item_name}</td>
							<td><span class='insufficient-inventory'>${item.quantity.inventory}</span></td>
							<td>${item.quantity.quantity}</td>
						</tr>
					`;

					insufficientInventory = true;

				} else {

					outputHtml += `
						<tr>
							<td>${item.item_id}</td>
							<td>${item.item_name}</td>
							<td>${item.quantity.inventory}</td>
							<td>${item.quantity.quantity}</td>
						</tr>
					`;

				}

			});

			outputHtml += '</tbody></table>';

			if (request.request_status == 'Requested') {

				if (!insufficientInventory) {
					outputHtml += `<button class="approve-request-button" onclick="approveRequest(${request.request_id})">Approve Request</button>`;
				} else {
					outputHtml += `<button class="approve-request-button" onclick="approveRequest(${request.request_id})" disabled=true>Approve Request</button>`;				
				}

			}

			outputHtml += `<p class="result-message${request.request_id}"></p>`
			outputHtml += '</div>';

		});

	}

	document.querySelector('.request-content').innerHTML = outputHtml;

}

function updateInventory(requestId) {

	requests.forEach(request => {

		if (request.request_id == requestId) {
			
			request.items.forEach(item => {
				item.quantity.inventory -= item.quantity.quantity;
			});

		}

	});

}

function approveRequest(requestID) {

	fetch('/approve_inventory_request', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(requestID)

	})
	.then(response => response.json())
	.then(result => {

		if (result === 'APPROVE_INVENTORY_REQUEST_SUCCESS') {

			document.querySelector(`.result-message${requestID}`).innerHTML = 'Inventory Request Successfully Approved';

			requests.forEach(request => {

				if (request.request_id == requestID) {
					request.request_status = 'Approved';
				}

			});

			updateInventory(requestID);
			displayInventoryRequests();

		} else if (result === 'Invalid Inventory Request Number' || result == 'Invalid Inventory Request Quantity') {

			document.querySelector(`.result-message${requestID}`).innerHTML = 'Inventory Request Approval Failed';

		}
	})
	.catch(error => {
		console.error('Error:', error);
	});

}