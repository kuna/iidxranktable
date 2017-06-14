//
// very-default skin of table renderer of @lazykuna
// by @lazykuna MIT License
//

function Rev2Renderer(ctx) {
  var self = this;
  self.ctx = ctx;

  // load image/resources
  var img_loadcnt = 0;
  var img_clear = new Image();
  var img_rank = new Image();
  img_clear.onload = function() { img_loadcnt++; }
  img_rank.onload = function() { img_loadcnt++; }
  self.isLoaded = function() { return img_loadcnt >= 2; }

  img_clear.src = "static/img/clearlamp_rev2.png";
  img_rank.src = "static/img/rank.png";


  //
  // privates
  //
  var drawBLine = function(x1,y1,x2,y2) {
    self.ctx.strokeStyle = "#333";
    self.ctx.lineWidth=2;
    self.ctx.moveTo(x1-0.5, y1-0.5);
    self.ctx.lineTo(x2-0.5, y2-0.5);
    self.ctx.stroke();
  };

  var drawCLine = function(x1,y1,x2,y2) {
    self.ctx.strokeStyle = "#a0a0a0";
    self.ctx.lineWidth=1;
    x1 = Math.floor(x1);
    x2 = Math.floor(x2);
    y1 = Math.floor(y1);
    y2 = Math.floor(y2);
    self.ctx.moveTo(x1-0.5, y1-0.5);
    self.ctx.lineTo(x2-0.5, y2-0.5);
    self.ctx.stroke();
  };

  //
  // common works
  //

  /** Theme Constants */
  self.width = 1000;
  self.colwidth = 140;
  self.itemcol = 6;
  self.itemheight = 48;

  self.margin_top = 150;
  self.margin_bottom = 50;
  self.theme_cate_margin = 0;
  self.theme_maincate_margin = 20;
  self.drawscore = true;
  self.renderforprint = false;

  self.drawCell = function(d,x,y,w,h) {
      /*
       * INFO table function will automatically close path
       * So you don't have to do beginpath ~ closepath.
       */
      
      var x = Math.floor(x+10);
      var w = Math.floor(w-10);
      var h = h-10;

      // 1 draw background
      self.ctx.fillStyle="#FFFFFF";
      if (d.data.diff == 'H') {
        self.ctx.fillStyle="#FFFFF0";
      } else if (d.data.diff == 'N') {
        self.ctx.fillStyle="#F0F0FF";
      }
      self.ctx.fillRect(x,y,w,h);

      // 2 draw font
      fnt_color = "#000";
      if (d.data.version >= 24) fnt_color = "#C6F";
      tdrawer = new TextDrawer(self.ctx, "12px Arial", "9px Arial", fnt_color,true);
      tdrawer.drawText(d.data.title,x,y+h/2+4,w-20,h);

      // 3 draw border
      drawCLine(x,y+h,x+w,y+h);
      drawCLine(x,y,x+w,y);
      drawCLine(x+w,y,x+w,y+h);
      drawCLine(x,y,x,y+h);

      // 4 draw lamp
      var lamp_idx = d.clear;
      if (d.rate > 88.88 && d.clear == 7)
        lamp_idx++;
      var sw = 104;
      var sh = 47;
      var sx=0, sy=lamp_idx * 47;
      self.ctx.drawImage(img_clear,
          sx,sy,sw,sh,
          x,y,w,h);
      self.rank_count[d.clear]++;   // accumulate count

      // 4 score TODO
      if (self.drawscore) {
        var sx = 0;
        var sy = -1;
        var sw = 16;
        var sh = 16;
        if (d.rank == "F") sy=116; //sy = 116;  
        else if (d.rank == "E") sy = 100;
        else if (d.rank == "D") sy = 83;
        else if (d.rank == "C") sy = 67;
        else if (d.rank == "B") sy = 50;
        else if (d.rank == "A") sy = 33;
        else if (d.rank == "AA") sy = 16;
        else if (d.rank == "AAA") sy = 0;
        if (sy >= 0 && sy <= 50)
        {
          self.ctx.drawImage(img_rank,
              sx,sy,sw,sh,
              x+w-12,y-3,sw,sh);
        }
      }
  }

  self.drawCategory = function(d,x,y,w,h) {
    var nh = h - 10;
    self.ctx.fillStyle="#F8F8F8";
    self.ctx.fillRect(x,y,w,nh);
    drawCLine(x+w,y,x+w,y+nh);

    self.ctx.font = "bold 13px Arial";
    self.ctx.textAlign="center";
    self.ctx.fillStyle="#000000";
    self.ctx.fillText(d.category, x+w/2, y+nh/2+6);
    self.ctx.shadowBlur=0;

    self.ctx.beginPath();
    drawCLine(x, y, x+w, y);
    drawCLine(x, y, x, y+nh);
    drawCLine(x, y+nh, x+w, y+nh);
    drawCLine(x+w, y, x+w, y+nh);
    self.ctx.closePath();

    // lamp
    // won't draw in here
  }

  self.drawCategoryBox = function(d,x,y,w,h) {
    /*
    self.ctx.beginPath();
    if (d.categorytype == 1) {
      drawBLine(x, y, x+w, y);
    } else {
      drawCLine(x, y, x+w, y);
    }
    self.ctx.closePath();
    */
    if (d.categorytype == 1) {
      self.ctx.beginPath();
      drawBLine(x, y-15, x+w, y-15);
      self.ctx.closePath();
    }
  }

  self.drawTableBefore = function(d,x,y,w,h) {
    var userdata = d.userdata;
    var tableinfo = d.tableinfo;

    var title = d.tableinfo.title;
    if (!title) title = d.title;
    var username = d.userdata.djname;
    if (!username) username = d.username;
    var spclass = d.userdata.spclass;
    var dpclass = d.userdata.dpclass;
    var spclassstr = d.userdata.spclassstr;
    var dpclassstr = d.userdata.dpclassstr;

    // init
    self.rank_count = [0,0,0,0,0,0,0,0];

    // fill total white
    self.ctx.fillStyle = "#FFF";
    self.ctx.fillRect(0, 0, self.ctx.canvas.width, self.ctx.canvas.height);

    // render title
    self.ctx.font = "bold 32px Arial";
    self.ctx.textAlign="center";
    self.ctx.strokeStyle="#333";
    self.ctx.shadowColor="#000000";
    self.ctx.shadowBlur=7;
    self.ctx.miterLimit=1;
    self.ctx.lineWidth=7;
    self.ctx.strokeText(title, x+w/2, 70);
    self.ctx.shadowBlur=0;
    self.ctx.fillStyle="#FFF";
    self.ctx.fillText(title, x+w/2, 70);

    var yy=142;
    // DJ name, clear status
    self.ctx.font = "bold 14px Arial";
    self.ctx.textAlign="left";
    self.ctx.fillStyle="#000";
    self.ctx.fillText("DJ " + username, x + 12, yy);

    var gradecolor = [
      "#000000",
      "#000000",
      "#AADD33",  // 2
      "#AADD33",
      "#AADD33",
      "#AADD33",
      "#AADD33",
      "#AADD33",
      "#AADD33",
      "#3399FF",  // 9
      "#3399FF",
      "#3399FF",
      "#3399FF",
      "#3399FF",
      "#3399FF",
      "#3399FF",
      "#3399FF",
      "#FF6666",  // 17
      "#FF6666",
      "#999999",  // 19
      "#DDDD33",  // 20
      ]
    if (spclass > 0) {
      self.ctx.fillStyle=gradecolor[spclass];
      self.ctx.fillText("SP" + spclassstr, x+w-120, yy);
      self.ctx.fillStyle="#000";
      self.ctx.fillText("/", x+w-68, yy);
      self.ctx.fillStyle=gradecolor[dpclass];
      self.ctx.fillText("DP" + dpclassstr, x+w-60, yy);
    }
  }

  function formatDate(d) {
    var month = '' + (d.getMonth()+1);
    var day = '' + d.getDate();
    var year = d.getFullYear();
    if (month.length < 2) month = '0'+month;
    if (day.length < 2) day = '0'+day;
    return [year, month, day].join('-');
  }

  self.drawTableAfter = function(d,x,y,w,h) {
    var tabletime = d.tableinfo.time;
    var copyright = d.tableinfo.copyright;

    // very bottom line
    self.ctx.beginPath();
    drawBLine(x, y+h, x+w, y+h);
    self.ctx.closePath();
    // date
    self.ctx.fillStyle="#999";
    self.ctx.font = "13px Arial";
    self.ctx.textAlign="right";
    console.log(d);
    var tdate = new Date(tabletime * 1000);
    self.ctx.fillText("Today: " + formatDate(new Date()) + " / Updated: " + formatDate(tdate),
        x+w, y+h+20);
    // copyright
    if (copyright) {
      self.ctx.textAlign="left";
      self.ctx.fillText(copyright, x, y+h+20);
    }
    self.ctx.textAlign="center";
    // rank count
    var ey = y+h;
    self.ctx.fillStyle="#ddd";
    self.ctx.fillRect(x+150,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[0], x+165, ey+20);
    self.ctx.fillStyle="#bbb";
    self.ctx.fillRect(x+190,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[1], x+205, ey+20);
    self.ctx.fillStyle="#ca9";
    self.ctx.fillRect(x+230,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[2], x+245, ey+20);
    self.ctx.fillStyle="#9c9";
    self.ctx.fillRect(x+270,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[3], x+285, ey+20);
    self.ctx.fillStyle="#9ac";
    self.ctx.fillRect(x+310,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[4], x+325, ey+20);
    self.ctx.fillStyle="#c99";
    self.ctx.fillRect(x+350,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[5], x+365, ey+20);
    self.ctx.fillStyle="#cc9";
    self.ctx.fillRect(x+390,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[6], x+405, ey+20);
    self.ctx.fillStyle="#9cc";
    self.ctx.fillRect(x+430,ey+6,30,20);
    self.ctx.fillStyle="#fff";
    self.ctx.fillText(self.rank_count[7], x+445, ey+20);
  }
}
