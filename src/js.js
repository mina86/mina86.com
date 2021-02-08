(img => {
	var D = document,
	    W = window,
	    tmp = id => D.getElementById(id),
	    createElement = tag => D.createElement(tag),
	    appendHeadChild = el => D.head.appendChild(el),
	    getRect = el => el.getBoundingClientRect(),
	    sidebar = tmp('s'),
	    header = tmp('h'),
	    footer = tmp('f');

	/* Third party scripts */
	W['_gaq'] = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	W['talkyardServerUrl'] = 'https://comments-for-mina86-com.talkyard.net';
	[
		'cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js',
		'www.google-analytics.com/ga.js',
		'c1.ty-cdn.net/-/talkyard-comments.min.js'
	].map(src => {
		tmp = createElement('script');
		tmp.src = 'https://' + src;
		appendHeadChild(tmp);
	});

	/* Apple touch icon */
	[192, 180, 152, 120, 76].map(w => {
		tmp = createElement('link');
		tmp.rel = 'apple-touch-icon';
		tmp.sizes = w + 'x' + w;
		tmp.href = '/d/' + w + '.png';
		appendHeadChild(tmp);
	});

	/* Sidebar pinning */
	sidebar && header && footer && (W.onscroll = W.onresize = left => {
		var sidebarRect = getRect(sidebar),
		    docEl = D.documentElement,
		    cls = sidebar.className.replace(/\s*\bv\b/, left = ''),
		    top = sidebarRect.bottom - sidebarRect.top;

		/* For sidebar to be pinned the following must hold:
		   - header must be off screen, i.e. it’s bottom must be
		     non-positive in respect to view port and
		   - sidebar’s height must be no greater than available client
		     height. */
		if (getRect(header).bottom > 0 ||
		    top > docEl.clientHeight) {
			top = left;
		} else {
			cls += ' v';
			top = getRect(footer).top - top;
			top = top < 0 ? top + 'px' : '0';
			left = (W.pageXOffset || docEl.scrollLeft || 0) -
				getRect(sidebar.parentElement).right +
				sidebarRect.right + sidebarRect.left + 'px';
		}

		sidebar.className = cls;
		sidebar.style.left = left;
		sidebar.style.top = top;
	})();

	/* WebP fallback */
	if (header) {
		img.onload = _ => {
			(!img.width || !img.height) && img.onerror();
		};
		img.onerror = _ => {
			header.style.backgroundImage = 'url(/D/Kjo1sh-Q.jpg)';
		};
		img.src = 'data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA';
	}
})(new Image);
