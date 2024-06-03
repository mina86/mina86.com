dataLayer = [];
function gtag(){dataLayer.push(arguments)}

(date => {
	/* Apart from those three, z is also variables available for use. */
	var a, x, el;

	var doc = document;
	var root = doc.documentElement;
	var storage = localStorage;

	var create = (tag, parent, className) => {
		tag = doc.createElement(tag);
		if (className) {
			tag.className = className;
		}
		if (parent) {
			parent.appendChild(tag);
		}
		return tag;
	};
	var createText = (text, parent) => {
		text = doc.createTextNode(text);
		if (parent) {
			parent.appendChild(text);
		}
		return text;
	};
	var query = selector => doc.querySelector(selector);
	var queryAll = selector => doc.querySelectorAll(selector);

	var header = query('#h');
	var isPL = root.lang == 'pl';

	/* Converts kind of L*uv colour into #RRGGBB string.

	   Note that u and v arguments aren’t really u and v.  Instead they are
	   expected to equal C*cos(h)/13 and C*sin(h)/13 respectively where
	   C and h come from LCh(uv) colour.  This allows optimisation where
	   when called several times in a row, the cos and sin calculations can
	   be cached.

	   Also beware that as everything else in this script, this code
	   optimises for size so some calculations are approximated.  This
	   shouldn’t be perceivable to humans though. */
	var rgbFromLuv = (l, u, v) => {
		/* See https://mina86.com/2019/srgb-xyz-matrix/ for X, Y and
		   Z values of reference point (we’re using D65). */
		/*
		var Xr = 0.9504492182750991;
		var Yr = 1;
		var Zr = 1.0889166484304715;
		var un = (4 * Xr) / (Xr + 15 * Yr + 3 * Zr);
		var vn = (9 * Yr) / (Xr + 15 * Yr + 3 * Zr);
		*/
		u = u / l + 0.198;  /* un = 0.198 */
		v = v / l + 0.468;  /* vn = 0.468 */

		/* This is Y but called x because we have that variable laying
		   around. */
		x = (l + 16) / 116;
		x = l > 8 ? x*x*x : (l / 903 /* 24389 / 27 */);

		/* X = Y * 9u / 4v
		   Z = Y * (12 - 3u - 20v) / 4v
		   c = cx * X + cy * Y + cz * Z

		   X' = 9u / v
		   Z' = (12 - 3u - 20v) / v
		   c = Y * (cx/4 * X' + cy * 1 + cz/4 * Z')

		   Z' = (12 - 3u - 20v)
		   c = Y * (9/4*cx * u + cy * v + cz/4 * Z') / v

		   c = Y * c' / v
		   c' = 9/4*cx * u + cy * v + cz/4 * (12 - 3u - 20v) =
		      = 9/4*cx    * u +
		        cy        * v +
		        3*cz          +
		        -3/4*cz/4 * u +
		        -5cz      * v =
		      = (9/4*cx - 3/4*cz/4) * u +
		        (cy - 5cz)          * v +
		        3cz

		    c = Y * (au * u + av * v + a0) / v =
		      = Y * ((au * u + a0) / v + av)
		    au = 9/4*cx - 3/4*cz = (9cx - 3cz) / 4
		    av = cy - 5cz
		    a0 = 3cz

		  See https://mina86.com/2019/srgb-xyz-matrix/ for values of
		  the XYZ→RGB coefficients.  */

		l = (au, av, a0, sh) => {
			au = x * ((au * u + a0) / v + av);
			au = au > 0.0031308 ?
				1.055 * Math.pow(au, 1 / 2.4) - 0.055 :
				(12.92 * au);
			return (au > 0 ? au < 1 ? au * 255 : 255 : 0) << sh;
		};

		return '#' + ('00000' + (
			l( 7.666 ,  0.9557, -1.496, 16) |
			l(-2.212 ,  1.668,   0.1247, 8) |
			l(-0.6677, -5.49,    3.171,  0)
		).toString(16)).substr(-6);
	};

	/* Returns an object with ‘c’ and ‘s’ properties equal to cosine and
	   sine of given angle.  Angle is given in twelves of a turn, i.e. 12
	   corresponds to 360°. */
	var cosSin = h => ((h *= .5236 /* ≈ tau / 12 */),
			   {c: Math.cos(h), s: Math.sin(h)});

	var mediaQuery = matchMedia('(prefers-color-scheme:dark)');
	/* Schema settings as saved in local storage.  For the most part this is
	   only used as a binary flag to determine whether mediaQuery changes
	   should be taken into account or ignored (if user explicitly toggled
	   colour scheme, changes to the media won’t change the palette). */
	var schemeSetting = storage.getItem('s') || '';
	var isDark = schemeSetting ?
	    !/^l/.exec(schemeSetting) : mediaQuery.matches;
	var isHighContrast = schemeSetting ? !/^.l/.exec(schemeSetting) : 0;
	var schemeHue = (h => isFinite(h) ? h : 8)(
		parseFloat(schemeSetting.substr(2)));

	/* Updates the schema by setting CSS variables on the document element.
	   Takes no arguments; ‘y’ is a fake one. */
	var updateScheme = y => {
		/* Those must match variables in css.less. */
		var clBg          = 'a:';
		var clFgLow       = 'c:';
		var clBorder      = 'e:';
		var clLink        = 'f:';
		var clVisited     = 'g:';
		var clHover       = 'h:';
		var clCode        = 'i:';
		var clAccBg       = 'j:';
		var clHdrBg       = 'k:';
		var clHdr         = 'l:';
		var clNavBg       = 'm:';
		var clNavFg       = 'n:';
		var clNavHover    = 'p:';
		var clNavHdr      = 'q:';
		var clSlide       = 'z:';

		el = v => (isDark ? 3 - v : v);

		/* We want links to be blue so depending on base hue we’re using
		   different offsets for links.  We also want code colour to be
		   distinct from link so its offset also varies.  To determine
		   each case, we divide the colour wheel into thirds.  and use
		   offset such that link colour falls in the blue third.  Blue
		   colour has hue 8. */
		if (2 < schemeHue && schemeHue <= 6) {
			x = 4;
			y = 8;
		} else if (6 < schemeHue && schemeHue <= 10) {
			x = 0;
			y = 8;
		} else {
			x = 8;
			y = 4;
		}

		/* Calculate all (well, all but two) sines and cosines we’ll
		   ever need.  The ‘z’ function looks into this object first
		   before calculating those trig functions. */
		a = {
			0: cosSin(schemeHue),
			4: cosSin(schemeHue + 4),
			8: cosSin(schemeHue + 8),
		};

		z = (shade, ch, h) => {
			h = a[h || 0] || cosSin(schemeHue + h);
			shade = [
				12, 30, 70, 88,
				05, 20, 80, 95,
			][shade + 4 * isHighContrast]
			if (shade < 10 || shade > 90) {
				ch /= 2;
			}
			return rgbFromLuv(shade, ch * h.c, ch * h.s);
		};

		storage.setItem('c', root.style = [
			'color:'   + z(el(0), 2),
			clBg       + z(el(3), 2 - isDark),
			clFgLow    + z(el(1), 2),
			clLink     + z(el(1), 4, x),
			clVisited  + z(el(1), 4, x + 1),
			clHover    + z(el(0), 4, x - 1),
			clCode     + z(el(1), isDark?2:8, y),
			clAccBg    + z(el(3), 1, y),
			clBorder   + z(el(2), 2),

			clHdrBg    + z(   0 , 2 + isDark)+'e0',
			clHdr      + z(   3 , 2),

			clNavBg    + z(   1 , 2),
			clNavFg    + z(   3 , 2, 8),
			/* clNavLink == clHdr */
			clNavHover + z(   2 , 4),
			clNavHdr   + z(   2 , 4, 4),

			clSlide    + z(   2 , 9),

			'x:' + schemeHue / 0.12 + '%',
		].join(';--'));
		root.id = isDark ? 'd' : '';
		doc.body.id = isHighContrast ? 't' : '';
	};

	/* Saves current schema into local storage.  Sets schemeSetting to the
	   wale such that changes to mediaQuery will be ignored so long as the
	   value is set. */
	var saveScheme = _ => {
		schemeSetting = (isDark ? 'd' : 'l') +
			(isHighContrast ? 'h' : 'l') + schemeHue;
		storage.setItem('s', schemeSetting);
		updateScheme();
		return false;
	};
	/* Resets the schema as if user did not specify it.  This removes the
	   setting from local storage, changes high contrast and hue to default
	   values and isDark based on mediaQuery. */
	var resetScheme = _ => {
		isDark = mediaQuery.matches;
		isHighContrast = 0;
		schemeHue = 8;
		storage.removeItem('s');
		updateScheme();
		return schemeSetting = false;
	};

	/* Constructs a drop down panel from widget in the navigation at the
	   bottom of the page.  ‘selector’ selects the UL of the widget.
	   Returns a deep clone of that element.

	   Note: this is called ‘z’ because it’s used immediately and later the
	   variable is reused as global temporary variable. */
	var z = selector => query(selector).cloneNode(1);
	/* ‘Contact’ drop down. */
	var ddContact = z('#n ul');
	/* ‘Categories’ drop down. */
	var ddCats = z('#k ul');
	/* ‘Code’ drop down.  This is going to be populated by ‘G’ function
	    once the ‘/d/g’ script is loaded. */
	var ddCode = create('ul', 0, 'g m np');
	/* ‘Settings’ drop down. */
	var ddSettings = create('ul', 0, 'c m np');
	var shade = create('div', doc.body);
	/* Currently visible drop down. */
	var visibleDropDown;
	/* If a drop down was shown as a result of mouse hover event, timestamp
	   in milliseconds when this happened.  This is used to handle taps on
	   touch devices where click happens immediately after hover and that
	   would normally result in a toggle. */
	var shownOnOver = 0;

	/* Hides specified element by first setting it’s opacity to zero and
	   then, after half a second, it’s display to ‘none’.  The intention is
	   that element’s transition property is set to ‘opacity .5s’ so that
	   the elements fades out and once that’s done the function will remove
	   it from display completely. */
	var fadeOut = el => {
		el.style.opacity = 0;
		if (el['t']) {
			clearTimeout(el['t']);
		}
		el['t'] = setTimeout(_ => ((el.style.display = 'none'),
					   el['t'] = 0), 500);
	};

	/* Positions the drop down such that it’s centred below the link
	   corresponding to it but makes sure that the drop down does not go
	   past the left or right view-port border.  Does nothing if no drop
	   down is visibleDropDown. */
	var positionDropDown = x => {
		if (!visibleDropDown) {
			return;
		}
		el = visibleDropDown['l'].getBoundingClientRect();
		a = visibleDropDown.offsetWidth;
		x = Math.min(el.x - (el.width < a) * (a - el.width) / 2,
			     root.clientWidth - a);
		visibleDropDown.style.left = x > 0 ? x + 'px' : 0;
	};

	/* Hides drop down if it’s visible.  Also hides shade. */
	var hideDropDown = _ => {
		if (visibleDropDown) {
			visibleDropDown['l'].className = '';
			visibleDropDown.style.display = 'none';
			fadeOut(shade);
			visibleDropDown = 0;
		}
	};

	/* Detects which drop down given target element corresponds to.  Finds
	   first enclosing A element and identifies the drop down based that
	   link’s href.  If drop down is identified, returns it; otherwise
	   returns zero.  Furthermore, as a side effect updates the ‘el’
	   variable to the link element. */
	var chooseDropDown = target => {
		el = target.closest('a');
		if (!el) {
			target = 0;
		} else if ('#n' == el.hash) {
			target = ddContact;
		} else if ('#k' == el.hash) {
			target = ddCats;
		} else if (/github/.exec(el.href)) {
			target = ddCode.contains(target) ? 0 : ddCode;
		} else if ('#s' == el.hash) {
			target = ddSettings;
		} else {
			target = 0;
		}
		return target;
	};

	/* If the target corresponds to a drop down (see chooseDropDown), shows
	   that drop down.  Does nothing otherwise. */
	var maybeShowDropDown = target => {
		target = chooseDropDown(target);
		if (el && showDropDown(target) && target) {
			shownOnOver = Date.now();
		}
	};

	/* Shows specified drop down.  Apart from ‘target’ argument, excepts
	   ‘el’ variable to be the link corresponding to the drop down.  Returns
	   true iff a new drop down has been shown (i.e. returns false if target
	   evaluates to false value – in which case the drop down is hidden – or
	   if it’s an already visible drop down).  */
	var showDropDown = target => {
		if (visibleDropDown == target) {
			return false;
		} else if (!target) {
			hideDropDown();
			return false;
		}
		if (visibleDropDown) {
			visibleDropDown['l'].className = '';
			visibleDropDown.style.display = 'none';
		}
		visibleDropDown = target;
		el.className = 's';
		if (!target['l']) {
			(target['l'] = el).parentNode.appendChild(target);
		}
		target.style.display = '';
		if (target == ddSettings) {
			fadeOut(shade);
		} else {
			shade['t'] = shade['t'] && clearTimeout(shade['t']);
			shade.style.display = '';
			setTimeout(_ => (shade.style.opacity = 1), 0);
		}
		positionDropDown();
		return true;
	};

	/* Moves hue slider and updates scheme hue according to the clientX
	   position of the event causing the change.  The slide argument is the
	   hue slide element.  The pos argument is an object with a clientX
	   property which is used to determine the new slider position and hue.
	   Also focuses the slider on the slide.  */
	var moveHueSlider = (slide, pos) => {
		a = slide.getBoundingClientRect();
		a = (pos.clientX - a.left) * 12 / a.width;
		saveScheme(schemeHue = a > 0 ? a < 12 ? a : 12 : 0);
		slide.firstChild.focus();
		return false;
	};

	/* Recursively decorates contents of the element by adding ABBR elements
	   around acronyms found in text elements.  Does not descends into KBD,
	   ABBR, PRE or CODE elements (and in fact a few more; see body of the
	   function) nor into elements which have NA attribute. */
	var processAbbr = parent => {
		for (var next = parent.firstChild; next;) {
			el = next;
			next = el.nextSibling;
			if (el.nodeType == 3) {
				processAbbrText(parent);
			} else if (el.nodeType == 1 &&
				   el.getAttribute('na') == null &&
				   /* kbd, abbr, pre, code; the regex also
				      matches progress, colgroup and col but
				      that’s fine since we don’t care about
				      processing those either. */
				   !/[KB]B|PR|CO/.exec(el.tagName)) {
				processAbbr(el);
			}
		}
	};

	/* Decorates contents of a text node by adding ABBR elements around
	   acronyms.  Expects ‘el’ to be the text node to operate on.  ‘parent’
	   is element containing the node. */
	var processAbbrText = parent => {
		var fragment = new DocumentFragment;
		/* We match sole ‘$’ so that once we’re done we get one final
		   empty match at the end of the string.  This way we never
		   leave the loop and it simplifies handling of text which is
		   not affected. */
		var re = /\b(GNU.Li.*?|HTML[45]|sRGB|W3C|TL;DR|U\+[A-F]{4,6}|([A-Z]{3,}[- \/]+)*[A-Z]{3,})(?=s?\b)|$/g;
		var text = el.nodeValue;
		var matched = a = 0;
		do {
			x = re.exec(text);
			z = x[0];
			if (/[i+]/.exec(z)) {
				/* GNU/Linux, GNU/Linuksa and U+#### don’t get
				   converted.  They are handled by the regular
				   expression so that ‘GNU’ in the first two and
				   ‘####’ (if it’s all digits above 9) doesn’t
				   get caught as an acronym. */
				continue;
			}
			if (z == 'sRGB') {
				/* With sRGB we want ‘RGB’ part to be treated
				   but ‘s’ to stay untouched.  Modify match as
				   if it matched one character later. */
				++x.index;
				z = z.substr(1);
			}
			if (x.index > a) {
				createText(text.substring(a, x.index), fragment);
			}
			if (z) {
				matched = a = x.index + z.length;
				create('abbr', fragment).innerText = z;
			}
		} while (z);
		matched && parent.replaceChild(fragment, el);
	};

	/* Displays citation dialogue. */
	var citationDialog = null;
	var showCitation = link => {
		if (citationDialog == null) {
			citationDialog = create('DIALOG', doc.body);
			citationDialog.onclick = ev => {
				a = citationDialog.getBoundingClientRect();
				if (ev.clientY < a.top ||
				    a.top + a.height < ev.clientY ||
				    ev.clientX < a.left ||
				    a.left + a.width < ev.clientX) {
					citationDialog.close();
				}
			};
		}
		citationDialog.innerHTML =
			`<table><thead><tr><th colspan="2">${isPL ? 'Cytuj' : 'Cite'}</th></tr></thead><tfoot><tr><td colspan="2"><form method=dialog><button>${isPL ? 'Zamknij' : 'Close'}</button></form></td></tfoot><tbody></tbody></table>`;
		createCitationTable(link, citationDialog.firstChild.lastChild);
		citationDialog.showModal();
		return false;
	};
	/* Generates rows with citations for the article.  `link` is the
	   A element inside of the H1 element holding title of the article. Rows
	   are appended to `tbody` which is assumed to be a TBODY element. */
	var createCitationTable = (link, tbody) => {
		var pubdate = link.dataset['date'];
		var pub = processDate(new Date(pubdate));
		var acc = processDate(date);
		var url = link.href;
		var title = create('SPAN');
		var mina86_com = create('I');

		var addRow = (th, ...rest) => {
			el = create('TR', tbody);
			createText(th, create('TH', el));
			el = create('TD', el);
			for (z of rest) {
				el.appendChild(typeof z == 'string' ? doc.createTextNode(z) : z.cloneNode(true));
			}
		};

		var field = (key, value) => {
			key = (key + '           ').substring(0, 12);
			return `,\n  ${key} = {${value}}`;
		};
		var bib = '@misc{Nazarewicz' + pub.fullYear +
		    String.fromCharCode(97 + pub.doy / 26 | 0, 97 + pub.doy % 26) +
		    field('title', link.dataset['title'] || link.innerText) +
		    field('author', 'Michał Nazarewicz') +
		    field('year', pub.fullYear) +
		    field('month', pubdate.substring(5, 7)) +
		    field('howpublished', `\\url{${url}}`) +
		    field('note', `Accessed: ${acc}`) +
		    field('url', url) +
		    field('urldate', acc) + '\n}';

		title.innerHTML = link.innerHTML.replace(/<\/?(code|kbd)>/g, '');
		mina86_com.innerHTML = 'mina86.com';

		addRow('BibTeX');
		createText(bib, create('PRE', el));

		addRow('ACM',
		       `Michał Nazarewicz. ${pub.fullYear}. `,
		       title,
		       `. (${pub.monthName} ${pub.fullYear}). Retrieved ${acc.monthName} ${acc.dom}, ${acc.fullYear} from ${url}`);

		addRow('IEEE',
		       'M. Nazarewicz, “', title, ',” ', mina86_com,
		       `, ${pub.ieeeDate}. [Online]. Available: ${url}. [Accessed: ${acc.ieeeDate}].`);

		addRow('ISO 690',
		       `NAZAREWICZ, Michał, ${pub.fullYear}, `, title, '. ', mina86_com,
		       ` [online]. ${pub.isoDate}. [Accessed ${acc.isoDate}]. Available from: ${url}`);
	};
	var months = 'January February March April May June July August September October November December'.split(' ');
	var shortMonths = 'Jan. Feb. Mar. Apr. May Jun. Jul. Aug. Sept. Oct. Nov. Dec.'.split(' ');
	var processDate = date => {
		x = date.getMonth(),
		a = {
			fullYear: date.getFullYear(),
			monthName: months[x],
			dom: date.getDate(),
			'toString': _ => date.toISOString().substring(0, 10),
		};
		a.doy = x * 52 + a.dom;
		a.ieeeDate = `${shortMonths[x]} ${a.dom}, ${a.fullYear}`;
		a.isoDate = `${a.dom} ${a.monthName} ${a.fullYear}`;
		return a;
	};

	/* Construct ‘Code’ drop down.  Only the link to GitHub is added; the
	   rest is populated by ‘G’ function below.  */
	ddCode.innerHTML =
		'<li><a href=//github.com/mina86>Repo' +
		(isPL ? 'zytoria' : 'sitories');

	/* Populates the ‘Code’ drop down and adds ‘Code’ panel at the bottom of
	   the page.  This is a global function which gets called from the
	   ‘/d/g’ script with an array of repositories as argument. */
	G = repos => {
		repos.map(r => {
			a = create('a', create('li', ddCode));
			a.href = '//github.com/mina86/' + r[0];
			a.innerText = r[0];
			a.title = r[1] || '';
		});
		el = ddCode.firstChild;
		el.firstChild.innerText =
			isPL ? ' zobacz wszystkie' : 'see all';
		ddCode.appendChild(el);

		a = create('section');
		a.innerHTML = '<h2>' + (isPL ? 'Kod' : 'Code') + '</h2>';
		a.appendChild(el = ddCode.cloneNode(1));

		el = query('#n');
		el.parentNode.insertBefore(a, el);
	};

	/* Construct ‘Settings’ drop down */
	ddSettings.innerHTML =
		'<li><div class="tg td" tabindex=0 title="' +
		       (isPL ? 'Przełącz tryb ciemny' : 'Toggle dark mode') +
		       '"></div>  ' +
		    '<div class="tg tc" tabindex=0 title="' +
		       (isPL ? 'Przełącz tryb wysokiego kontrastu'
		           : 'Toggle high contrast mode') +
		       '"></div>  ' +
		    '<a href=#r>Reset</a>' +
		'<li class=w style=background:linear-gradient(90deg,' +
		[...Array(12)].map((_, h) => {
			h = cosSin(h);
			return rgbFromLuv(50, 6 * h.c, 6 * h.s);
		}).join(',') + ')><div tabindex=0></div>';

	/* Add ‘Setting’ panel at the bottom of the page.  This is a clone of
	   the drop down. */
	el = query('#n');
	create('h2', el).innerText = isPL ? 'Ustawienia' : 'Settings';
	el.appendChild(el = ddSettings.cloneNode(1));
	ddSettings.style.display = 'none';

	/* Handles click event on the settings widget.  When clicking the Reset
	   link, reset the scheme; when clicking one of the toggle buttons,
	   toggle corresponding setting.  Note that clicking on the slide is
	   handled separately by mouse down and mouse move handlers. */
	el.onclick = ddSettings.onclick = ev => {
		el = ev.target;
		if (/#r/.exec(el.hash)) {
			resetScheme();
		} else if ((a = /\btd\b/.exec(el = el.className)) ||
			   /\btc\b/.exec(el)) {
			saveScheme(a ? (isDark = !isDark) :
				   (isHighContrast = !isHighContrast));
		}
		return false;
	};
	/* Handles key down in the settings widget.  Handles backspace and
	   escape resetting the scheme, arrows moving the slider and return
	   activating the switches. */
	el.onkeydown = ddSettings.onkeydown = ev => {
		x = ev.keyCode;
		if (x == 8 || x == 27 || (x == 71 && ev.ctrlKey)) {
			/* Backspace and Escape reset the scheme no matter what
			   element we’re focused on. */
			return resetScheme();
		} else if (x == 37 || x == 39) {
			/* Arrows change the hue */
			x -= 38;
			if (ev.shiftKey) x /= 3;
			if (!ev.ctrlKey) x /= 4;
			schemeHue = (schemeHue + 12 + x) % 12.0;
			return saveScheme();
		} else if (x == 13 && (el = ev.target.closest('div'))) {
			/* Enter toggles theme if slider is focused. */
			saveScheme(isDark = !isDark);
			return true;
		} else {
			return true;
		}
	};

	/* Add handlers for dragging the hue slider.  While primary mouse
	   button is pressed, moving the mouse over the slider changes its
	   position and the scheme. */
	[el, ddSettings].map(el => {
		el = el.lastChild;
		el.onmousedown = el.onmousemove =
			ev => !(ev.buttons & 1) || moveHueSlider(el, ev);
		el.ontouchstart = el.ontouchmove = el.ontouchend =
			ev => moveHueSlider(el, ev.touches[0]);
	});

	/* Set up shade which fades page when drop down is shown. */
	shade.style.display = 'none';
	shade.id = 's';

	/* Construct Settings cog link which activates the drop down. */
	(el = create('li', header.firstChild, 'c')).innerHTML =
		'<a href=#s>⚙</a>';
	el.appendChild(ddSettings);

	/* Handles moving over and out of the drop down links.  Specifically,
	   handles moving over and out of the UL that contains all those links
	   and drop downs.

	   The general structure of the UL element is:

	       <ul>… <li><a …>Link Text</a><ul>…</ul></li> …</ul>

	   Hovering (or clicking) the A element is what shows the drop down.
	   The nested UL element is the drop down to be shown.  The drop down is
	   nested this way because moving mouse within it counts as being within
	   the LI that holds the drop down link.

	   If no drop down is visible, as soon as pointer moves over one of the
	   links, the drop down is shown.  When drop down is visible mouse over
	   events are ignored.

	   While drop down is shown mouse out event checks whether relatedTarget
	   (i.e. where the pointer moved to) and if its not withing the drop
	   down decides whether to hide it.

	   Drop down is hidden if pointer moves outside of the header bar
	   (remember that the drop down counts as being part of the header) or
	   pointer moves onto another link (in which case a new drop down is
	   shown). */
	header.firstChild.onmouseover =
		ev => visibleDropDown || maybeShowDropDown(ev.target);
	header.onmouseout = ev => {
		if (!visibleDropDown) {
		} else if (!header.contains(ev = ev.relatedTarget)) {
			hideDropDown();
		} else if (!visibleDropDown.parentNode.contains(ev)) {
			maybeShowDropDown(ev);
		}
	};

	/* Handles click event on the header.  If one of the drop down links is
	   clicked, toggles visibility of that drop down.  One exception is if
	   the drop down has ‘just’ been shown as a result of a mouse move in
	   which case clicking the link will keep it shown.  This is to handle
	   touch screen devices where mouse over and click are executed
	   immediately one after the other. */
	header.onclick = ev => {
		ev = chooseDropDown(ev.target);
		if (!ev) {
			return true;
		}
		/* If the link has been clicked while the drop down is already
		   shown, hide the drop down.  (This is most useful when
		   navigating via keyboard and user presses Return for the
		   second time).

		   However, don't toggle if the drop down has just been shown as
		   a result of a mouse over.  This happens on touch devices
		   where hover and click events happen immediately after each
		   other.  250 milliseconds should be enough of a delay to cover
		   this case. */
		showDropDown((ev == visibleDropDown) && (Date.now() - shownOnOver > 250) ? 0 : ev);
		shownOnOver = 0;
		return false;
	};

	/* Initial setting of the scheme. */
	updateScheme();
	/* Listen on changes to the schema media query and update scheme if
	   necessary.  While we always listen on the changes, they only take
	   effect if user has not explicitly set the settings. */
	mediaQuery.addListener(_ => {
		if (!schemeSetting) {
			isDark = mediaQuery.matches,
			updateScheme();
		}
	});

	/* Resize header as the page is scrolled.  Since various sizes and
	   positions are relative to header’s font size (i.e. ‘em’ is used),
	   it’s enough to update that one style to get everything scaled. */
	onscroll = e => {
		e = (pageYOffset || root.scrollTop) - (root.clientTop || 0);
		e = 8.5 - e / header.offsetHeight;
		header.style.fontSize = (e > 4 ? e > 8 ? 8 : e : 4) / 8 + 'rem';
	};
	/* On resize in addition on making sure the header is correct size,
	   position the drop down (if visible) since it might have moved outside
	   of the Left or right border.  Furthermore, do that now as well to set
	   everything initially. */
	(onresize = e => (onscroll(), positionDropDown()))();


	/* Scrolls document to the element specified in the hash taking into
	   consideration height of the header. */
	(onhashchange = el => {
		if (!/^#[a-z0-9-_]+$/i.exec(el = location.hash) ||
		    !(el = query(el))) {
			return true;
		}
		scrollTo(pageXOffset,
		         el.getBoundingClientRect().top + pageYOffset -
		         header.getBoundingClientRect().bottom - 16);
		return false;
	})();


	/* Add third party scripts. */
	a = src => create('script', doc.head).src = src;

	if (query('#c')) {
		/* Don’t load comments unless there’s comment DIV. */
		talkyardServerUrl = 'https://site-hz95jhr8je.talkyard.net';
		a('//c1.ty-cdn.net/-/talkyard-comments.min.js');
	}
	a('//www.googletagmanager.com/gtag/js?id=G-2KN8BH0V6Z');
	gtag('js', date);
	gtag('consent', 'default', {
		'ad_storage': 'denied',
		'ad_user_data': 'denied',
		'ad_personalization': 'denied',
		'analytics_storage': 'denied'
	});
	gtag('config', 'G-2KN8BH0V6Z');

	/* Add prefetch and prerender links to the first article if this is an
	   index page*/
	el = queryAll('article h1 a');
	if (el.length > 1 && !query('#p .r')) {
		/* If there are multiple articles we’re on an index page (this
		   may yield false negative on last index page if there’s only
		   one entry but we don’t care about last page anyway.  And
		   then, if there’s no right-aligned link in pagination table
		   than we’re on the first index page. */
		['prefetch', 'prerender'].map(rel => {
			a = create('link', doc.head);
			a.crossOrigin = '';
			a.href = el[0].href;
			a.rel = rel;
		});
	}


	/* Handle byline.  Add (cite) button showing citation and on 1st of
	   April change the author. */
	doc.querySelectorAll('.y').forEach(byline => {
		/* Cite button. */
		el = create('SPAN', byline, 'np');
		createText(' | ', el);
		el = create('A', el);
		el.innerText = isPL ? '(cytuj)' : '(cite)';
		el.href = '#';
		el.onclick = _ => showCitation(byline.previousElementSibling.firstChild);

		/* 1st of April */
		if (date.getDate() == 1 && date.getMonth() == 3) {
			byline.innerHTML = byline
				.innerHTML
				.replace(/(Michał) .mina86. (Nazarewicz)/,
					 (isPL ? 'Hrabia' : 'Count') + ' $1 P. $2');
		}
	});


	/* Decorate the main content by adding ABBR elements for acronyms. */
	processAbbr(query('#b'));
})(new Date);
