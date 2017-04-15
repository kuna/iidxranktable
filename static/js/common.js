
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
  alert("Under construction");
  return;

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

/* uses local storage for save/load settings */
function loadSetting(key, def) {
	if (typeof(Storage) !== "undefined") {
		r = localStorage.getItem(key);
		if (r == undefined) {
			return def;
		} else {
			return r;
		}
	} else {
		/* this browser doesn't support Local Storage Objects, sorry! */
		return def;
	}
}
function saveSetting(key, val) {
	if (typeof(Storage) !== "undefined") {
		localStorage.setItem(key, val);
		return val;
	} else {
		/* this browser doesn't support Local Storage Objects, sorry! */
		return undefined;
	}
}

function registerRecentuser(username) {
  var users = getRecentusers();
  var idx = users.indexOf(username);
  if (idx >= 0) {
    console.log(users);
    users.splice(idx, 1);
    console.log(users);
  }
  if (users.length > 5)
    users.pop();
  users.unshift(username);
  console.log(users);
  saveSetting("recentuser", JSON.stringify(users));
}

function removeRecentuser(username) {
  var users = getRecentusers();
  var idx = users.indexOf(username);
  if (idx >= 0) {
    users.splice(idx, 1);
  }
  saveSetting("recentuser", JSON.stringify(users));
}

function getRecentusers() {
  var json = loadSetting("recentuser");
  var users = []
  if (json) {
    users = JSON.parse(json);
  }
  return users;
}

function createSaveString(tabledata) {
  savedata = {}
  savedata['savedata_version'] = 1.0;
  savedata['info'] = {};
  savedata['songs'] = {};

  savedata['info']['username'] = tabledata.userdata.username;
  savedata['info']['spclass'] = tabledata.userdata.spclass;
  savedata['info']['dpclass'] = tabledata.userdata.dpclass;
  savedata['info']['iidxid'] = tabledata.userdata.iidxid;

  for (var i in tabledata.categories) {
    var cate = tabledata.categories[i];
    for (var j in cate.items) {
      var item = cate.items[j];
      savedata['songs'][item.pkid] = {
        'clear': item.clear,
        'rate': item.rate
      };
    }
  }
	return JSON.stringify(savedata);
}

function loadSaveString(str, tabledata) {
  var savedata = JSON.parse(str);
  if (savedata.savedata_version == 1.0) {
    console.log(savedata);
    tabledata.userdata.username = savedata.info.username;
    tabledata.userdata.spclass = savedata.info.spclass;
    tabledata.userdata.dpclass = savedata.info.dpclass;
    tabledata.userdata.spclassstr = getClassstr(savedata.info.spclass);
    tabledata.userdata.dpclassstr = getClassstr(savedata.info.dpclass);
    tabledata.userdata.iidxid = savedata.info.iidxid;

    for (var i in tabledata.categories) {
      var cate = tabledata.categories[i];
      for (var j in cate.items) {
        var item = cate.items[j];
        if (item.pkid in savedata.songs) {
          var sitem = savedata.songs[item.pkid];
          item.clear = sitem.clear;
          item.rate = sitem.rate;
          item.rank = getRank(sitem.rate);
        }
      }
    }

    return true;
  } else {
    console.log("invalid save data");
    return false;
  }
}


/* class string & rank string */
function getClassstr(cls) {
  switch (cls) {
    case 1:
      return "-";
    case 2:
      return "七級";
    case 3:
      return "六級";
    case 4:
      return "五級";
    case 5:
      return "四級";
    case 6:
      return "三級";
    case 7:
      return "二級";
    case 8:
      return "一級";
    case 9:
      return "初段";
    case 10:
      return "二段";
    case 11:
      return "三段";
    case 12:
      return "四段";
    case 13:
      return "五段";
    case 14:
      return "六段";
    case 15:
      return "七段";
    case 16:
      return "八段";
    case 17:
      return "九段";
    case 18:
      return "十段";
    case 19:
      return "中伝";
    case 20:
      return "皆伝";
  }
}

function getRank(rate) {
  if (rate > 800.0/9.0)
    return "AAA";
  else if (rate > 700.0/9.0)
    return "AA";
  else if (rate > 600.0/9.0)
    return "A";
  else if (rate > 500.0/9.0)
    return "B";
  else if (rate > 400.0/9.0)
    return "C";
  else if (rate > 300.0/9.0)
    return "D";
  else if (rate > 200.0/9.0)
    return "E";
  else
    return "F";
}


