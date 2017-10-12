//= require jquery
//= require popper
//= require bootstrap-sprockets

// 
// Home
//




// Move the module summaries' height so they match up with the diagonal linear gradient
function setDynamicSizes () {
	// Section Buttons 
	var cw = $('.section-button').width();
	$('.section-button').css('height', cw+'px');
    // Adjust line connector
    var lineWidth = Math.floor($('.line-connector-container').width() * (0.5 - parseInt($('.line-connector#first').css('left'))/$('.line-connector-container').width()) - $('.logo-spacer > img').width()/2);
    $('.line-connector#first').css('width', lineWidth+'px');
    //Adjust info-oval sides
    var infoOvalHeight = $('.info-oval > p').height();
    $('.info-oval > div[class$="-semi-circle"]').css({'height': infoOvalHeight+'px', 'width': infoOvalHeight/2.0+'px'});
    $('.right-semi-circle').css({'border-bottom-right-radius': infoOvalHeight+'px', 'border-top-right-radius': infoOvalHeight+'px'});
    $('.left-semi-circle').css({'border-bottom-left-radius': infoOvalHeight+'px', 'border-top-left-radius': infoOvalHeight+'px'});
    // team portraits
    var teamPhotos = document.getElementsByClassName('team-photo');
    var imgWraps = document.getElementsByClassName('img_wrap');
    for (i=0; i<imgWraps.length; i++){
        imgWraps[i].style.height = teamPhotos[i].offsetHeight;
    }
	//Module Summaries
	var midWidth = document.querySelector('.modules-summary-container-outer > .logo-spacer').offsetWidth / 2.0;
	var midHeight = document.querySelector('.modules-summary-container-outer > .logo-spacer').offsetHeight / 2.0;
	var angle = -12.5 * Math.PI / 180.0;
    var buffer = 100;
    var icons = document.getElementsByClassName('summary-modules-outer');
    for (i=0; i<icons.length; i++){
        var marginTop = midHeight - (icons[i].offsetLeft - midWidth) * Math.tan(angle) + buffer;
        icons[i].style.marginTop = marginTop.toString() + 'px';
        
    }
};
window.onload = setDynamicSizes;
setTimeout(setDynamicSizes, 1000);
window.onresize = setDynamicSizes;
