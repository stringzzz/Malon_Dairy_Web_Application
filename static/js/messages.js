function displayInbox() {

	document.querySelector('.inbox').innerHTML = `Inbox (${unreadCount})`;

	let html = '<h1>Inbox</h1>';
	if (inbox && inbox.length > 0) {

		inbox.forEach(message => {

			if (message.viewing === undefined) {
				message.viewing = false;
			}

			html += `<div class='message'>`;

			if (Number(message.unread)) {
				html += `<p class='subject-unread' onclick='viewInboxMessage(${message.message_id})'>${message.first_name} ${message.last_name[0]}.: ${message.message_subject}</p>`;
			} else {
				html += `<p class='subject-read' onclick='viewInboxMessage(${message.message_id})'>${message.first_name} ${message.last_name[0]}.: ${message.message_subject}</p>`;
			}

			if (message.viewing) {
				html += `<div class='message-body'><p>${message.body}</p><button class="reply-button" onclick="displaySendMessage(employees, true, ${Number(message.message_id)})">Reply</button></div></div>`;
			} else {
				html += `<div class='message-body'></div></div>`;
			}

		});

		document.querySelector('.employee-messages').innerHTML = html;

	} else {
		document.querySelector('.employee-messages').innerHTML = '<p>Inbox is empty</p>';
	}

}

function viewInboxMessage(messageId) {

	inbox.forEach(message => {

		if (messageId == message.message_id) {

			if (Number(message.unread)) {

				message.unread = '0';
				fetch('/process_read', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(message.message_id)

				})
				.then(response => response.json())
				.then(result => {
					if (result === 'READ_SUCCESS') {
						unreadCount--;
						document.querySelector('.inbox').innerHTML = `Inbox (${unreadCount})`;
					}
				})
				.catch(error => {
					console.error('Error:', error);
				});
			}

			if (message.viewing == false) {
				message.viewing = true;
			} else {
				message.viewing = false;
			}

		}

	});

	displayInbox();

}

function displaySent() {

	document.querySelector('.inbox').innerHTML = `Inbox (${unreadCount})`;

	let html = '<h1>Sent</h1>';
	if (sent && sent.length > 0) {

		sent.forEach(message => {

			if (message.viewing === undefined) {
				message.viewing = false;
			}

			html += `<div class='message'>`;

			if (Number(message.unread)) {
				html += `<p class='subject-unread' onclick='viewSentMessage(${message.message_id})'>${message.first_name} ${message.last_name[0]}.: ${message.message_subject}</p>`;
			} else {
				html += `<p class='subject-read' onclick='viewSentMessage(${message.message_id})'>${message.first_name} ${message.last_name[0]}.: ${message.message_subject}</p>`;
			}

			if (message.viewing) {
				html += `<div class='message-body'><p>${message.body}</p></div></div>`;
			} else {
				html += `<div class='message-body'></div></div>`;
			}

		});

		document.querySelector('.employee-messages').innerHTML = html;

	} else {
		document.querySelector('.employee-messages').innerHTML = '<p>Sent is empty</p>';
	}

}

function viewSentMessage(messageId) {

	sent.forEach(message => {

		if (messageId == message.message_id) {

			if (message.viewing == false) {
				message.viewing = true;
			} else {
				message.viewing = false;
			}

		}

	});

	displaySent();

}

function displaySendMessage(employees, isReplying, messageId) {

	document.querySelector('.inbox').innerHTML = `Inbox (${unreadCount})`;

	let replyMessage = '';
	let replyEmployee = '';
	if (isReplying) {

		inbox.forEach(message => {

			if (message.message_id == messageId) {
				replyMessage = message;
			}

		});

		employees.forEach(employee => {

			if (employee.employee_id == replyMessage.sender) {
				replyEmployee = employee;
			}

		});

	}

	let html = `
		<form action="${sendMessageUrl}" method="POST">
			<select name="recipient">
		`;

	if (isReplying) {
		html += `<option value="${replyEmployee.employee_id}">${replyEmployee.first_name} ${replyEmployee.last_name[0]}. ${replyEmployee.email}</option>`;
	} else {

		employees.forEach(employee => {
			html += `<option value="${employee.employee_id}">${employee.first_name} ${employee.last_name[0]}. ${employee.email}</option>`;
		});

	}

	if (isReplying) {

		html += `
				</select>
				<input type="text" name="message_subject" value="${replyMessage.message_subject}:RE" maxlength=256><br>
				<p class="replied-message">${replyMessage.body}</p>
				<textarea name="body" class="input-body" maxlength=1024></textarea><br>
				<input id="send-message-button" type="submit" value="send-message">
			</form>
		`;

	} else {

		html += `
				</select>
				<input type="text" name="message_subject" placeholder="subject" maxlength=256><br>
				<textarea name="body" class="input-body" maxlength=1024></textarea><br>
				<input id="send-message-button" type="submit" value="send-message">
			</form>
		`;

	}

	document.querySelector('.employee-messages').innerHTML = html;

}

displayInbox();
