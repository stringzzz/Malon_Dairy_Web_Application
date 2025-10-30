class Cart {
	cart_name;
	cart;
	quantity = 0;
	estimatedTotal = 0;

	constructor(cart_name, emptyOutCart) {

		this.cart_name = cart_name;
		if (!emptyOutCart) {

			let tempCart = localStorage.getItem(this.cart_name);

			if (tempCart) {
				let tempCart2 = JSON.parse(tempCart);
				this.cart = tempCart2.cart;
				this.quantity = tempCart2.quantity;
				this.estimatedTotal = tempCart2.estimatedTotal;
			}

		}

		else {
			this.cart = [];
		}

	}

	updateCart() {
	
		localStorage.setItem(this.cart_name, JSON.stringify({
	
			'cart': this.cart, 
			'quantity': this.quantity, 
			'estimatedTotal': this.estimatedTotal
	
		}));
	
	}

	displayCart(orderPlaced) {
	
		if (this.cart.length > 0) {
	
			let outerHtml1 = `
				<h1>Cart Contents</h1><br>
				<div class='cart-and-buttons'>
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
				`;

			let innerHtml = '';
			let shippingCost = 0;
			this.cart.forEach(cartItem => {

				shippingCost += (Number(cartItem.weight) * 0.20) * cartItem.quantity;

				innerHtml += `
					<tr>
						<td>${cartItem.name}</td>
						<td>$${cartItem.price}</td>
						<td>${cartItem.quantity}</td>
						<td>$${(Number(cartItem.price) * cartItem.quantity).toFixed(2)}</td>
					</tr>
				`;
				
			});		

			let tax = cart.estimatedTotal * 0.10;
			let cartSummary = `
				<div class='cart-summary'>
					<table>
						<tr>
							<td>Total: </td>
							<td>$${cart.estimatedTotal.toFixed(2)}</td>
						</tr>
						<tr>	
							<td>Shipping: </td>
							<td>$${shippingCost.toFixed(2)}</td>
						</tr>
						<tr>
							<td>Tax: </td>
							<td>$${tax.toFixed(2)}</td>
						</tr>
						<tr>
							<td>Final Total: </td>
							<td>$${(cart.estimatedTotal + shippingCost + tax).toFixed(2)}</td>
						</tr>
					</table>
				</div>
				<div class='cart-link'>
					<img src="/static/shopping_cart1.png" alt="Shopping Cart Icon">
					<a href='${cartUrl}'>Back To Cart</a>
				</div>
			`;

			let payCode = '';
			if (payActive) {

				payCode = `
					<div class='place-order'>
						<input id='card-number' maxlength=6 placeholder='Enter 6-Digit card number'>
						<button onclick='placeOrder(cart)'>Place Order</button>
					</div>
				`;

			} else {

				payCode = `
					<div class='confirm-and-pay'><button onclick='payActive = true; cart.displayCart(false)'>Confirm And Pay</button></div>
				`;

			}

			let shippingInfo = `
				<div class='shipping-info'>
					<h1>Shipping Information</h1>
					<p>${userInfo.name}</p>
					<p>${userInfo.street_address}</p>
					<p>${userInfo.city_state_zip}</p>
					<p>${userInfo.phone_number}</p>
					<div class='change-info-link'><a href='${changeInfoUrl}'>Change Info</a></div>
					${payCode}	
				</div>
			`;

			let outputHtml = outerHtml1 + innerHtml + outerHtml2;
			document.querySelector('.checkout-content').innerHTML = outputHtml + cartSummary + shippingInfo;

		} else {

			if (orderPlaced) {
				document.querySelector('.checkout-content').innerHTML = `<div class='order-placed'><p>Order Successfully Placed</p><a href='${viewOrdersUrl}'>View Orders</a></div>`;
			} else {
				document.querySelector('.checkout-content').innerHTML = '<div class="empty-cart"><p>Cart Empty</p></div>';
			}

		}

	}

}

function placeOrder(cart) {

	//Place customer order of cart contents

	let cardNumber = document.getElementById('card-number').value; //Insecure way, don't do this
	let cartItems = [];

	cart.cart.forEach(cartItem => {
		cartItems.push([cartItem.item_id, cartItem.quantity]);
	});

	let cartInfo = {
		'cart': cartItems,
		'card_number': cardNumber
	};

	fetch('/process_order', {

		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(cartInfo)

	})
	.then(response => response.json())
	.then(result => {

		if (result === 'ORDER_SUCCESS') {

			cart = new Cart('cart', true);
			cart.updateCart();
			cart.displayCart(true);

		} else if (result === 'Invalid Card Number' || result === 'Invalid Cart Input') {
			document.querySelector('.checkout-content').innerHTML = `<div class='order-placed'><p>Invalid Card Number</p></div>`;
		}

	})
	.catch(error => {
		console.error('Error:', error);
	});

}

let cart = new Cart('cart', false);
let payActive = false;
cart.displayCart(false);