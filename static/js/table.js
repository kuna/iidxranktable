//
// table renderer script
// by @lazykuna, under MIT License.
// COMMENT: requires default skin, if no default skin designated.
// rev 170614
//


function DummyRenderer(ctx) {
  var self = this;
  self.ctx = ctx;

  self.isLoaded = function() { return true; }

  /** Theme Constants */
  self.theme_cate_margin = 0;
  self.margin_top = 20;
  self.margin_bottom = 20;

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

function getOffset(el) {
  /*
  el = el.getBoundingClientRect();
  alert(el.top);
  return {
    left: el.left + window.scrollX,
    top: el.top + window.scrollY
  }
  */
  return {
    left: el.offsetLeft,
    top: el.offsetTop
  };
}

var TableRenderer = function(renderer) {
  var self = this;
  self._canvas = document.createElement("canvas");
  var ctx = self._canvas.getContext("2d");
  self.getContext = function () { return ctx; }
  self.getCanvas = function() { return self._canvas; }
  self.onItemClick = function(e,item,pos) { console.log(item); }
  self.onItemHover = undefined;
  self._width = 1000;
  self._height = 1000;
  self._margin = 20;
  self._colwidth = 150;
  self._itemcol = 5;
  self._itemheight = 30;
  self._itemwidth = 200;  // will be recalculated automatically
  self._vitempos = [];    // (itemdata, pos: (x, y, w, h), parent)

  // backward compatibility
  if (renderer.width) self._width = renderer.width;
  if (renderer.colwidth) self._colwidth = renderer.colwidth;
  if (renderer.itemcol) self._itemcol = renderer.itemcol;
  if (renderer.itemheight) self._itemheight = renderer.itemheight;
  if (renderer.theme_maincate_margin === undefined) renderer.theme_maincate_margin = 0;

  function convPos(e,obj) {
    //var offset = obj.offset();
    var offset = getOffset(obj[0]);
    var ratio = 1.0/obj.width()*self._width;
    var x = (e.pageX - offset.left) * ratio;
    var y = (e.pageY - offset.top) * ratio;
    return {'x':x,'y':y};
  }
  function onItemClick_internal(e) {
    if (self.onItemClick === undefined)
      return;
    var p = convPos(e,$(this));
    for (var idx in self._vitempos)
    {
      var itempos = self._vitempos[idx];
      if (p.x >= itempos.pos[0] && p.x < itempos.pos[2] &&
          p.y >= itempos.pos[1] && p.y < itempos.pos[3])
      {
        self.onItemClick(e, itempos.item, itempos.idx);
        return;
      }
    }
    self.onItemClick(e, undefined, -1);
  }
  function onItemHover_internal(e) {
    if (self.onItemHover === undefined)
      return;
    var p = convPos(e,$(this));
    for (var idx in self._vitempos)
    {
      var itempos = self._vitempos[idx];
      if (p.x >= itempos.pos[0] && p.x < itempos.pos[2] &&
          p.y >= itempos.pos[1] && p.y < itempos.pos[3])
      {
        self.onItemHover(e, itempos.item, itempos.idx);
        return;
      }
    }
  }
  function _CalculateHeight(t) {
    // calculate total table size
    var _h = self.renderer.margin_bottom + self.renderer.margin_top;
    var idx=0;
    for (var i in t) {
      _h += self._itemheight * Math.floor((t[i].items.length - 1) / self._itemcol + 1);
      if (idx > 0)
      {
        _h += self.renderer.theme_cate_margin;
        if (t[i].categorytype == 1) _h += self.renderer.theme_maincate_margin;
      }
      idx++;
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
  self.RenderColumn = function(data,idx) {
    // margin calculate first
    if (idx > 0)
    {
      self._y += self.renderer.theme_cate_margin;
      if (data.categorytype == 1) {
        self._y += self.renderer.theme_maincate_margin;
      }
    }
    // save base y position
    var _y_save = self._y;
    ctx.beginPath();
    // first render all of the items
    var cell_idx = 0;
    for (var i in data.items) {
      self._x = self._margin + (i % self._itemcol) * self._itemwidth + self._colwidth;
      self._y = Math.floor(i / self._itemcol) * self._itemheight + _y_save;
      self.renderer.drawCell(data.items[i],self._x,self._y,self._itemwidth,self._itemheight,cell_idx,idx);
      cell_idx += 1;
      // append item to _vitempos
      self._vitempos.push({
        'item': data.items[i],
        'idx': cell_idx,
        'pos': [self._x, self._y, self._x+self._itemwidth, self._y+self._itemheight]
      });
    }
    // second render category
    self._y += self._itemheight;        // add itemheight
    var _cheight = self._y - _y_save;   // calc category height
    self._x = self._margin;
    ctx.closePath();
    // render category
    self.renderer.drawCategory(data,self._x,_y_save,self._colwidth,_cheight,idx);
    // render total category box
    self.renderer.drawCategoryBox(data,self._x,_y_save,self._innerwidth,_cheight,idx);
  };
  self.RenderTable = function(tdata, bWait, callback) {
    // wait until loading is done
    if (bWait !== undefined && !self.renderer.isLoaded()) {
      setTimeout(function() {
        self.RenderTable(tdata, bWait, callback);
      }, 100);
      return;
    }

    var bSucceed = true;

    // check tdata validation
    if (!('categories' in tdata))
    {
      bSucceed = false;
      if (callback) { callback(bSucceed); }
      return;
    }

    // calculate total table size at very first
    _Reset();
    _CalculateHeight(tdata.categories);
    // before rendering
    self.renderer.drawTableBefore(tdata,self._margin,self._margin,
      self._width-self._margin*2,self._height-self.renderer.margin_bottom-self._margin);
    // render table
    var idx=0;
    for (var i in tdata.categories) {
      self.RenderColumn(tdata.categories[i],idx);
      idx += 1;
    }
    // after rendering (draw bottom things mostly)
    self.renderer.drawTableAfter(tdata,self._margin,self.renderer.margin_top,
      self._width-self._margin*2,self._height-self.renderer.margin_bottom-self.renderer.margin_top);

    // attach event
    $(self._canvas).click(onItemClick_internal);
    $(self._canvas).mousemove(onItemHover_internal);

    // if callback func exists?
    if (callback) { callback(bSucceed); }
  }
  self.Clear = function() {
    // clear table inner position.
    // must be called before you redraw table.
    _Reset();
  };

  // helper func
  self.RenderTo = function(tdata, dest) {
    var todest = function() {
      var canvas = self.getCanvas();
      $(canvas).addClass('ranktable');
      dest.append(canvas);
    }
    self.RenderTable(tdata, true, todest);
  };
  self.Redraw = function(tdata) {
    self.RenderTable(tdata, true);
  }
}

//
// some helpers for rendering
//
function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
  if (typeof stroke == 'undefined') {
    stroke = true;
  }
  if (typeof radius === 'undefined') {
    radius = 5;
  }
  if (typeof radius === 'number') {
    radius = {tl: radius, tr: radius, br: radius, bl: radius};
  } else {
    var defaultRadius = {tl: 0, tr: 0, br: 0, bl: 0};
    for (var side in defaultRadius) {
      radius[side] = radius[side] || defaultRadius[side];
    }
  }
  ctx.beginPath();
  ctx.moveTo(x + radius.tl, y);
  ctx.lineTo(x + width - radius.tr, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius.tr);
  ctx.lineTo(x + width, y + height - radius.br);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius.br, y + height);
  ctx.lineTo(x + radius.bl, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius.bl);
  ctx.lineTo(x, y + radius.tl);
  ctx.quadraticCurveTo(x, y, x + radius.tl, y);
  ctx.closePath();
  if (fill) {
    ctx.fill();
  }
  if (stroke) {
    ctx.stroke();
  }
}

function TextDrawer(ctx, fnt, fntsub, color, br) {
  // default argument
  color = color !== undefined ? color : "#000";
  br = br !== undefined ? br : false;   // line-break for subtitle

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
    var iSubtitle_x = 0;
    var iMainWidth = 0;
    var iSubWidth = 0;
    var iTotalWidth = 0;
    self.ctx.font = self.fnt;
    iMainWidth = (iSubtitle_x = self.ctx.measureText(title).width);
    self.ctx.font = self.fntsub;
    iSubWidth = self.ctx.measureText(subtitle).width;
    iTotalWidth = iMainWidth + iSubWidth;

    if (!br) {
      self.drawText_nobr(title,subtitle,x,y,w,h,iTotalWidth,iSubtitle_x);
    } else {
      self.drawText_br(title,subtitle,x,y,w,h,iMainWidth,iSubWidth);
    }
  }

  this.drawText_nobr = function(title,subtitle,x,y,w,h,textWidth,subtitle_x) {
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

  this.drawText_br = function(title,subtitle,x,y,w,h,iMainWidth,iSubWidth) {
    // title draw
    var ratio = 1;
    if (iMainWidth > w) {
      ratio = w / iMainWidth;
    }
    self.ctx.textAlign="left";
    self.ctx.setTransform(ratio,0,0,1,x+10,y);
    self.ctx.fillStyle = this.color;
    self.ctx.font = self.fnt;
    self.ctx.fillText(title, 0, 0);

    // subtitle draw
    ratio = 1;
    if (iSubWidth > w) {
      ratio = w / iSubWidth;
    }
    self.ctx.setTransform(ratio,0,0,1,x+10,y+10);
    self.ctx.font = self.fntsub;
    self.ctx.fillText(subtitle, 0, 0);

    // reset
    self.ctx.setTransform(1,0,0,1,0,0);
  };
}
