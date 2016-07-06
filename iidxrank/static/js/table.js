//
// table renderer script
// by @lazykuna, under MIT License.
// COMMENT: requires default skin, if no default skin designated.
//


function DummyRenderer(ctx) {
  var self = this;
  self.ctx = ctx;

  self.isLoaded = function() { return true; }

  /** Theme Constants */
  self.theme_cate_margin = 0;
  self.margin_top = 20;

  self.drawCell = function(d,x,y,w,h) {
  }

  self.drawCategory = function(d,x,y,w,h) {
  }

  self.drawCategoryBox = function(d,x,y,w,h) {
  }

  self.drawTableBefore = function(d,x,y,w,h) {
  }

  self.drawTableAfter = function(d,x,y,w,h) {
  }
}

var TableRenderer = function(renderer) {
  var self = this;
  self._canvas = document.createElement("canvas");
  var ctx = self._canvas.getContext("2d");
  self.getContext = function () { return ctx; }
  self.getCanvas = function() { return self._canvas; }
  self._width = 1000;
  self._height = 1000;
  self._margin = 20;
  self._colwidth = 140;
  self._itemcol = 5;
  self._itemheight = 30;
  self._itemwidth = 200;  // will be recalculated automatically
  function _CalculateHeight(t) {
    // calculate total table size
    var _h = self._margin + self.renderer.margin_top;
    for (var i in t) {
      _h += self._itemheight * Math.floor((t[i].items.length - 1) / self._itemcol + 1);
      _h += self.renderer.theme_cate_margin;
    }
    self._height = _h;
    // initalize canvas with properties
    self._canvas.width = self._width;
    self._canvas.height = self._height;
  }
  function _Reset() {
    self._x = self._margin;
    self._y = self.renderer.margin_top;
    self._innerwidth = self._width - self._margin * 2;
    self._itemwidth = (self._innerwidth - self._colwidth) / self._itemcol;
  }
  if (renderer == undefined) {
    self.renderer = new DummyRenderer(ctx);
  } else {
    self.renderer = renderer;
    self.renderer.ctx = ctx;
  }
  _Reset();

  function drawHorizLine(y) {
    drawBLine(ctx, self._x, y,
      self._x+self._itemwidth*self._itemcol+self._colwidth, y);
  }

  //
  // public functions
  //
  self.RenderColumn = function(data) {
    // /this should be private ...? TODO
    // save base y position
    var _y_save = self._y;
    ctx.beginPath();
    // first render all of the items
    for (var i in data.items) {
      console.log(i);
      self._x = self._margin + (i % self._itemcol) * self._itemwidth + self._colwidth;
      self._y = Math.floor(i / self._itemcol) * self._itemheight + _y_save;
      self.renderer.drawCell(data.items[i],self._x,self._y,self._itemwidth,self._itemheight);
    }
    // second render category
    self._y += self._itemheight;        // add itemheight
    var _cheight = self._y - _y_save;   // calc category height
    self._x = self._margin;
    ctx.closePath();
    // render category
    self.renderer.drawCategory(data,self._x,_y_save,self._colwidth,_cheight);
    // render total category box
    self.renderer.drawCategoryBox(data,self._x,_y_save,self._innerwidth,_cheight);
    self._y += self.renderer.theme_cate_margin;
  };
  self.RenderTable = function(tdata) {
    // calculate total table size at very first
    _Reset();
    _CalculateHeight(tdata.categories);
    // before rendering
    self.renderer.drawTableBefore(tdata.info,self._margin,self._margin_top,
      self._width-self._margin*2,self._height-self._margin-self._margin_top);
    // render table
    for (var i in tdata.categories) {
      self.RenderColumn(tdata.categories[i]);
    }
    // after rendering
    self.renderer.drawTableAfter(tdata.info,self._margin,self.renderer.margin_top,
      self._width-self._margin*2,self._height-self._margin-self.renderer.margin_top);
  }
  self.Clear = function() {
    // clear table inner position.
    // must be called before you redraw table.
    _Reset();
  }
  self.Click = function(tdata, x, y) {
    // get clicked item from click pos
    var sx = self._margin;
    var sy = self.renderer.margin_top;
    var item = undefined;
    for (var i in tdata.categories) {
      if (item) break;
      c = tdata.categories[i];
      if (c.categorytype == 1) {
        sy += self.renderer.theme_cate_margin;
      }
      for (var j in c.items) {
        if (j > 0 && j % self._itemcol == 0) {
          sy += self._itemheight;
        }
        sx = self._margin + self._colwidth + (j % self._itemcol) * self._itemwidth;
        if (x >= sx && x < sx + self._itemwidth &&
            y >= sy && y < sy + self._itemheight) {
          item = c.items[j];
          break;
        }
      }
      sy += self._itemheight;
    }
    return item;
  }
}

//
// some helpers for rendering
//
function RoundRect(ctx, x, y, w, h, color, stroke) {

}

function TextDrawer(ctx, fnt, fntsub, color="#000") {
  // regex used to catch subtitle
  var reg = /\(.+?\).*$|-.+?-.*$|~.+?~.*$|～.+?～.*$|”.+?”.*$|feat\..+$/g;
  var self = this;
  self.ctx = ctx;
  self.fnt = fnt;
  self.fntsub = fntsub;
  self.color = color; //"#cc66cc";

  this.drawText = function(text,x,y,w,h) {
    /* check is there any subtitle available */
    var subtitle = text.match(reg);
    var title = text;
    if (subtitle != null) {
      subtitle = subtitle.join(' ');
      title = text.replace(reg, "");
    } else {
      subtitle = "";
    }

    // get total text size
    var subtitle_x = 0;
    var textWidth = 0;
    self.ctx.font = self.fnt;
    textWidth += (subtitle_x = self.ctx.measureText(title).width);
    self.ctx.font = self.fntsub;
    textWidth += self.ctx.measureText(subtitle).width;

    // set context size
    var ratio = 1;
    if (textWidth > w) {
      ratio = w / textWidth;
    }

    // draw
    self.ctx.textAlign="left";
    self.ctx.setTransform(ratio,0,0,1,x+10,y);
    self.ctx.fillStyle = this.color;
    self.ctx.font = self.fnt;
    self.ctx.fillText(title, 0, 0);
    self.ctx.font = self.fntsub;
    self.ctx.fillText(subtitle, subtitle_x, 0);
    self.ctx.setTransform(1,0,0,1,0,0);
  };
}
