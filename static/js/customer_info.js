class Cart {
	cart_name;
	cart;
	quantity = 0;
	estimatedTotal = 0;

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

let cart = new Cart('cart');
cart.updateCart();

document.querySelector('.login-and-register').innerHTML = `<a href="${customerInfoUrl}" class="user-email">${userEmail}</a><br><a href="${logoutUrl}" class="user-email">Logout</a>`;
document.querySelector('.greeting').innerHTML = 'Welcome, ' + customerName;