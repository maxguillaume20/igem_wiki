//= require jquery
//= require popper
//= require bootstrap-sprockets

// 
// Home
//

//Change image source
$(function() {
        $(".section-button#Project").hover(
            function() {
                $(this).children("img:first").attr("src", "http://2017.igem.org/wiki/images/5/52/Project_logo_1.gif");
            },
            function() {
                $(this).children("img:first").attr("src", "http://2017.igem.org/wiki/images/a/a6/Project_logo_1.png");
            }                         
        );                  
    });

$(function() {
        $(".section-button#Practices").hover(
            function() {
                $(this).children("img:first").attr("src", "http://2017.igem.org/wiki/images/0/08/Practice_logo.gif");
            },
            function() {
                $(this).children("img:first").attr("src", "http://2017.igem.org/wiki/images/8/83/Practice_logo.png");
            }                         
        );                  
    });

// Move the module summaries' height so they match up with the diagonal linear gradient
function setDynamicHeights () {
	// Section Buttons 
	var cw = $('.section-button').width();
	$('.section-button').css({'height':cw+'px'});
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
