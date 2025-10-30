function displayFilters() {
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
	document.getElementById('all').checked = true;
	document.getElementById('total-descending').checked = true;
}

function filterSales() {
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
	radios = document.getElementsByName('group-by');
	selectedGroupBy = '';
	radios.forEach(radio => {
		if (radio.checked) {
			selectedGroupBy = radio.value;
			return;
		}
	});
	sortRadios = document.getElementsByName('sort-by');
	selectedSortBy = '';
	sortRadios.forEach(radio => {
		if (radio.checked) {
			selectedSortBy = radio.value;
			return;
		}
	});

	let sales2 = JSON.parse(JSON.stringify(sales));

	let filteredSales = []
	sales2.forEach(item => {
		if (searchFilter == 'Any' || regex.test(item.item_name)) {
			if (selectLocation == 'All' || item.location_id == selectLocation) {
				if (item.purchase_price >= minPrice && item.purchase_price <= maxPrice) {
					if (item.quantity >= minQuantity && item.quantity <= maxQuantity) {
						if (selectedGroupBy == 'All') {
							filteredSales.unshift(item);
						} else if (selectedGroupBy == 'Total Per Store') {
							duplicateFound = false;
							filteredSales.forEach(sale => {
								if (item.location_id == sale.location_id && item.item_name == sale.item_name && item.purchase_price == sale.purchase_price) {
									sale.quantity += item.quantity;
									sale.total += Number(item.purchase_price) * item.quantity;
									duplicateFound = true;
									return;
								}
							});
							if (!duplicateFound) {
								item.total = Number(item.purchase_price) * item.quantity;
								filteredSales.unshift(item);
							}
						} else if (selectedGroupBy == 'Complete Total') {
							duplicateFound = false;
							filteredSales.forEach(sale => {
								if (item.item_name == sale.item_name && item.purchase_price == sale.purchase_price) {
									sale.quantity += item.quantity;
									sale.total += Number(item.purchase_price) * item.quantity;
									duplicateFound = true;
									return;
								}
							});
							if (!duplicateFound) {
								item.total = Number(item.purchase_price) * item.quantity;
								filteredSales.unshift(item);
							}
						}
					}
				}
			}
		}
	});

	if (selectedGroupBy != 'All') {
		if (selectedSortBy == 'Total Descending') {
			filteredSales.sort((a, b) => b.total - a.total);
		} else if (selectedSortBy == 'Total Ascending') {
			filteredSales.sort((a, b) => a.total - b.total);
		}
	}

	let foundSales = false;
	if (selectedGroupBy == 'All') {
		filteredHtml = `
			<table class="sales-table">
				<thead>
					<tr>
						<td>Location</td>
						<td>Item Name</td>
						<td>Price</td>
						<td>Qty</td>
						<td>Purchased</td>
					</tr>
				</thead>
				<tbody>
			`;

			filteredSales.forEach(sale => {
				if (selectedCategories == 'All') {
					filteredHtml += `
					<tr class="sales-item">
						<td>${sale.location_id}</td>
						<td>${sale.item_name}</td>
						<td>$${Number(sale.purchase_price).toFixed(2)}</td>
						<td>${sale.quantity}</td>
						<td>${sale.purchase_time}</td>
					</tr>
					`;
					foundSales = true;
				} else {
					selectedCategories.forEach(category => {
						if (category == sale.category) {
							filteredHtml += `
						<tr class="sales-item">
							<td>${sale.location_id}</td>
							<td>${sale.item_name}</td>
							<td>$${Number(sale.purchase_price).toFixed(2)}</td>
							<td>${sale.quantity}</td>
							<td>${sale.purchase_time}</td>
						</tr>
						`;
							foundSales = true;
							return;
						}
					});
				}
			});
	
	} else if (selectedGroupBy == 'Total Per Store') {
		filteredHtml = `
		<table class="sales-table">
			<thead>
				<tr>
					<td>Location</td>
					<td>Item Name</td>
					<td>Price</td>
					<td>Qty</td>
					<td>Total</td>
				</tr>
			</thead>
			<tbody>
		`;

		filteredSales.forEach(sale => {
			if (selectedCategories == 'All') {
				filteredHtml += `
				<tr class="sales-item">
					<td>${sale.location_id}</td>
					<td>${sale.item_name}</td>
					<td>$${Number(sale.purchase_price).toFixed(2)}</td>
					<td>${sale.quantity}</td>
					<td>$${sale.total.toFixed(2)}</td>
				</tr>
				`;
				foundSales = true;
			} else {
				selectedCategories.forEach(category => {
					if (category == sale.category) {
						filteredHtml += `
					<tr class="sales-item">
						<td>${sale.location_id}</td>
						<td>${sale.item_name}</td>
						<td>$${Number(sale.purchase_price).toFixed(2)}</td>
						<td>${sale.quantity}</td>
						<td>$${sale.total.toFixed(2)}</td>
					</tr>
					`;
						foundSales = true;
						return;
					}
				});
			}
		});

	} else if (selectedGroupBy == 'Complete Total') {
		filteredHtml = `
		<table class="sales-table">
			<thead>
				<tr>
					<td>Item Name</td>
					<td>Price</td>
					<td>Qty</td>
					<td>Total</td>
				</tr>
			</thead>
			<tbody>
		`;

		filteredSales.forEach(sale => {
			if (selectedCategories == 'All') {
				filteredHtml += `
				<tr class="sales-item">
					<td>${sale.item_name}</td>
					<td>$${Number(sale.purchase_price).toFixed(2)}</td>
					<td>${sale.quantity}</td>
					<td>$${(Number(sale.purchase_price) * sale.quantity).toFixed(2)}</td>
				</tr>
				`;
				foundSales = true;
			} else {
				selectedCategories.forEach(category => {
					if (category == sale.category) {
						filteredHtml += `
					<tr class="sales-item">
						<td>${sale.item_name}</td>
						<td>$${Number(sale.purchase_price).toFixed(2)}</td>
						<td>${sale.quantity}</td>
						<td>$${(Number(sale.purchase_price) * sale.quantity).toFixed(2)}</td>
					</tr>
					`;
						foundSales = true;
						return;
					}
				});
			}
		});
	}

	filteredHtml += '</tbody></table>';
	if (foundSales) {
		document.querySelector('.sales-content').innerHTML = filteredHtml;
	} else {
		document.querySelector('.sales-content').innerHTML = '<p>No items found</p>';
	}
}