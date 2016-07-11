// http://www.jqueryscript.net/animation/Animated-Bubbles-Background-with-jQuery-Canvas.html
//
//

var pxs = [];

function draw_init(count, con, width, height) {
	for(var i = 0; i < count; i++) {
		pxs[i] = new Circle(con, width, height);
		pxs[i].reset();
	}
}

function draw_circle() {
	con = pxs[0].con;
	con.clearRect(0,0,con.width, con.height);
	for(var i = 0; i < pxs.length; i++) {
		pxs[i].fade();
		pxs[i].move();
		pxs[i].draw();
	}
}

function Circle(con, WIDTH, HEIGHT) {
	this.con = con;
	this.s = {ttl:8000, xmax:3, ymax:2, rmax:200, rt:1, xdef:960, ydef:540, xdrift:2, ydrift: 2, random:true, blink:true};

	// fill vars
	var crFill = [
					['rgba(110,156,167,0)', 'rgba(110,156,167,1)'],
					['rgba(111,167,199,0)', 'rgba(111,167,199,1)'],
					['rgba(108,146,149,0)', 'rgba(108,146,149,1)'],
					['rgba(107,164,160,0)', 'rgba(107,164,160,1)']
				];

	// opacity var
	var opacityFill = "." + Math.floor(Math.random() * 5) + 1;

	this.reset = function() {
		this.x = (this.s.random ? WIDTH*Math.random() : this.s.xdef);
		this.y = (this.s.random ? HEIGHT*Math.random() : this.s.ydef);
		this.r = ((this.s.rmax-1)*Math.random()) + 1;
		this.dx = (Math.random()*this.s.xmax) * (Math.random() < 0.5 ? -1 : 1);
		this.dy = (Math.random()*this.s.ymax) * (Math.random() < 0.5 ? -1 : 1);
		this.hl = (this.s.ttl/60)*(this.r/this.s.rmax);	// edit 60 to change speed
		this.rt = Math.random()*this.hl;
		this.s.rt = Math.random()+1;
		this.stop = Math.random()*0.2+0.4;
		this.s.xdrift *= Math.random() * (Math.random() < 0.5 ? -1 : 1);
		this.s.ydrift *= Math.random() * (Math.random() < 0.5 ? -1 : 1);
		this.opacityFill = opacityFill;

		this.currentColor = Math.floor(Math.random()*crFill.length);
	};

	this.fade = function() {
		this.rt += this.s.rt;
	};

	this.draw = function() {
		if(this.s.blink && (this.rt <= 0 || this.rt >= this.hl)){
			this.s.rt = this.s.rt*-1;
		}
		else if(this.rt >= this.hl){
			this.reset();
		}
		con.beginPath();
		con.arc(this.x,this.y,this.r,0,Math.PI*2,true);
		con.globalAlpha = opacityFill;
		var newo = 1-(this.rt/this.hl);
		var cr = this.r*newo;
    
		gradient = con.createRadialGradient(this.x,this.y,0,this.x,this.y,(cr <= 0 ? 1 : cr));
		gradient.addColorStop(0.0, crFill[(this.currentColor)][1]);
		gradient.addColorStop(0.7, crFill[(this.currentColor)][1]);
		gradient.addColorStop(1.0, crFill[(this.currentColor)][0]);

		con.fillStyle = gradient;
		con.fill();

		con.closePath();
	};

	this.move = function() {
		this.x += (this.rt/this.hl)*this.dx;
		this.y += (this.rt/this.hl)*this.dy;
		if(this.x > WIDTH || this.x < 0){
			this.dx *= -1;
		} 
		if(this.y > HEIGHT || this.y < 0){
			this.dy *= -1;
		} 
	};

	this.getX = function() { return this.x; };
	this.getY = function() { return this.y; };
}
