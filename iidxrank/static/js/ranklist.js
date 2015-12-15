/*
 * by kuna (insane.pe.kr/iidx)
 * MIT License
 */

function ranklist(width, height, text, color, size) {
	// common settings
	this.maxwidth = width;
	this.height = height;
	this.text = text;
	this.color = color;
	this.textsize = size;

	/* check is there any subtitle available */
	var reg = /\(.+?\).*$|-.+?-.*$|~.+?~.*$|～.+?～.*$|”.+?”.*$|feat\..+$/g;
	this.subtitle = this.text.match(reg);
	if (this.subtitle != null) {
		this.subtitle = this.subtitle.join(' ');
		this.title = this.text.replace(reg, "");
	} else {
		this.subtitle = "";
		this.title = this.text;
	}

	this.makeCanvas = function() {
		var canvas = document.createElement('canvas');
		canvas.height = this.height;
		canvas.width = this.maxwidth;
		var ctx = canvas.getContext("2d");

		// set font color/size/family of canvas
		// and measure text (after font is selected)
		var font_title = this.textsize + 'px "M+ 1c medium"';
		var font_subtitle = this.textsize/2 + 'px "M+ 1c medium"';
		var subtitle_x = 0;
		var textWidth = 0;
		ctx.font = font_title;
		textWidth += (subtitle_x = ctx.measureText(this.title).width);
		ctx.font = font_subtitle;
		textWidth += ctx.measureText(this.subtitle).width;

		// set context size
		if (textWidth > this.maxwidth) {
			canvas.width = textWidth;
			canvas.setAttribute('style', "width:" + this.maxwidth + "px; height:" + this.height + "px;");
		}


		// draw
		ctx.fillStyle = this.color;
		ctx.font = font_title;
		ctx.fillText(this.title, 0, this.height - 4);
		console.log(font_subtitle + " " + font_title);
		ctx.font = font_subtitle;
		ctx.fillText(this.subtitle, subtitle_x, this.height - 4);

		return canvas;
	}
}