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

/* load json (for datatable) */
function loadJSON(json_url, processor, onload) {
	$.getJSON(json_url, function(data) {
		for (var row in data['songs']) {
			processor(data['songs'][row], row);
		}
		for (var row in data['users']) {
			processor(data['users'][row], row);
		}
		for (var row in data['recommends']) {
			processor(data['recommends'][row], row);
		}
		if (onload) {
			onload();
		}
	});
}

/* 'custom' type sorting for datatable */
$(function() {
	if (jQuery.fn.dataTableExt) {
		function cmp(a, b) {
			return (a==b)?0:((a<b)?-1:1);
		}

		function conv_series(s) {
			if (s == "ss")
				return 1.5;
			else
				return parseInt(s);
		}

		function conv_diff(s) {
			if (s == "-")
				return -999;
			else if (s == "∞")
				return 999;
			return parseFloat(s.replace(/SP|DP/i,"").toString().replace(/★/g, ""));
		}

		function conv_target(s) {
			if (s == "FC")
				return 7;
			else if (s == "EXH")
				return 6;
			else if (s == "HARD")
				return 5;
			else if (s == "GROOVE")
				return 4;
			else if (s == "EASY")
				return 3;
			return 0;
		}

		function diff_asc(a, b) {
			return cmp(conv_diff(a), conv_diff(b));
		}

		function diff_desc(a, b) {
			return cmp(conv_diff(b), conv_diff(a));
		}

		function series_asc(a, b) {
			return cmp(conv_series(a), conv_series(b));
		}

		function series_desc(a, b) {
			return cmp(conv_series(b), conv_series(a));
		}

		function target_asc(a, b) {
			return cmp(conv_target(a), conv_target(b));
		}

		function target_desc(a, b) {
			return cmp(conv_target(b), conv_target(a));
		}

		jQuery.fn.dataTableExt.oSort["diff-asc"] = diff_asc;
		jQuery.fn.dataTableExt.oSort["diff-desc"] = diff_desc;
		jQuery.fn.dataTableExt.oSort["series-asc"] = series_asc;
		jQuery.fn.dataTableExt.oSort["series-desc"] = series_desc;
		jQuery.fn.dataTableExt.oSort["target-asc"] = target_asc;
		jQuery.fn.dataTableExt.oSort["target-desc"] = target_desc;
	}
});

/* (user) update */
function update_json(url) {
	$.getJSON(url, function(data) {
		alert(data['status']);
	});
}
function updateuser(iidxmeid) {
	$.getJSON("/iidx/update/user/" + iidxmeid, function(data) {
		if (data['status'] == "success") {
			alert('업데이트가 진행중입니다. 잠시만 기다려주세요.');
			$("#loading_animation").show();
			setInterval(function () {
				$.getJSON("/iidx/update/user_status/" + iidxmeid, function (data) {
					console.log(data.updating);
					if (!data.updating) {
						alert("업데이트 완료");
						$("#loading_animation").hide();
						window.location.reload();
					}
				});
			}, 3000);
		} else {
			alert(data['status']);
		}
	});
}



/* load json (for admin) */
function updateSongRank(formobj) {
	var formData = JSON.stringify($(formobj).serializeArray());
	$.post("/iidx/update/rank/", $(formobj).serialize())
		.done(function (data) {
			alert(data.status
				+"\naction:" + data.action
				+"\ncategory to:" + data.rankcategory
				+"\nsongname:" + data.song);
			window.location.reload()
		});
}

/* process songlevel */
function convertSongLevel(level) {
	if (level > 17) {
		return "∞";
	} else if (level <= 0.1) {
		return "-";
	} else {
		return "★"+level;
	}
}