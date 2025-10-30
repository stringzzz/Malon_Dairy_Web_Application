function displayAnnouncements() {

	//Display the Manager announcements

	let html = '<h1>Announcements</h1>';
	if (announcements && announcements.length > 0) {
	
		announcements.forEach(announcement => {
	
			if (announcement.viewing === undefined) {
				announcement.viewing = false;
			}
	
			html += `
			<div class='announcement'>
			<p class='announcement-info' onclick='viewAnnouncement(${announcement.announcement_id})'>${announcement.name} ${announcement.created}</p>`;
	
			if (announcement.viewing) {
				html += `<div class='announcement-body'><p>${announcement.announcement}</p></div></div>`;
			} else {
				html += `<div class='announcement-body'></div></div>`;
			}
	
		});
	
		document.querySelector('.announcements-content').innerHTML = html;
	
	} else {
	
		document.querySelector('.announcements-content').innerHTML = '<p>No Announcements</p>';
	
	}
}

function viewAnnouncement(announcementId) {

	//Toggle viewing announcement, displays the body if viewing

	announcements.forEach(announcement => {
	
		if (announcementId == announcement.announcement_id) {

			if (announcement.viewing == false) {
				announcement.viewing = true;
			} else {
				announcement.viewing = false;
			}

		}

	});
	
	displayAnnouncements(announcements);

}

displayAnnouncements();