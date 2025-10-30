//localStorage.clear();

class Cart {
	cart_name;
	cart;
	quantity = 0;
	estimatedTotal = 0;

	//Get cart from locatSotrage if it exists, otherwise create it as empty
	constructor(cart_name) {
	
		this.cart_name = cart_name;
		let tempCart = localStorage.getItem(this.cart_name);
	
		if (tempCart) {
			let tempCart2 = JSON.parse(tempCart);
			this.cart = tempCart2.cart;
			this.quantity = tempCart2.quantity;
			this.estimatedTotal = tempCart2.estimatedTotal;
			this.updateCart();
		}
	
		else {
			this.cart = [];
		}
	
	}

	updateCart() {

		//Displays the updated cart on page after any changes are made

		localStorage.setItem(this.cart_name, JSON.stringify({

			'cart': this.cart, 
			'quantity': this.quantity, 
			'estimatedTotal': this.estimatedTotal

		}));

		if (this.quantity <= 99) {
			document.querySelector('.total-quantity').innerHTML = this.quantity;
		} else {
			document.querySelector('.total-quantity').innerHTML = '99+';
		}

		if (this.estimatedTotal !== 0) {

			if (this.estimatedTotal < 0) {
				this.estimatedTotal = 0;
			}

			document.querySelector('.estimated-total').innerHTML = "Estimated Total: $" + this.estimatedTotal.toFixed(2);

		}

	}

}

function displayCustomerInfo(customerInfo) {

	document.getElementById('first_name').value = customerInfo.first_name;
	document.getElementById('last_name').value = customerInfo.last_name;
	document.getElementById('street_address').value = customerInfo.street_address;
	document.getElementById('city').value = customerInfo.city;
	document.getElementById('state').value = customerInfo.state;
	document.getElementById('zip_code').value = customerInfo.zip_code;
	document.getElementById('phone_number').value = customerInfo.phone_number;

}

let cart = new Cart('cart');
cart.updateCart();

document.querySelector('.login-and-register').innerHTML = `<a href="${customerInfoUrl}" class="user-email">${userEmail}</a><br><a href="${logoutUrl}" class="user-email">Logout</a>`;

if (formInput != 'None') {

	//After error in form submission, re-display the customer info so they can fix it

	document.getElementById('first_name').value = formInput.first_name;
	document.getElementById('last_name').value = formInput.last_name;
	document.getElementById('street_address').value = formInput.street_address;
	document.getElementById('city').value = formInput.city;
	document.getElementById('zip_code').value = formInput.zip_code;
	document.getElementById('phone_number').value = formInput.phone_number;

} else {

	displayCustomerInfo(customerInfo);

}