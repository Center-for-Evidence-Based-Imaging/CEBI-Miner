function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function titleModified() {
	
	await sleep(50);
	
	if (window.document.title.includes("Updating")) {
		window.document.getElementById('loading').style.display = "block"
		window.document.getElementById('loading2').style.display = "block"
	}
		
	else {
		window.document.getElementById('loading').style.display = "none"
		window.document.getElementById('loading2').style.display = "none"
	}
}

window.onload = function() {
    var titleEl = document.getElementsByTagName("title")[0];
    var docEl = document.documentElement;

    if (docEl && docEl.addEventListener) {
        docEl.addEventListener("DOMSubtreeModified", function(evt) {
            var t = evt.target;
            if (t === titleEl || (t.parentNode && t.parentNode === titleEl)) {
                titleModified();
            }
        }, false);
    } else {
        document.onpropertychange = function() {
            if (window.event.propertyName == "title") {
                titleModified();
            }
        };
    }
};