(function(D, W) {
	/* Third party scripts */
	var a = function(src) {
		b = D.createElement('script');
		b.src = 'https://' + src;
		(D.head || D.body).appendChild(b);
	},
	    b = D.getElementById,
	    docEl = D.documentElement,
	    sidebar = b.call(D, 's'),
	    header = b.call(D, 'h'),
	    footer = b.call(D, 'f');

	W['SPOTIM'] = {spotId: 'sp_yH01UA8B'};
	a('www.spot.im/launcher/bundle.js');

	W['_gaq'] = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	a('www.google-analytics.com/ga.js');

	a('platform.twitter.com/widgets.js');

	a('cse.google.com/cse.js?cx=005697715059674104273:zluc68s5jow');

	/* Sidebar pinning */
	sidebar && header && footer && (W.onscroll = W.onresize = function() {
		a = a && (W.setTimeout(function() {
			a = sidebar.getBoundingClientRect;
			var r = a.call(sidebar),
			    cls = sidebar.className.replace(/\s*\bv\b/, b = ''),
			    top = r.bottom - r.top;

			/* For sidebar to be pinned the following must hold:
			   - header must be off screen, i.e. it’s bottom must be
			     non-positive in respect to view port and
			   - sidebar’s height must be no greater than available
			     client height. */
			if (a.call(header).bottom > 0 ||
			    top > docEl.clientHeight) {
				top = b;
			} else {
				cls += ' v';
				top = a.call(footer).top - top;
				top = top < 0 ? top + 'px' : '0';
				b = (W.pageXOffset || docEl.scrollLeft || 0) -
					a.call(sidebar.parentElement).right +
					r.right + r.left + 'px';
			}

			sidebar.className = cls;
			sidebar.style.left = b;
			sidebar.style.top = top;
		}, 0), 0);
	})();
})(document, window);
