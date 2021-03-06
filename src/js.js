(img => {
	var D = document;
	var tmp = id => D.getElementById(id),
	    createElement = tag => D.createElement(tag),
	    appendHeadChild = el => D.head.appendChild(el),
	    getRect = el => el.getBoundingClientRect();
	var sidebar = tmp('s'), header = tmp('h'), footer = tmp('f');

	var processAbbrText = (parent, node) => {
		/* We match sole ‘$’ so that once we’re done we get one final
		   empty match at the end of the string.  This way we never
		   leave the loop and it simplifies handling of text which is
		   not affected. */
		var re = /\b(GNU.Linu(x|ksa)|HTML[45]|sRGB|W3C|TL;DR|U\+[0-9A-F]{4,6}|([A-Z]{3,}[- \/]+)*[A-Z]{3,})(?=s?\b)|$/g;
		var fragment = new DocumentFragment();
		var pos = 0;
		var match;
		var text = node.nodeValue;
		var matched = false;
		while (match = re.exec(text)) {
			tmp = match[0];
			if (/[i+]/.exec(tmp)) {
				/* GNU/Linux, GNU/Linuks and U+#### don’t get
				   converted.  They are handled by the regular
				   expression so that ‘GNU’ in the first two and
				   ‘####’ (if it’s all digits above 9) doesn’t
				   get caught as an acronym. */
				continue;
			}
			if (tmp == 'sRGB') {
				/* With sRGB we want ‘RGB’ part to be treated
				   but ‘s’ to stay untouched.  Modify match as
				   if it matched one character later. */
				++match.index;
				tmp = tmp.substr(1);
			}
			if (match.index > pos) {
				fragment.appendChild(D.createTextNode(
					text.substring(pos, match.index)));
			}
			if (tmp) {
				pos = match.index + tmp.length;
				matched = true;
				fragment.appendChild(
					match = createElement('abbr'));
				match.innerText = tmp;
			} else if (matched) {
				pos = fragment.childNodes.length;
				parent.replaceChild(fragment, node);
				return pos;
			} else {
				return 1;
			}
		}
	};
	var processAbbr = (el,i) => {
		i = 0;
		while (tmp = el.childNodes[i]) {
			if (tmp.nodeType == 3) {
				i += processAbbrText(el, tmp);
			} else {
				if (tmp.nodeType == 1 &&
				    tmp.getAttribute('na') == null &&
				    !/KBD|PRE|CODE|ABBR/.exec(tmp.tagName)) {
					processAbbr(tmp);
				}
				++i;
			}
		}
	};

	/* Third party scripts */
	_gaq = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	talkyardServerUrl = 'https://comments-for-mina86-com.talkyard.net';
	[
		'cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml',
		'www.google-analytics.com/ga',
		'c1.ty-cdn.net/-/talkyard-comments.min'
	].map(src => {
		tmp = createElement('script');
		tmp.src = '//' + src + '.js';
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
		onscroll = lft => {
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
				top = top < 0 ? top + 'px' : 0;
				lft = (pageXOffset || docEl.scrollLeft || 0) -
					getRect(sidebar.parentElement).right +
					rect.right + rect.left + 'px';
			}

			sidebar.className = cls;
			sidebar.style.left = lft;
			sidebar.style.top = top;
		};
		(onresize = rect => {
			onscroll();
			rect = getRect(header);
			tmp = 1400 * rect.height / 475;
			tmp = rect.width < tmp ? tmp + 'px' : '100%';
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

	D.querySelectorAll('main').forEach(processAbbr);
})(new Image);
