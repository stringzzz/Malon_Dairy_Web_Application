//localStorage.clear();

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

		//Display the new cart any time changes are made

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

function checkPassword() {
	//Check input password to see if it matches the password policy
	//Also check retyped password to make sure it matches the first

	pass = document.getElementById("new_password").value;

	checkOutputHtml = '';

	const invalid_special_pattern = /[^a-zA-Z0-9!@$%^&*?<>]/g
	if (invalid_special_pattern.test(pass)) {

		checkOutputHtml += '<p>Must not contain special characters other than: ! @ # $ % ^ & * ? < ></p>';
		bar = document.querySelector('.inner-password-bar');
		strength = document.querySelector('.strength');
		bar.style.width = "0";
		strength.innerHTML = "Invalid";	

		document.querySelector('.password-policy').innerHTML = checkOutputHtml;	

		return;
	}
	
	pass_score = 0;

	pass_len = pass.length;
	if (pass_len >= 16) {
		pass_score++;
	} else {
		checkOutputHtml = "<p>Must be at least 16 characters</p>";
	}

	const lowercase_pattern = /[a-z]/g;
	if (lowercase_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 lowercase letter</p>";
	}

	const uppercase_pattern = /[A-Z]/g;
	if (uppercase_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 uppercase letter</p>";
	}

	const digit_pattern = /[0-9]/g;
	if (digit_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 digit</p>";
	}

	const special_pattern = /[!@$%^&*?<>]/g;
	if (special_pattern.test(pass)) {
		pass_score++;
	} else {
		checkOutputHtml += "<p>Must contain at least 1 special character: ! @ # $ % ^ & * ? < ></p>";
	}

	bar = document.querySelector('.inner-password-bar');
	strength = document.querySelector('.strength');
	if (pass_score == 0) {
		bar.style.width = "0";
		strength.innerHTML = "Very Weak";
	}

	else if (pass_score == 1) {
		bar.style.width = "20%";
		bar.style.backgroundColor = "red";
		strength.innerHTML = "Weak";
	}

	else if (pass_score == 2) {
		bar.style.width = "40%";
		bar.style.backgroundColor = "orange";
		strength.innerHTML = "Somewhat Weak";
	}

	else if (pass_score == 3) {
		bar.style.width = "60%";
		bar.style.backgroundColor = "yellow";
		strength.innerHTML = "Moderate";
	}

	else if (pass_score == 4) {
		bar.style.width = "80%";
		bar.style.backgroundColor = "yellowgreen";
		strength.innerHTML = "Less Weak";
	}

	else if (pass_score == 5) {
		bar.style.width = "100%";
		bar.style.backgroundColor = "green";
		strength.innerHTML = "Strong";
	}

	retypedPass = document.getElementById('retyped_new_password').value;
	if (pass != retypedPass) {
		document.querySelector('.matching-passwords').innerHTML = '<p>Retyped password must match new password</p>';
	} else {
		document.querySelector('.matching-passwords').innerHTML = '';
	}


	document.querySelector('.password-policy').innerHTML = checkOutputHtml;
	if (checkOutputHtml.length > 0 || pass != retypedPass) {
		document.getElementById('submit-password-button').disabled = true;
	} else {
		document.getElementById('submit-password-button').disabled = false;
	}

}

let cart = new Cart('cart');
cart.updateCart();

document.querySelector('.login-and-register').innerHTML = `<a href="${customerInfoUrl}" class="user-email">${userEmail}</a><br><a href="${logoutUrl}" class="user-email">Logout</a>`;

document.getElementById('submit-password-button').disabled = true;

//Put event listeners on the password forms to activate when the user types something in them
document.addEventListener('DOMContentLoaded', function() {
	password_input = document.getElementById("new_password");
	password_input.addEventListener("input", checkPassword);
});

document.addEventListener('DOMContentLoaded', function() {
	retyped_password_input = document.getElementById("retyped_new_password");
	retyped_password_input.addEventListener("input", checkPassword);
});