/*  loading screen */
function showLoadingBackground() {
	$("#loading_background").show();
}
function showLoading(message) {
	$("#loading_message").text(message);
	$("#loading_message").show();
	showLoadingBackground();
}
function hideLoadingBackground() {
	$("#loading_background").fadeOut(500);
}
function hideLoading(message) {
	$("#loading_message").fadeOut(500);
	hideLoadingBackground();
}
function showMessage(message) {
	// temporarily message, so it'll fade out automatically.
	$("#message").text(message);
	$("#message").show();
	if (typeof _tid !== 'undefined') {
		clearTimeout(_tid);
	}
	_tid = setTimeout(function() {
		$("#message").fadeOut(2000);
	}, 5000);
}



/*
 * for user page
 */
$(function() {
  function moveUserpage(username) {
    window.location.href = '/' + username;
    // register to recent user
    registerRecentuser(username);
  }
  $('#goto').click(function (e) {
    moveUserpage($('#searchuser').val());
  });
  $('#searchuser').keypress(function (e) {
    if (e.which == 13) {
      moveUserpage($('#searchuser').val());
    }
  });
});

/*
 * download canvas
 */
function downloadCanvas(c, fn) {
  fn = fn !== undefined ? fn : "download.png";
  var link = document.createElement('a');
  link.setAttribute('download', fn);
  var dataurl = c.toDataURL("image/png");
  /*
  link.setAttribute('href', dataurl);//.replace("image/png", "image/octet-stream"));
  link.click();
  // some browsesr might fail, so add link object dynamically ...
  $(link).text('다운로드가 안되신다면, 여기를 눌러서 직접 다운로드하세요!');
  $('#rankimg a').remove();
  $('#rankimg').append(link);
  */
  var data = dataurl.split(",")[1];
  $("#imgdata").val(data);
  $("#imgname").val(fn);
  $("#imgdownload").submit();
}
$(function() {
  $("#capture").click(function () {
    downloadCanvas($("#rankimg canvas")[0]);
  });
});

/*
 * theme
 */
$(function() {
  $(".list.theme li").each(function (i,obj) {
    $(obj).click(function() {
      $(".list.theme li").removeClass("sel");
      $(this).addClass("sel");
      // re-render table
      dorender($(this).attr("data-value"));
    });
  });
});






/*
 * edit tool
 */
$(function() {
  function submit(action,v) {
    $('#editform-action').val(action);
    $('#editform-v').val(v);
    var jstr = $('#editform').serialize();
    console.log(jstr);
    $.ajax({
      url: "/!/modify/",
      type: "POST",
      data: jstr,
      success: function(r) {
        console.log(r);
        showMessage(r.message);
      }
    });
  }

  $('#editstart').click(function () {
    var clears = ['0','1','2','3','4','5','6','7'];
    var ranks = ['F','E','D','C','B','A','AA','AAA'];
    $('#editwidget').removeClass('beforeedit');
    $('#editwidget').addClass('afteredit');
    /* load ranktable from webpage */
    $('#editsonglist').load('./table/?edit=1', function () {
      /* attach edit button to each songs */
      $('.edit-rank').click(function(e) {
        var rank_str = $(this).attr('data-rank');
        var rank = ranks.indexOf(rank_str);
        if (rank < 0) {
          alert('error');
          return;
        }
        $(this).removeClass('edit-rank-'+ranks[rank]);
        rank = (rank+1)%9;
        $(this).addClass('edit-rank-'+ranks[rank]);
        $(this).attr('data-rank', ranks[rank]);
        var param = [{'id':parseInt($(this).parent().attr('data-id')),'rank':rank}];
        submit('edit',JSON.stringify(param));
      });
      $('.edit-clear').click(function(e) {
        var clear = parseInt($(this).attr('data-clear'));
        $(this).removeClass('edit-clear-'+clears[clear]);
        clear = (clear+1)%8;
        $(this).addClass('edit-clear-'+clears[clear]);
        $(this).attr('data-clear', clear);
        var param = [{'id':parseInt($(this).parent().attr('data-id')),'clear':clear}]
        submit('edit',JSON.stringify(param));
      });
    });
    
  });

  /* If web cache exists, then ask and remove it */
  var tname =tablename;
  if (tname && editmode) {
    var savedata = loadSetting(tname + "_data");
    if (savedata) {
      var chk = confirm("기존에 저장된 데이터를 발견했습니다.\n불러오시겠습니까? [y/n]");
      if (chk == 'n') {
      } else if (chk == 'y') {
        var savedata = JSON.parse(str);
        if (savedata.savedata_version == 1.0) {
          alert("버전이 호환되지 않아 불러올 수 없습니다.");
          return;
        }
        var param = [];
        for (var pkid in savedata.songs) {
          var sitem = savedata.songs[item.pkid];
          var item = {
            'id': pkid,
            'clear': sitem.clear,
            'rate': sitem.rate
          };
          param.push(item);
        }
        submit('edit',JSON.stringify(param))
      }
    }
  }
});
