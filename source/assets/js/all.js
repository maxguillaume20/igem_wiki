//= require jquery
//= require popper
//= require bootstrap-sprockets

//
// Home
//

function displayCollapsible(clicked_id) {

            var inner = document.querySelector("#"+clicked_id+".module-collapsible-container-inner");
            var text = document.querySelector("#"+clicked_id+".module-collapsible-container-outer > .in-text-link")
            if (inner.style.display === "none") {
                inner.style.display = "flex";
                console.log(text.innerHTML);
                text.innerHTML = text.innerHTML.replace(/▶/g, "▼");

            } else {
                inner.style.display = "none";
                text.innerHTML = text.innerHTML.replace(/▼/g, "▶");

            }

        }


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
    var teamPhotoAspectRatio = 1.23;
    var teamImageWrapWidth = $('.team-image-wrap').width();
    var teamImageWrapHeight = teamImageWrapWidth * teamPhotoAspectRatio;
    $('.team-image-wrap').css('height', teamImageWrapHeight+'px');
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

$(document).ready(function() {
    if (window.location.hash !== "") {
        var eid = $(window.location.hash).parents(".module-collapsible-container-outer")[0].id;
        if (typeof eid !== 'undefined' ) {
	        displayCollapsible(eid)
        }
    }
});
