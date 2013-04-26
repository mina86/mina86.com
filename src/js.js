(function(D, W) {
  W['_gaq'] = [
    ['_setAccount', 'UA-240278-1'],
    ['_trackPageview'],
    ['_setCustomVar', 1, 'user_type', W['mina86_user_type'] || 'guest']
  ];

  W['___gcfg'] = { lang: 'en-GB' };

  var TRUE = !0,
      UNDEF,

      T, xml, nodes,

      getter = function(prop) {
        return function(x) { return x[prop]; };
      },
      getParent = getter('parentNode'),
      getLength = getter('length'),
      getClientHeight = getter('clientHeight'),
      getScrollTop = getter('scrollTop'),

      setHTMLAndClass = function(element, html, cls) {
        element.innerHTML = html;
        element.className = cls;
      },

      getDocumentElement = getter('documentElement'),
      getResponseDocumentElement = function(request) {
        try { return getDocumentElement(request.responseXML); }
        catch (e) { }
      },

      byId = D.getElementById.bind(D),
      byTag = function(element, tag) {
        return element.getElementsByTagName(tag || 'div');
      },
      removeId = function(element) {
        element.id = '';
        element.removeAttribute('id');
      },
      removeElement = function(child) {
        getParent(child).removeChild(child);
      },

      createElement = D.createElement.bind(D),

      makeRequest = function(url, callback, request) {
        try {
          request = new XMLHttpRequest();
        }
        catch (e) {
          try {
            request = new ActiveXObject("Msxml2.XMLHTTP");
          }
          catch (e) {
            return TRUE;
          }
        }
        request.onreadystatechange = function() {
          T = this;
          T.readyState === 4 && T.status === 200 && callback();
        };
        request.open('GET', url, TRUE);
        request.responseType = 'document';
        request.send();
      },

      /* Load contents of article when “more” link is clicked. */
      prepareMoreLinks = function(links) {
        for (i = getLength(links); i--; ) {
          var node = links[i], url = node.href, node2;
          if (node.getAttribute('href') != '#m' &&
              url.substring(getLength(url) - 2) == '#m') {
            node2 = createElement(str_a);
            node2.href = url;
            setHTMLAndClass(node2, 'load the rest', str_load_more);
            node2.onclick = function() {
              T = this;
              i = T.href;
              node2 = createElement('span');
              return makeRequest(url = i.substring(0, getLength(i) - 2),
                                 function() {
                try {
                  for (nodes = byTag(getResponseDocumentElement(T)), i = 0;
                       (node = nodes[i++]).id != 'm';
                       /* nop */) {
                    /* nop */
                  }
                  removeId(node);
                  setHTMLAndClass(node2.previousSibling, 'Comment…');
                  url = getParent(node2);
                  removeElement(node2);
                  getParent(url).insertBefore(node, url);
                }
                catch (e) {
                  W.location = url;
                }
              }) || (
                setHTMLAndClass(node2, 'loading…', str_load_more),
                T = this,
                !getParent(T).replaceChild(node2, T)
              );
            };
            getParent(node).insertBefore(node2, node.nextSibling);
          }
        }
      },

      /* Auto download new pages when scrolling down */
      scrollerUpdate = function() {
        node = D.body;
        T = node.scrollHeight;
        i = node.offsetHeight,
        i =
          (i > T ? i : T)
          - (W.innerHeight ||
             getClientHeight(documentElement) ||
             getClientHeight(node) ||
             0)
          - (W.pageYOffset === UNDEF
             ? getScrollTop(documentElement) === UNDEF
               ? getScrollTop(node) || 0
               : getScrollTop(documentElement)
            : W.pageYOffset);

        i > 750
          ? W.setTimeout(scrollerUpdate, i > 1500 ? 1000 : 500)
          : makeRequest(scrollerLink.href, function() {
            if (xml = getResponseDocumentElement(T)) {
              for (nodes = byTag(xml), i = 0; node = nodes[i++]; ) {
                if (node.id == str_scroller_content) {
                  for (prepareMoreLinks(byTag(node, str_a));
                       (i = node.firstChild);
                       /* nop */) {
                    scrollerContent.appendChild(i);
                    try { gapi.plusone.go(i); } catch (e) {}
                  }

                  nodes = byTag(xml, str_a);
                  for (i = 0; node = nodes[i++]; ) {
                    if (node.id == str_scroller_link) {
                      scrollerLink.href = scrollerLink2.href = node.href;
                      W.setTimeout(scrollerUpdate, 500);
                      return;
                    }
                  }

                  removeElement(scrollerLink);
                  removeElement(scrollerLink2);
                  scrollerLink = UNDEF;
                }
              }
            }
          });
      },

      addScript = function(src) {
        node = createElement('script');
        node.type = 'text/javascript';
        node.async = TRUE;
        node.src = 'http' + src;
        i.appendChild(node);
      },

      str_a = 'a',
      str_scroller_content = 'sc',
      str_scroller_link = 'sl',
      str_load_more = 'l',

      documentElement = getDocumentElement(D) || {},

      commentTextarea = byId('commbody'),

      scrollerLink    = byId(str_scroller_link),
      scrollerLink2   = byId('sp'),
      scrollerContent = byId(str_scroller_content),

      node,
      i = D.head;

  /* Google Analytics */
  W['mina86_skip_ga'] || addScript(
      (getLength(W.location.protocol) == 6 ? 's://ssl' : '://www') +
      '.google-analytics.com/ga.js');

  /* Google+ */
  addScript('s://apis.google.com/js/plusone.js');

  /* AJAX */
  W.opera || (
    prepareMoreLinks(D.links),
    scrollerLink && scrollerContent && scrollerUpdate()
  );

  /* Comment's body textarea resize */
  commentTextarea && (commentTextarea.onkeydown = W.onload = function() {
    for (xml = commentTextarea.cols,
         nodes = commentTextarea.value.split('\n'),
         node = i = getLength(nodes); i--;) {
      node += Math.floor(getLength(nodes[i]) / xml);
    }
    commentTextarea.rows = ++node > 5 ? node > 60 ? 60 : node : 6;
    return TRUE;
  });
})(document, window);
