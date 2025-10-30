function displayReviews() {
	if (reviews.length > 0) {

		let searchFilter = document.getElementById('search-filter').value;

		if (!searchFilter) {
			searchFilter = 'Any';
		}

		const regex = new RegExp(searchFilter, "i");
		let selectCategory = document.getElementsByName('category-selection');
		let selectedCategories = [];

		selectCategory.forEach(selectedCategory => {

			if (selectedCategory.checked) {
				selectedCategories.push(selectedCategory.value);
			}

		});

		if (selectedCategories.length == 0) {
			selectedCategories = ['All'];
		}

		let selectedStarRating = document.getElementById('star-filter').value;
		console.log(selectedStarRating);

		fullHtml = '<h1 class="heading">Customer Reviews</h1>';
		let foundReview = false;

		reviews.forEach(review => {

			let foundSearchMatch = false;

			review.items.forEach(item => {

				if (regex.test(item.item_name)) {
					foundSearchMatch = true;
					return;
				}

			});

			let foundCategoryMatch = false;

			selectedCategories.forEach(category => {

				review.items.forEach(item => {

					if (category == item.category) {
						foundCategoryMatch = true;
						return;
					}

				});

			});

			//Apply search filter to reviews
			if (searchFilter == 'Any' || foundSearchMatch) {

				if (selectedStarRating == 'Any' || selectedStarRating == review.stars) {

					if (selectedCategories == 'All' || foundCategoryMatch) {

						foundReview = true;
						let outerHtml1 = `
							<h1>Order #${review.order_id}</h1><br>
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
						review.items.forEach(orderItem => {

							innerHtml += `
								<tr>
									<td>${orderItem.item_name}</td>
									<td>$${Number(orderItem.purchase_price).toFixed(2)}</td>
									<td>${orderItem.quantity}</td>
									<td>$${(Number(orderItem.purchase_price) * Number(orderItem.quantity)).toFixed(2)}</td>
								</tr>
							`;

						});

						let outputHtml = outerHtml1 + innerHtml + outerHtml2;

						let reviewMessage = '';

						reviewMessage += `
							<div class='review'>
								<p>${review.created}</p>
								<p>${review.customer_name}</p>
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

						fullHtml += '<div class="order-group">' + outputHtml + reviewMessage + '</div>';

					}

				}

			}

		});	

		if (!foundReview) {
			fullHtml += '<p>No Matching Reviews Found</p>';
		}

		document.querySelector('.reviews-content').innerHTML = fullHtml;

	} else {
		document.querySelector('.reviews-content').innerHTML = '<p class="no-order-message">No reviews placed</p>';
	}

}

function displayFilters() {

	let categoryHtml = '';

	categories.forEach(category => {

		categoryHtml += `
			<div class='category-checkboxes'><input class='single-checkbox' type='checkbox' name='category-selection' value='${category}'>${category}</div>
		`;

	});

	document.querySelector('.categories').innerHTML = categoryHtml;				

}

function clearFilters() {

	document.getElementById('search-filter').value = '';
	let selectCategory = document.getElementsByName('category-selection');

	selectCategory.forEach(selectedCategory => {
		selectedCategory.checked = false;
	});

	document.getElementById('star-filter').value = 'Any';

}

displayFilters();
displayReviews();