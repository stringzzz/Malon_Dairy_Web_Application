function displayFilters() {

	//Display the search filters for the inventory items

	let locationHtml = '<select id="select-location"><option value="All">All Locations</option>';
	locations.forEach(location => {
		locationHtml += `<option value='${location.location_id}'>${location.street_address}, ${location.city}, ${location.state}</option>`;
	});

	locationHtml += '</select>';

	document.querySelector('.locations').innerHTML = locationHtml;

	let categoryHtml = '';
	categories.forEach(category => {

		categoryHtml += `
			<div class='category-checkboxes'><input class='single-checkbox' type='checkbox' name='category-selection' value='${category.category}'>${category.category}</div>
		`;

	});

	document.querySelector('.categories').innerHTML = categoryHtml;				

}

displayFilters();

function clearFilters() {

	document.getElementById('search-filter').value = '';
	document.getElementById('select-location').value = 'All';

	let selectCategory = document.getElementsByName('category-selection');
	selectCategory.forEach(selectedCategory => {
		selectedCategory.checked = false;
	});

	document.getElementById('min-price').value = '';
	document.getElementById('max-price').value = '';
	document.getElementById('min-quantity').value = '';
	document.getElementById('max-quantity').value = '';
}

function filterInventory() {
	let searchFilter = document.getElementById('search-filter').value;
	if (!searchFilter) {
		searchFilter = 'Any';
	}

	const regex = new RegExp(searchFilter, "i");
	let selectLocation = document.getElementById('select-location').value;
	if (!selectLocation) {
		selectLocation = 'All';
	}

	let selectCategory = document.getElementsByName('category-selection');
	let selectedCategories = [];
	selectCategory.forEach(selectedCategory => {

		if (selectedCategory.checked) {
			selectedCategories.push(selectedCategory.value);
		}

	});

	if (selectedCategories.length == 0) {
		selectedCategories = 'All';
	}

	let minPrice = Number(document.getElementById('min-price').value);
	if (!minPrice) {
		minPrice = 0.00;
	}

	let maxPrice = Number(document.getElementById('max-price').value);
	if (!maxPrice) {
		maxPrice = 9999.99;
	}

	let minQuantity = Number(document.getElementById('min-quantity').value);
	if (!minQuantity) {
		minQuantity = 0;
	}

	let maxQuantity = Number(document.getElementById('max-quantity').value);
	if (!maxQuantity) {
		maxQuantity = 9999;
	}

	filteredHtml = `
		<table class="inventory-table">
			<thead>
				<tr>
					<td>Location</td>
					<td>Item Name</td>
					<td>Category</td>
					<td>Price</td>
					<td>Qty</td>
				</tr>
			</thead>
			<tbody>
		`;

	foundInventory = false;	
	inventory.forEach(item => {

		if (searchFilter == 'Any' || regex.test(item.item_name)) {

			if (selectLocation == 'All' || item.location_id == selectLocation) {

				if (item.price >= minPrice && item.price <= maxPrice) {

					if (item.quantity >= minQuantity && item.quantity <= maxQuantity) {

						if (selectedCategories == 'All') {

							filteredHtml += `
							<tr class="inventory-item">
								<td>${item.location_id}</td>
								<td>${item.item_name}</td>
								<td>${item.category}</td>
								<td>$${Number(item.price).toFixed(2)}</td>
								<td>${item.quantity}</td>
							</tr>
							`;

							foundInventory = true;

						} else {

							selectedCategories.forEach(category => {

								if (category == item.category) {
									filteredHtml += `
								<tr class="inventory-item">
									<td>${item.location_id}</td>
									<td>${item.item_name}</td>
									<td>${item.category}</td>
									<td>$${Number(item.price).toFixed(2)}</td>
									<td>${item.quantity}</td>
								</tr>
								`;

									foundInventory = true;
	
									return;
	
								}
	
							});
	
						}
	
					}
	
				}
	
			}
	
		}
	
	});
	
	filteredHtml += '</tbody></table>';
	
	if (foundInventory) {
		document.querySelector('.inventory-content').innerHTML = filteredHtml;
	} else {
		document.querySelector('.inventory-content').innerHTML = '<p>No items found</p>';
	}

}