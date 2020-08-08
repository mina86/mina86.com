(function(D, W) {
	var tmp = D.getElementById,
	    docEl = D.documentElement,
	    sidebar = tmp.call(D, 's'),
	    header = tmp.call(D, 'h'),
	    footer = tmp.call(D, 'f');

	/* Third party scripts */
	W['_gaq'] = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	[
		'cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js',
		'www.google-analytics.com/ga.js',
	].map(function(src) {
		tmp = D.createElement('script');
		tmp.async = true;
		tmp.src = 'https://' + src;
		D.head.appendChild(tmp);
	});

	/* Apple touch icon */
	[192, 180, 152, 120, 76].map(function(w) {
		tmp = D.createElement('link');
		tmp.rel = 'apple-touch-icon';
		tmp.sizes = w + 'x' + w;
		tmp.href = '/d/' + w + '.png';
		D.head.appendChild(tmp);
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

	/* WebP fallback */
	if (header) {
		tmp = new Image();
		tmp.onload = function() {
			(!this.width || !this.height) && this.onerror();
		};
		tmp.onerror = function() {
			header.style.backgroundImage = 'url(/D/Kjo1sh-Q.jpg)';
		};
		tmp.src = 'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA';
	}
})(document, window);
