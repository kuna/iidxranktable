/*
 * by kuna (insane.pe.kr/iidx)
 * MIT License
 */

function ranklist(width, height, text, color, size) {
	// common settings
	this.maxwidth = width;
	this.height = height;
	this.text = text
	this.color = color;
	this.textsize = size;

	this.makeCanvas = function() {
		var canvas = document.createElement('canvas');
		canvas.height = this.height;
		canvas.width = this.maxwidth;
		var ctx = canvas.getContext("2d");

		// default font!
		ctx.font = this.textsize + ' "M+ 1c medium"'
		ctx.fillStyle = this.color;
		var textWidth = ctx.measureText(this.text).width;

		// set context size
		if (textWidth > this.maxwidth) {
			canvas.width = textWidth;
			ctx.font = this.textsize + ' "M+ 1c medium"'	//reset font
			canvas.setAttribute('style', "width:" + this.maxwidth + "px; height:" + this.height + "px;");
		}

		// draw
		ctx.fillText(this.text, 0, this.height - 4);

		return canvas;
	}
}