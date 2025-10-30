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
		}

		else {
			this.cart = [];
		}

	}

	addToCart(item_id, quantityElement) {

		if (this.cart) {

			this.cart.forEach(cartItem => {

				if (item_id == cartItem.item_id) {

					let quantity = Number(document.querySelector(quantityElement).value);
					cartItem.quantity += quantity;
					this.quantity += quantity;
					this.estimatedTotal += quantity * Number(cartItem.price);
					foundDuplicate = true;

					return;

				}

			});

		}

		product.forEach(productItem => {

			if (item_id == productItem.item_id) {

				let tempProduct = productItem;
				tempProduct.quantity = Number(document.querySelector(quantityElement).value);
				this.cart.push(productItem);
				this.quantity += tempProduct.quantity;
				this.estimatedTotal += tempProduct.quantity * Number(productItem.price);

				return;

			}

		});

		this.updateCart();
	}

	updateCart() {

		localStorage.setItem(this.cart_name, JSON.stringify({

			'cart': this.cart, 
			'quantity': this.quantity, 
			'estimatedTotal': this.estimatedTotal

		}));

	}

	display_cart() {

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
			let buttons = '';
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

				buttons += `<div class="buttons"><button class="increase-lower" onclick="cart.increaseQuantity(${cartItem.item_id})">+</button><button class="increase-lower" onclick="cart.decreaseQuantity(${cartItem.item_id})">-</button><button class="remove-button" onclick="cart.removeItem(${cartItem.item_id})">Remove Item</button></div>`;

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
					<div class='checkout-url'><a href='${checkoutUrl}'>Go To Checkout</a></div>
				</div>
			`;

			let outputHtml = outerHtml1 + innerHtml + outerHtml2 + '<div class="remove-items-buttons">' + buttons + '</div></div>';
			document.querySelector('.cart-content').innerHTML = outputHtml + cartSummary;

		} else {
			document.querySelector('.cart-content').innerHTML = '<p class="empty-message">Cart Empty</p>';
		}

	}

	removeItem(item_id) {

		this.cart.forEach((cartItem, index) => {

			if (item_id == cartItem.item_id) {

				this.quantity -= cartItem.quantity;
				this.estimatedTotal -= Number(cartItem.price) * cartItem.quantity;
				this.cart.splice(index, 1);

				return;

			}

		});

		this.updateCart();
		this.display_cart();

	}

	increaseQuantity(item_id) {

		this.cart.forEach(cartItem => {

			if (item_id == cartItem.item_id) {

				cartItem.quantity++;
				this.quantity++;
				this.estimatedTotal += Number(cartItem.price);

				return;

			}

		});

		this.updateCart();
		this.display_cart();

	}

	decreaseQuantity(item_id) {

		this.cart.forEach((cartItem, index) => {

			if (item_id == cartItem.item_id) {

				if (this.quantity === 1 || cartItem.quantity === 1) {

					this.quantity--;
					this.estimatedTotal -= Number(cartItem.price);
					this.cart.splice(index, 1);

					return;

				}

				cartItem.quantity--;
				this.quantity--;
				this.estimatedTotal -= Number(cartItem.price);

				return;

			}

		});

		this.updateCart();
		this.display_cart();
	}
}

let cart = new Cart('cart');

cart.display_cart();
