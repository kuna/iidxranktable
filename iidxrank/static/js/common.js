/* comment part */
function openComment(url) {
	if (url.indexOf("/-1/") > 0) {
		alert("유효하지 않은 곡 번호입니다. DB 업데이트가 필요합니다.\n사이트 관리자에게 문의하세요.");
		return false;
	}
	window.open(url, 'insane_newwindow', 'width=600, height=600');
	return false;
}

/* alert message */
setTimeout(function() {
	$("#message").fadeOut(2000);
}, 5000);

/* load json */
function loadJSON(json_url, processor, onload) {
	$.getJSON(json_url, function(data) {
		for (var row in data['songs']) {
			processor(data['songs'][row], row);
		}
		for (var row in data['users']) {
			processor(data['users'][row], row);
		}
		if (onload) {
			onload();
		}
	});
}