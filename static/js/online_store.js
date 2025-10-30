function increaseQuantity(inputElementClass) {
	inputElement = document.querySelector(inputElementClass);
	inputElement.value = Number(inputElement.value) + 1;
}

function decreaseQuantity(inputElementClass) {
	inputElement = document.querySelector(inputElementClass);
	temp_quantity = Number(inputElement.value) - 1;
	if (temp_quantity <= 0) { temp_quantity = 1; }
	inputElement.value = temp_quantity;
}

class Item {

	item_id;
	item_img;
	name;
	category;
	weight;
	price;

	constructor(item_id, name, item_img, category, weight, price) {

		this.item_id = item_id;
		this.name = name;
		this.item_img = item_img;
		this.category = category;
		this.weight = weight;
		this.price = price;

	}

}

let product = [];
productsFromDB.forEach(item => { product.push(new Item(...item)) });

function displayProduct(category) {

	html = '';
	product.forEach((item, index) => {

		if (category === 'All' || category === item.category) {

			html += `
				<div class="item">
					<img src="${item.item_img}" alt="${item.name}">
					<p class="item-name">${item.name}</p>
					<div class="price_and_quantity">
						<p class="price">$${(Number(item.price)).toFixed(2)}</p>
						<div class="quantity">
							<input type="text" value="1" autocomplete="off" class='quantity-input${index + 1}'>
							<button onclick="increaseQuantity('.quantity-input${index + 1}')">+</button>
							<button onclick="decreaseQuantity('.quantity-input${index + 1}')">-</button>
						</div>
					</div>
					<button class="add_to_cart" onclick="cart.addToCart('${item.item_id}', '.quantity-input${index + 1}')">Add To Cart</button>
				</div>
			`;

		}

	});

	document.querySelector('.products').innerHTML = html;

}

function displayCategories() {

	html = '<li class="category-choice" onclick="displayProduct(\'All\')">All</li>';

	categories.forEach(category => {

		html += `
			<li class="category-choice" onclick="displayProduct('${category}')">${category}</li>
		`;

	});

	document.querySelector('.category-list').innerHTML = html;

}

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

	addToCart(item_id, quantityElement) {

		if (this.cart) {

			let foundDuplicate = false;

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

			if (foundDuplicate) { 
				this.updateCart();
				return; 
			}

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

}

function displayLoginOrUser(loggedIn) {

	if (loggedIn === 'true') {
		document.querySelector('.login-and-register').innerHTML = `<a href="${customerInfoUrl}" class="user-email">${userEmail}</a><br><a href="${logoutUrl}" class="user-email">Logout</a>`;
	} else {
		document.querySelector('.login-and-register').innerHTML = `<a href="${loginUrl}">Login</a>/<a href="${registrationUrl}">Register</a>`
	}

}

let cart = new Cart('cart');
cart.updateCart();

displayProduct('All');
displayLoginOrUser(loggedIn);
displayCategories();