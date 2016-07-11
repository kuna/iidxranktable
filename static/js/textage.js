/*
 * script from textage.cc
 * all rights reserved
 */

//
// first few lines
//
referstr="";referorg="";fav1="";str36="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";m=[];lc=[];
lcbase=location.search;
if(!lcbase || lcbase.length<8)lcbase="?vM11B00";
for (i=0;i<=7;i++) {
	lc[i]=lcbase.charAt(i);
	if (i>=2) lc[i]= parseInt(lc[i],36);
}
if (lc[1]=="r") {
	rpos = lcbase.indexOf("_");
	if (rpos>=0) {
		referorg = lcbase.substring(rpos+1);
		for (ri=0; ri<referorg.length; ri+=4) {
			refcrd = parseInt(referorg.substring(ri,ri+4), 16);
			referstr += String.fromCharCode(refcrd);
		}
	}
}

function getTextageLink(songtitle) {
	nowval = songtitle;
	cbox = 2;	// gen 0x100, tit 0x010, ref 0x001

	//
	// script start
	// 
	ret = "";
	lc[1] = "r";
	lc[2] = cbox;
	for(ii=0; ii<=7; ii++) {
		ret+= (ii>=2 ? str36.charAt(lc[ii]) : lc[ii]);
	}

	refcrdstr = "_";
	for (ri=0; ri<nowval.length; ri++) {
		refcrd = (nowval.charCodeAt(ri)).toString(16);
		while (refcrd.length<4) refcrd = "0"+refcrd;
		refcrdstr += refcrd;
	}

	// 
	// script end
	//

	return "http://textage.cc/score/index.html" + ret+refcrdstr;
}
