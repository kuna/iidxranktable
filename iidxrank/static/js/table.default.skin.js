//
// very-default skin of table renderer of @lazykuna
// by @lazykuna MIT License
//

function DefaultRenderer(ctx) {
  var self = this;
  self.ctx = ctx;

  // load image/resources
  var img_clear = new Image();
  img_clear.src = "/static/img/clearlamp2.png";
  self.isLoaded = function() {
    return (img_clear);
  }

  //
  // privates
  //
  var drawBLine = function(x1,y1,x2,y2) {
    self.ctx.strokeStyle = "#000";
    self.ctx.lineWidth=2;
    self.ctx.moveTo(x1-0.5, y1-0.5);
    self.ctx.lineTo(x2-0.5, y2-0.5);
    self.ctx.stroke();
  };

  var drawCLine = function(x1,y1,x2,y2) {
    self.ctx.strokeStyle = "#a0a0a0";
    self.ctx.lineWidth=1;
    self.ctx.moveTo(x1-0.5, y1-0.5);
    self.ctx.lineTo(x2-0.5, y2-0.5);
    self.ctx.stroke();
  };

  //
  // common works
  //

  /** Theme Constants */
  self.margin_top = 150;
  self.theme_cate_margin = 0;
  self.drawscore = false;
  self.renderforprint = false;

  self.drawCell = function(d,x,y,w,h) {
      /*
       * INFO table function will automatically close path
       * So you don't have to do beginpath ~ closepath.
       */

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
      if (d.data.version >= 23) fnt_color = "#C6F";
      tdrawer = new TextDrawer(self.ctx, "12px Arial", "9px Arial", fnt_color);
      tdrawer.drawText(d.data.title,x,y+h/2+4,w-35,h);
      // 3 draw border
      drawCLine(x,y+h,x+w,y+h);
      drawCLine(x+w,y,x+w,y+h);
      // 4 draw lamp
      if (d.clear > 0) {
        self.ctx.drawImage(img_clear,
            0,30 * (d.clear-1),15,h,
            x+w-15,y,15,h);
      }
      // 4 score TODO
      if (self.drawscore) {
      }
  }

  self.drawCategory = function(d,x,y,w,h) {
    self.ctx.fillStyle="#F8F8F8";
    self.ctx.fillRect(x,y,w,h);
    drawCLine(x+w,y,x+w,y+h);

    self.ctx.font = "12px Arial";
    self.ctx.textAlign="center";
    self.ctx.fillStyle="#000000";
    self.ctx.fillText(d.category, x+w/2, y+h/2+4);

    // lamp
    var totalcnt = d.items.length;
    if (totalcnt > 5) {
      var rw = 50;
      var rx = x + w/2 - rw/2;
      var ry = y + h/2 + 12;
      var rh = 5;
      var fillclr = [
        "#E0E0E0",
        "#CCCCCC",
        "#FFAAFF",
        "#CCFF33",
        "#3399FF",
        "#FF6633",
        "#FFFF99",
        "#33FFCC"];
      self.ctx.fillStyle=fillclr[0];
      self.ctx.fillRect(rx, ry, rw, rh);
      var clearrate = [1,0,0,0,0,0,0,0];
      var ccnt = 0;
      for (var i=1; i<=7; i++) {
        ccnt = 0;
        for (var j=0; j<totalcnt; j++) {
          if (d.items[j].clear >= i) ccnt++;
        }
        clearrate[i] = ccnt / totalcnt;
        console.log(clearrate[i]);

        self.ctx.fillStyle=fillclr[i];
        self.ctx.fillRect(rx, ry, rw*clearrate[i], rh);
      }
    }
  }

  self.drawCategoryBox = function(d,x,y,w,h) {
    self.ctx.beginPath();
    if (d.categorytype == 1) {
      drawBLine(x, y, x+w, y);
    } else {
      drawCLine(x, y, x+w, y);
    }
    self.ctx.closePath();
  }

  self.drawTableBefore = function(d,x,y,w,h) {
    // fill total white
    self.ctx.fillStyle = "#FFF";
    self.ctx.fillRect(0, 0, self.ctx.canvas.width, self.ctx.canvas.height);

    // render title
    self.ctx.font = "bold 30px Arial";
    self.ctx.textAlign="center";
    self.ctx.strokeStyle="#333";
    self.ctx.lineWidth=8;
    self.ctx.miterLimit=2;
    self.ctx.strokeText(d.title, x+w/2, 70);
    self.ctx.fillStyle="#EEE";
    self.ctx.fillText(d.title, x+w/2, 70);

    // DJ name, clear status
    self.ctx.font = "bold 14px Arial";
    self.ctx.textAlign="left";
    self.ctx.fillStyle="#000";
    self.ctx.fillText("DJ " + d.name, x + 12, 132);

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
    if (d.spdannum > 0) {
      self.ctx.fillStyle=gradecolor[d.spdannum];
      self.ctx.fillText("SP" + d.spdan, x+w-120, 132);
      self.ctx.fillStyle="#000";
      self.ctx.fillText("/", x+w-68, 132);
      self.ctx.fillStyle=gradecolor[d.dpdannum];
      self.ctx.fillText("DP" + d.dpdan, x+w-60, 132);
    }
  }

  self.drawTableAfter = function(d,x,y,w,h) {
    // very bottom line
    self.ctx.beginPath();
    drawBLine(x, y+h, x+w, y+h);
    self.ctx.closePath();
  }
}
