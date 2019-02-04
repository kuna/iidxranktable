/**
 * IIDX CSV Generator r190204
 * by @lazykuna
 *
 * MIT License
 *
 * usage:
 * javascript:$.getScript('https://iidx.insane.pe.kr/static/js/update.js');
 */

/** Will not load jquery.js as 573 site already uses it. */

(function(){

var IIDXCSVGenerator = function()
{
  var self = this;
  self.csv_sp = [];
  self.csv_dp = [];
  self.version = 26;
  self.version_str = "Rootage";
  self.request_interval = 500; /* ms */
  self.request_queue = []; /* [req_url, req_method, req_param, func_to_call_when_success, params, interval] */
  self.url_recent_list = 'https://p.eagate.573.jp/game/2dx/{0}/djdata/music/music_info.html?index={1}'; /* 0 - 19 */
  self.url_series_list = 'https://p.eagate.573.jp/game/2dx/{0}/djdata/music/series.html'; /* POST request */
  self.url_series_list_post_arg = 'list={0}&play_style={1}&s=1&rival='; /* 0 - 25(:version-1), 0(SP)/1(DP) */
  self.url_level_list = 'https://p.eagate.573.jp/game/2dx/{0}/djdata/music/difficulty.html'; /* POST */
  self.url_level_list_post_arg = 'difficult={0}&play_style={1}&disp=1'; /* 0 - 11(:level-1), 0(SP)/1(DP) */
  self.stop = false; /* for stopping task */
  self.clear_types = [
     "NO PLAY",
     "FAILED",
     "ASSIST CLEAR",
     "EASY CLEAR",
     "CLEAR",
     "HARD CLEAR",
     "EX HARD CLEAR",
     "FULLCOMBO CLEAR"
  ];

  function generate_window()
  {
    function _diag()
    {
      // show dialog
      $('#iidxcsv_dialog').remove();
      $('<div id="iidxcsv_dialog" title="IIDX CSV Generator">IIDX CSV Generator is here!<br>Status: <span id="csv_status">Ready</span><br><center><button id="csv_allsong" style="font-weight:bold;">CSV (all song)</button><br><button id="csv_stop" disabled>Stop</button><br><button id="csv_download_sp" disabled>Download CSV (SP)</button><br><button id="csv_download_dp" disabled>Download CSV (DP)</button><br><button id="csv_uploadtoinsane" disabled>Upload to iidx.insane</button></center></div>').dialog();
      // attach events
      $('#csv_allsong').click(csv_allsong);
      //$('#csv_recentrecord').click(csv_recentrecord);
      $('#csv_stop').click(csv_stop);
      $('#csv_download_sp').click(csv_download_sp);
      $('#csv_download_dp').click(csv_download_dp);
    }
    if (!window._jquery_ui)
    {
      window._jquery_ui = true;
      $('<link/>', {rel:'stylesheet',type:'text/css',href:'//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css'}).appendTo('head');
      $('html > head').append('<style>#iidxcsv_dialog button { width: 200px; height: 28px; border-radius: 5px; cursor:pointer; margin-top: 10px; } #iidxcsv_dialog button:hover { background-color: #999; }</style>');
      $.getScript('https://code.jquery.com/ui/1.12.1/jquery-ui.js', _diag);
    }
    else
    {
      //already loaded
      _diag();
    }
  }

  function set_msg(msg)
  {
    $('#csv_status').text(msg);
  }

  function set_progress(msg, progress)
  {
    $('#csv_status').text(msg + ' (' + Math.round(progress*100) + '%)');
  }

  function set_error(msg)
  {
    $('#csv_status').html('<span style="color:#900">'+msg+'</span>');
  }

  function check_login_state()
  {
    set_msg('(Ready)');
  }

  function do_request()
  {
    // in case of stop
    if (self.stop) { return; }
    if (self.request_queue.length <= 0) { return; /* end */ }
    // pop a request
    var req = self.request_queue.shift();
    var interval_ = req[5];
    // if no request but only function call
    if (req[0] === null)
    {
      if (req[3] !== null) { req[3]( req[4] ); }
      setTimeout(do_request, interval_);
      return;
    }
    var url_ = req[1];
    var method_ = req[0].toUpperCase();
    var params_ = req[2];
    if (method_ == 'GET' && params_ != null)
    {
      url_ += '?' + params_;
      params_ = null;
    }
    // do request
    $.ajax({
      type: method_,
      url: url_,
      data: params_,
      success: function(data) {
        /** data process */
        var dom = $(data);
        if (req[3] !== null) { req[3]( req[4], dom ); }
        /** calling for next request */
        setTimeout(do_request, interval_);
      },
      error: function (e) {
        /** error message & cancel all queue */
        set_error("Error - request failed.");
        console.log(req);
        console.log(e);
        self.request_queue = [];
      }
    });
  }

  function _get_score_from_str(str)
  {
    //var ex = str.replace(/\((.*?)\)/g, "");
    return str.match(/[\d]+/g);
  }

  function _get_record_from_imgsrc(imgsrc)
  {
    return imgsrc.replace(/(.*?)score_icon\//g,"").replace(".gif","").replace(/[a-z]+/,"");
  }

  function csv_allsong()
  {
    self.csv_initialize();
    var series_max = self.version;
    var level_max = 12;  // XXX: set to 12
    var level_cached = {}; /* songname_DIFF : level_num */

    function _cache_level(p, dom)
    {
      var level = p[0];
      var style = p[1];
      var offset = p[2];
      // if invalid offset then exit (END OF VERSION)
      // else, insert request(front) for next offset
      var dom_table = dom.find("div.series-difficulty");
      if (dom_table.length <= 0)
      {
        return;
      }
      // next page: push to first
      if (dom.find('div.next-prev a').length > 0) /* IF NEXT BUTTON */
      {
        self.request_queue.unshift(["GET", self.url_level_list.format(self.version) + "?" +
          self.url_level_list_post_arg.format(level, 0) + "&offset=" + (offset+50), null,
          _cache_level, [level,style,offset+50], self.request_interval]); // XXX: check value: why unknown?
      }
      // cache song level
      var dom_tr = dom_table.find('tr').slice(2);
      for (var i=0; i<dom_tr.length; i++)
      {
        var r = dom_tr.eq(i);
        var tds = r.find('td');
        var title = tds.eq(0).text();
        var diff = tds.eq(1).text();
        level_cached[title + "_" + diff + "_" + style] = level;
      }
      set_progress("Caching song level ...", level/(level_max+series_max));

      console.log("TOTAL CACHED SONGS: " + Object.keys(level_cached).length + " - " + [level,style,offset].join(","));
    }
    function _process_series(p, dom)
    {
      var idx = p[0];
      var style = p[1];
      var offset = p[2];
      var song_cached = [];

      // if invalid offset then exit (END OF VERSION)
      // else, insert request(front) for next offset
      var dom_tables = dom.find("div.series-difficulty");
      if (dom_tables.length <= 0)
      {
        return;
      }
      // meta scan
      var version = dom.find('div#series-select').find('select option:selected').eq(0).text()
      // song scan
      for (var i=0; i<dom_tables.length; i++)
      {
        var dom_tr = dom_tables.eq(i).find('tr').slice(2);
        for (var j=0; j<dom_tr.length; j++)
        {
          var tds = dom_tr.eq(j).find('td');
          var title = tds.eq(0).text();
          var diff = tds.eq(1).text();
          var level = level_cached[title + "_" + diff + "_" + style]; /* XXX: may be undefined */
          var ex_raw_arr = _get_score_from_str(tds.eq(3).text());
          var ex = ex_raw_arr[0];
          var pg = ex_raw_arr[1];
          var gr = ex_raw_arr[2];
          var clear_type_idx = _get_record_from_imgsrc(tds.eq(4).find("img").eq(0).attr("src"));
          var dj_level = _get_record_from_imgsrc(tds.eq(2).find("img").eq(0).attr("src"));
          var clear_type = self.clear_types[clear_type_idx];
          var r = [level/*difficulty*/,ex,pg,gr,"---"/* miss */,clear_type,dj_level/*dj level*/];
          if (song_cached.length > j)
            song_cached[j] = song_cached[j].concat(r);
          else
            song_cached.push([version,title,"---"/*genre*/,"---"/*artist*/,0].concat(r));
        }
      }
      // add rows to csv
      for (var i=0; i<song_cached.length; i++)
      {
        csv_insert_row(style, song_cached[i]);
      }
      set_progress("Parsing series ...", (level_max+idx+1)/(level_max+series_max));
    }
    function _process_finish()
    {
      set_msg("All song done");
      csv_prepared();
    }

    /** request for level caching */
    for (var i=0; i<level_max; i++)
    {
      self.request_queue.push(["GET", self.url_level_list.format(self.version),
        self.url_level_list_post_arg.format(i, 0),
        _cache_level, [i+1,0,0], self.request_interval]);
      self.request_queue.push(["GET", self.url_level_list.format(self.version),
        self.url_level_list_post_arg.format(i, 1),
        _cache_level, [i+1,1,0], self.request_interval]);
    }
    /** request for song per series */
    for (var i=0; i<series_max; i++)
    {
      self.request_queue.push(["GET", self.url_series_list.format(self.version),
        self.url_series_list_post_arg.format(i, 0),
        _process_series, [i,0,0], self.request_interval]);
      self.request_queue.push(["GET", self.url_series_list.format(self.version),
        self.url_series_list_post_arg.format(i, 1),
        _process_series, [i,1,0], self.request_interval]);
    }
    self.request_queue.push([null, null, null, _process_finish, null, 0]);

    set_msg("Initalizing ...");
    do_request();
  }

  function csv_recentrecord() /* DEPRECIATED */
  {
    self.csv_initialize();
    var count_max = 20;

    function _get_meta(d)
    {
      var t = d.find('div.music-name li').eq(1).text();
      var g = d.find('div.music-name li').eq(2).text();
      var a = d.find('div.music-name li').eq(3).text();
      return {'title': t, 'genre': g, 'artist': a};
    }
    function _get_chart_meta(c)
    {
      var rows = c.find("tr");
      var clear_type_html = rows.eq(1).find("td").eq(1).find("img").eq(0).attr("src");
      var dj_level_html = rows.eq(2).find("td").eq(1).find("img").eq(0).attr("src");
      var clear_type_idx = _get_record_from_imgsrc(clear_type_html);
      var dj_level = _get_record_from_imgsrc(dj_level_html);
      var clear_type = self.clear_types[clear_type_idx];
      var ex_raw = rows.eq(3).find("td").eq(1).text();
      var ex_raw_arr = _get_score_from_str(ex_raw);
      var ex = ex_raw_arr[0];
      var pg = ex_raw_arr[1];
      var gr = ex_raw_arr[2];
      var miss = rows.eq(4).find("td").eq(1).text();
      return [0/*difficulty*/,ex,pg,gr,miss,clear_type,dj_level/*dj level*/];
    }
    function _get_row(m, n_obj, h_obj, a_obj)
    {
      n_m = _get_chart_meta(n_obj);
      h_m = _get_chart_meta(h_obj);
      a_m = _get_chart_meta(a_obj);
      return [self.version_str, m.title, m.genre, m.artist, 0/*playcount*/]
        .concat(n_m, h_m, a_m);
    }
    function _process_dom(idx, dom)
    {
      var m = _get_meta(dom);
      var d = dom.find('div.music-detail');
      if (d.length == 0)
      {
        set_error("Error - Check login");
        return;
      }
      csv_insert_row(0, _get_row(m,d.eq(0),d.eq(1),d.eq(2)));
      csv_insert_row(1, _get_row(m,d.eq(3),d.eq(4),d.eq(5)));
      set_progress("Recent record", (idx+1)/count_max);
    }
    function _process_finish()
    {
      set_msg("Recent record done");
      csv_prepared();
    }

    self.request_queue = [];
    self.request_queue.push(["GET",
      "https://p.eagate.573.jp/game/2dx/{0}/djdata/music/recent.html".format(self.version), null,
      null, null, self.request_interval]);
    for (var i=0; i<count_max; i++)
    {
      self.request_queue.push(["GET", self.url_recent_list.format(self.version, i), null,
        _process_dom, i, self.request_interval]);
    }
    self.request_queue.push([null, null, null, _process_finish, null, 0]);

    set_progress("Initalizing ...");
    do_request();
  }

  function csv_initialize()
  {
    self.csv = [];
    /* it is column, actually. */
    cols = [
      "バージョン",   /* version */
      "タイトル",     /* title */
      "ジャンル",     /* genre */
      "アーティスト", /* artist */
      "プレー回数",   /* playcount */
      "NORMAL 難易度",/* difficulty */
      "NORMAL EXスコア",
      "NORMAL PGreat",
      "NORMAL Great",
      "NORMAL ミスカウント",
      "NORMAL クリアタイプ",
      "NORMAL DJ LEVEL",
      "HYPER 難易度",
      "HYPER EXスコア",
      "HYPER PGreat",
      "HYPER Great",
      "HYPER ミスカウント",
      "HYPER クリアタイプ",
      "HYPER DJ LEVEL",
      "ANOTHER 難易度",
      "ANOTHER EXスコア",
      "ANOTHER PGreat",
      "ANOTHER Great",
      "ANOTHER ミスカウント",
      "ANOTHER クリアタイプ",
      "ANOTHER DJ LEVEL",
      "最終プレー日時"/* play time: %Y-%M-%D %h:%m */
    ]
    self.csv_insert_row(0,cols);
    self.csv_insert_row(1,cols);

    /**
     * CLEAR TYPES:
     * NO PLAY
     * FAILED
     * EASY CLEAR
     * CLEAR
     * HARD CLEAR
     * EX HARD CLEAR
     * FULLCOMBO CLEAR
     */

    self.stop = false;
    $("#csv_stop").prop("disabled", false);
    $("#csv_download_sp").prop("disabled", true);
    $("#csv_download_dp").prop("disabled", true);
    //$("#csv_uploadtoinsane").prop("disabled", true);
  }

  function csv_prepared()
  {
    $("#csv_stop").prop("disabled", true);
    $("#csv_download_sp").prop("disabled", false);
    $("#csv_download_dp").prop("disabled", false);
    //$("#csv_uploadtoinsane").prop("disabled", false);
  }

  function csv_insert_row(type,row)
  {
    /* NO EMPTY COLUMN IS PERMITTED: use --- */
    if (type==0)
      self.csv_sp.push(row);
    else
      self.csv_dp.push(row);
  }

  function csv_to_string(type)
  {
    function _row_to_string(row)
    {
      var r = row.slice();
      r[0] = "\"" + r[0].replace(/"/g, '""') + "\"";
      r[1] = "\"" + r[1].replace(/"/g, '""') + "\"";
      r[2] = "\"" + r[2].replace(/"/g, '""') + "\"";
      r[3] = "\"" + r[3].replace(/"/g, '""') + "\"";
      return r.join(',');
    }
    var csv = (type==0)?self.csv_sp:self.csv_dp;
    var s = "";
    for (var i=0; i<csv.length; i++)
    {
      s += _row_to_string(csv[i]) + "\n";
    }
    return s;
  }

	function _download(filename, text) {
		var element = document.createElement('a');
		element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
		element.setAttribute('download', filename);
		element.style.display = 'none';
		document.body.appendChild(element);
		element.click();
		document.body.removeChild(element);
	}
	function _gen_filename(fn) { return fn + "_" + new Date().toISOString().split('T')[0] + ".csv"; }
  function csv_download_sp() { _download(_gen_filename("IIDX_SP"), csv_to_string(0)); }
  function csv_download_dp() { _download(_gen_filename("IIDX_DP"), csv_to_string(1)); }

  function csv_stop() { set_msg("*Stopped*"); self.stop = true; }

  function _string_prototype_format()
	{
		String.prototype.format = function() {
			a = this;
			for (k in arguments) {
				a = a.replace("{" + k + "}", arguments[k])
			}
			return a;
		}
	}
  _string_prototype_format();

  self.check_login_state = check_login_state;
  self.generate_window = generate_window;
  self.csv_allsong = csv_allsong;
  self.csv_recentrecord = csv_recentrecord;
  self.csv_initialize = csv_initialize;
  self.csv_insert_row = csv_insert_row;
  self.csv_to_string = csv_to_string;
  self.csv_download_sp = csv_download_sp;   // XXX: check(call) this func and csv_sp variable.
  self.csv_download_dp = csv_download_dp;
  self.stop_ = csv_stop;

  return self;
};

var csv = IIDXCSVGenerator();
csv.generate_window();
csv.check_login_state();

// in case if you want to customize ... :-)
window._csv = csv;

})();
