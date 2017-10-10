//= require jquery
//= require popper
//= require bootstrap-sprockets

// 
// Home
//




// Move the module summaries' height so they match up with the diagonal linear gradient
function setDynamicHeights () {
    console.log(5 + 6);
    console.log("AAAAA");
	// Section Buttons 
	var cw = $('.section-button').width();
	$('.section-button').css({'height':cw+'px'});
    //Adjust info-oval sides
    var infoOvalHeight = $('.info-oval > p').height();
    $('.info-oval > div[class$="-semi-circle"]').css({'height': infoOvalHeight+'px', 'width': infoOvalHeight/2.0+'px'});
    $('.right-semi-circle').css({'border-bottom-right-radius': infoOvalHeight+'px', 'border-top-right-radius': infoOvalHeight+'px'})
    $('.left-semi-circle').css({'border-bottom-left-radius': infoOvalHeight+'px', 'border-top-left-radius': infoOvalHeight+'px'})
	//Module Summaries
	var midWidth = document.querySelector('.summary-container#modules > .summary-col-mid').offsetWidth / 2.0;
	var midHeight = document.querySelector('.home-spacer#modules').offsetHeight / 2.0;
	var angle = 25 * Math.PI / 180.0;
    var icons = document.getElementsByClassName('summary-modules-outer');
    for (i=0; i<icons.length; i++){
        var marginTop = midHeight - (icons[i].offsetLeft - midWidth) * Math.tan(angle);
    	icons[i].style.marginTop = marginTop.toString() + 'px';
    }
};
window.onload = setDynamicHeights;
setTimeout(setDynamicHeights, 1000);
window.onresize = setDynamicHeights;
