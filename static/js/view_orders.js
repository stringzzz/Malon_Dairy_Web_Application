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

function displayOrders() {

	if (orders.length > 0) {

		fullHtml = '';

		orders.forEach(order => {

			if (!order.reviewActive) {
				order.reviewActive = false;
			}

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

			let reviewHtml = '';

			if (order.reviewActive) {

				reviewHtml = `
					<div class='review-box'>
						<p>All reviews are public</p>
						<div class="container1">
							<img src="${starUrl}" alt="yellow rating star" class="transparent-star" id="star1" onclick="selectRating(1, true)">
							<img src="${starUrl}" alt="yellow rating star" class="transparent-star" id="star2" onclick="selectRating(2, true)">
							<img src="${starUrl}" alt="yellow rating star" class="transparent-star" id="star3" onclick="selectRating(3, true)">
							<img src="${starUrl}" alt="yellow rating star" class="transparent-star" id="star4" onclick="selectRating(4, true)">
							<img src="${starUrl}" alt="yellow rating star" class="transparent-star" id="star5" onclick="selectRating(5, true)">
						</div>
						<textarea id='review-body' maxlength=1024></textarea><br>
						<button class='button submit-review-button' onclick="submitReview(${order.order_id})">Submit Review</button>
						<button class='button review-button' onclick="deactivateReviews()">Close Review</button>
					</div>
				`;

			}

			let outputHtml = outerHtml1 + innerHtml + outerHtml2;
			let writeReviewButton = '';

			if (order.order_status == 'Shipped' && !Number(order.given_review) && !order.reviewActive) {
				writeReviewButton = `<button class='button activate-review-button' onclick="activateReview(${order.order_id})">Write Review</button>`;
			}

			let reviewMessage = '';

			if (Number(order.given_review)) {

				reviews.forEach(review => {

					if (review.order_id == order.order_id) {

						reviewMessage += `
							<div class='review'>
								<p>${review.created}</p>
								<p>`;

						for (let n = 1; n <= 5; n++) {
	
							if (n <= Number(review.stars)) {
								reviewMessage += `<img src="${starUrl}" alt="yellow rating star" class="opaque-star">`;
							} else {
								reviewMessage += `<img src="${starUrl}" alt="yellow rating star" class="transparent-star">`;
							}
	
						}
	
						reviewMessage += `
								<p>${review.review_comment}</p>
							</div>
						`;
	
						return;
	
					}
	
				});
	
			}			
	
			fullHtml += '<div class="order-group">' + outputHtml + orderSummary + shippingInfo + writeReviewButton + reviewHtml + reviewMessage + '</div>';
	
		});	
	
		document.querySelector('.main-content').innerHTML = fullHtml;

		if (reviewActive) {
	
			for (let n = 1; n <= 5; n++) {
	
				star = document.getElementById(`star${n}`);
	
				star.addEventListener("mouseenter", () => {
					selectRating(`${n}`, false);
				});
	
				star.addEventListener("mouseleave", () => {
					revertToTransparency();
				});
	
			}
	
		}
	
	} else {
		document.querySelector('.main-content').innerHTML = '<p class="no-order-message">No orders placed</p>';
	}

}

let reviewActive = false;
function activateReview(orderId) {

	orders.forEach(order => {

		if (order.reviewActive) {
			order.reviewActive = false;
		}

		if (orderId == order.order_id) {
			order.reviewActive = true;
			reviewActive = true;
			chosenRating = 0;
		}

	});

	displayOrders();

	document.querySelector('.submit-review-button').disabled = true;

}

let chosenRating = 0;

function selectRating(rating, isChosen) {

	for (let n = 1; n <= rating; n++) {
		document.getElementById(`star${n}`).className = "opaque-star";
	}

	for (let n = rating + 1; n <= 5; n++) {
		document.getElementById(`star${n}`).className = "transparent-star";
	}

	if (isChosen) {

		chosenRating = rating;
		document.querySelector('.submit-review-button').disabled = false;

	}

}

function revertToTransparency() {

	if (chosenRating > 0) {

		for (let n = chosenRating + 1; n <= 5; n++) {
			document.getElementById(`star${n}`).className = "transparent-star";
		}

	} else {

		for (let n = 1; n <= 5; n++) {
			document.getElementById(`star${n}`).className = "transparent-star";
		}

	}

}

function submitReview(orderId) {

	orders.forEach(order => {

		if (orderId == order.order_id) {

			review = {

				order_id: order.order_id,
				stars: chosenRating,
				review_comment: document.getElementById('review-body').value

			}

			if (order.given_review == '0') {

				order.given_review = '1';

				fetch('/process_review', {

					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(review)

				})
				.then(response => response.json())
				.then(result => {

					if (result === 'REVIEW_SUCCESS') {

						reviewActive = false;
						chosenRating = 0;
						deactivateReviews();
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

function deactivateReviews() {

	orders.forEach(order => {

		if (order.reviewActive) {
			order.reviewActive = false;
		}

	});

	reviewActive = false;
	chosenRating = 0;

	displayOrders();

}

let cart = new Cart('cart');
cart.updateCart();

document.querySelector('.login-and-register').innerHTML = `<a href="${customerInfoUrl}" class="user-email">${userEmail}</a><br><a href="${logoutUrl}" class="user-email">Logout</a>`;
displayOrders();