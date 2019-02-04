(function(D, W) {
	var tmp = D.getElementById,
	    docEl = D.documentElement,
	    sidebar = tmp.call(D, 's'),
	    header = tmp.call(D, 'h'),
	    footer = tmp.call(D, 'f');

	/* Third party scripts */
	W['_gaq'] = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	[
		'cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_CHTML',
		'platform.twitter.com/widgets.js',
		'launcher.spot.im/spot/sp_yH01UA8B',
		'www.google-analytics.com/ga.js',
		'cse.google.com/cse.js?cx=005697715059674104273:zluc68s5jow'
	].map(function(src) {
		tmp = D.createElement('script');
		tmp.src = 'https://' + src;
		(D.head || D.body).appendChild(tmp);
	});

	/* Sidebar pinning */
	sidebar && header && footer && (W.onscroll = W.onresize = function() {
		var getRect = sidebar.getBoundingClientRect,
		    sidebarRect = getRect.call(sidebar),
		    cls = sidebar.className.replace(/\s*\bv\b/, tmp = ''),
		    top = sidebarRect.bottom - sidebarRect.top;

		/* For sidebar to be pinned the following must hold:
		   - header must be off screen, i.e. it’s bottom must be
		     non-positive in respect to view port and
		   - sidebar’s height must be no greater than available client
		     height. */
		if (getRect.call(header).bottom > 0 ||
		    top > docEl.clientHeight) {
			top = tmp;
		} else {
			cls += ' v';
			top = getRect.call(footer).top - top;
			top = top < 0 ? top + 'px' : '0';
			tmp = (W.pageXOffset || docEl.scrollLeft || 0) -
				getRect.call(sidebar.parentElement).right +
				sidebarRect.right + sidebarRect.left + 'px';
		}

		sidebar.className = cls;
		sidebar.style.left = tmp;
		sidebar.style.top = top;
	})();
})(document, window);
