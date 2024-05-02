(tr => {
	if (!tr) {
		return;
	}
	const getParent = (el, tag) => {
		while (el && el.tagName !== tag) {
			el = el.parentNode;
		}
		return el;
	};
	const table = getParent(tr, 'TABLE');

	// Add toggling visibility of canons
	const tbody = table && table.getElementsByTagName('TBODY')[0];
	if (!tbody) {
		return;
	}
	const enabled = Array.prototype.map.call(tr.children, (th, idx) => {
		th.__mina86_idx = idx;
		return false;
	});
	let count = 0;
	const toggle = th => {
		const idx = th.__mina86_idx;
		if (idx !== void 0) {
			const on = (enabled[idx] = !enabled[idx]);
			count += on ? 1 : -1;
			th.style.fontStyle = on ? 'italic' : '';
		}
		return idx !== void 0;
	};
	tr.addEventListener('click', event => {
		if (!toggle(getParent(event.target, 'TH'))) {
			return;
		}
		const display = count != 0 && count != enabled.length ? row => {
			const cols = row.children;
			for (let i = 0; i < enabled.length; ++i) {
				if (enabled[i] && cols[i].innerText.trim()) {
					return '';
				}
			}
			return 'none';
		} : _ => '';
		for (let i = 0, row; (row = tbody.children[i]); ++i) {
			row.style.display = display(row);
		}
	});
	tr.style.cursor = 'pointer';

	/* Replace titles and links based on user’s preferred language. */
	let wantPolish = false;
	let wantGwentleman = false;
	for (let lang of (navigator.languages || [])) {
		lang = lang.substring(0, 2);
		if (lang == 'pl') {
			wantPolish = wantGwentleman = true;
			break;
		} else if (lang == 'en') {
			break;
		}
		useGwentleman = useGwentleman || /fr|de|es|it|pt/.test(lang);
	}
	if (wantPolish) {
		const re = /^pl\. ‘(.*)’/;
		for (const span of table.parentNode.getElementsByTagName('SPAN')) {
			const m = re.exec(span.title || '');
			if (m) {
				span.title = '‘' + span.innerText + '’';
				span.innerText = m[1];
				span.style.fontStyle = 'italic';
				span.lang = 'pl';
			}
		}
	}
	if (wantGwentleman) {
		/* https://forums.cdprojektred.com/index.php?threads/tales-from-the-path-the-stories-of-gwents-journeys.11038958/
		   → https://trendygwentleman.com/journey/stories
		     Except for the Yennefer and Triss stories which are just
		     slide shows and aren’t translated on the Trendy Gwentleman
		     website.

		 * https://www.playgwent.com/en/news/39646/aretuza-journey-story
		   → https://trendygwentleman.com/journey/stories

		 * https://forums.cdprojektred.com/index.php?threads/novigrad-confidential-the-journal-of-walter-veritas.11008597/
		   → https://wiedzmin.fandom.com/wiki/Walter_Veritas?file=Walter_dziennik_1.jpg */
		for (const lnk of table.getElementsByTagName('A')) {
			if (lnk.search.endsWith('.11038958/')) {
				if (lnk.hash != '#post-12945487' && lnk.hash != '#post-13071184') {
					lnk.href = 'https://trendygwentleman.com/journey/stories';
				}
			} else if (lnk.pathname.startsWith('/en/news/39646/')) {
				lnk.href = 'https://trendygwentleman.com/journey/stories';
			} else if (wantPolish && lnk.search.endsWith('.11008597/')) {
				lnk.href = 'https://wiedzmin.fandom.com/wiki/Walter_Veritas?file=Walter_dziennik_1.jpg';
			}
		}
	}

	// Wrap all emojis in a SPAN with font-family set to try and make
	// Chromium display them properly.
	for (let queue = [table.parentNode], node, m, el;
	     (el = queue.pop());
	    ) {
		for (node = el.firstChild; node; node = node.nextSibling) {
			if (node.nodeType == 1) {
				queue.push(node);
			} else if (node.nodeType == 3 &&
				   ((m = /[\u{1F3A5}-\u{1F58C}]/u.exec(node.wholeText)))) {
				if (m.index) {
					node = node.splitText(m.index);
				}
				if (node.wholeText.length > (m = m[0].length)) {
					node.splitText(m);
				}
				m = document.createElement('SPAN');
				m.className = 'em';
				node.parentNode.replaceChild(m, node);
				m.appendChild(node);
				node = m;
			}
		}
	}
})(document.getElementById('canons'));
