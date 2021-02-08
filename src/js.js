(img => {
	var D = document,
	    W = window,
	    tmp = id => D.getElementById(id),
	    createElement = tag => D.createElement(tag),
	    appendHeadChild = el => D.head.appendChild(el),
	    getRect = el => el.getBoundingClientRect(),
	    sidebar = tmp('s'),
	    header = tmp('h'),
	    footer = tmp('f'),
	    strPx = 'px';

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

	/* Sidebar pinning and top bar background fixing */
	if (sidebar && header && footer) {
		W.onscroll = lft => {
			var rect = getRect(sidebar),
			    docEl = D.documentElement,
			    cls = sidebar.className.replace(
				    /\s*\bv\b/, lft = ''),
			    top = rect.bottom - rect.top;

			/* For sidebar to be pinned the following must hold:
			   - header must be off screen, i.e. it’s bottom must be
			     non-positive in respect to view port and
			   - sidebar’s height must be no greater than available
			     client height. */
			if (getRect(header).bottom > 0 ||
			    top > docEl.clientHeight) {
				top = lft;
			} else {
				cls += ' v';
				top = getRect(footer).top - top;
				top = top < 0 ? top + strPx : 0;
				lft = (W.pageXOffset || docEl.scrollLeft || 0) -
					getRect(sidebar.parentElement).right +
					rect.right + rect.left + strPx;
			}

			sidebar.className = cls;
			sidebar.style.left = lft;
			sidebar.style.top = top;
		};
		(W.onresize = rect => {
			W.onscroll();
			rect = getRect(header);
			tmp = 1400 * rect.height / 475
			tmp = rect.width < tmp ? tmp + strPx : '100%';
			header.style.backgroundSize = tmp + ' auto';
			header.style.backgroundAttachment = 'fixed';
			header.style.positionX = 'center';
		})();
	}

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
