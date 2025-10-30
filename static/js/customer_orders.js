function displayOrders() {

	if (orders.length > 0) {

		fullHtml = '';
		orders.forEach(order => {

			let outerHtml1 = `
				<h1>Order #${order.order_id} ${order.Date}</h1><br>
				<div class='order-items'>
				<table>
					<thead>
						<tr>
							<td>Product Name</td>
							<td>Price</td>
							<td>Quantity</td>
							<td>Total Price</td>
						</tr>
					</thead>
					<tbody>`;

			let outerHtml2 = `
					</tbody>
				</table>
				</div>
				`;

			let innerHtml = '';
			order.items.forEach(orderItem => {

				innerHtml += `
					<tr>
						<td>${orderItem.item_name}</td>
						<td>$${Number(orderItem.purchase_price).toFixed(2)}</td>
						<td>${orderItem.quantity}</td>
						<td>$${(Number(orderItem.purchase_price) * Number(orderItem.quantity)).toFixed(2)}</td>
					</tr>
				`;

			});
					
			let orderSummary = `
				<div class='order-summary'>
					<table>
						<tr>
							<td>Total: </td>
							<td>$${Number(order.estimated_cost).toFixed(2)}</td>
						</tr>
						<tr>	
							<td>Shipping: </td>
							<td>$${Number(order.shipping_cost).toFixed(2)}</td>
						</tr>
						<tr>
							<td>Tax: </td>
							<td>$${Number(order.tax).toFixed(2)}</td>
						</tr>
						<tr>
							<td>Final Total: </td>
							<td>$${Number(order.final_price).toFixed(2)}</td>
						</tr>
					</table>
				</div>
			`;

			let shippingInfo = `
				<div class='shipping-info'>
					<h1>Shipping Information</h1>
					<p>Card #: ${order.credit_card_number}</p>
					<p>${order.to_street_address}</p>
					<p>${order.to_city}, ${order.to_state} ${order.to_zip_code}</p>
					<p>Status: ${order.order_status}</p>
				</div>
			`;

			let outputHtml = outerHtml1 + innerHtml + outerHtml2;
			let confirmOrderButton = '';

			if (order.order_status == 'Ordered') {
				confirmOrderButton = `<button class='confirm-order-button' onclick="confirmOrder(${order.order_id})">Confirm Order</button>`;
			}

			fullHtml += '<div class="order-group">' + outputHtml + orderSummary + shippingInfo + confirmOrderButton + '</div>';

		});	

		document.querySelector('.order-content').innerHTML = fullHtml;

	} else {
		document.querySelector('.order-content').innerHTML = '<p class="no-order-message">No orders placed</p>';
	}

}

function confirmOrder(orderId) {
	//Confirm customer order

	orders.forEach(order => {

		if (orderId == order.order_id) {

			if (order.order_status == 'Ordered') {

				order.order_status = 'Shipped';

				fetch('/confirm_order', {

					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(order.order_id)

				})
				.then(response => response.json())
				.then(result => {
					if (result === 'READ_SUCCESS') {
						displayOrders();
					}
				})
				.catch(error => {
					console.error('Error:', error);
				});

			}

		}

	});

}

if (orders == 'No Valid Orders') {
	document.querySelector('.order-content').innerHTML = `<p class='no-order-message'>${orders}</p>`;
} else {
	displayOrders();
}