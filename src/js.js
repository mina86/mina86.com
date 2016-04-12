(function(D, W) {
  W['_gaq'] = [
    ['_setAccount', 'UA-240278-1'],
    ['_trackPageview'],
  ];

  W['___gcfg'] = { lang: 'en-GB' };

  var TRUE = !0,

      T, xml, nodes,

      getter = function(prop) {
        return function(x) { return x[prop]; };
      },
      getParent = getter('parentNode'),
      getLength = getter('length'),

      setHTMLAndClass = function(element, html, cls) {
        element.innerHTML = html;
        element.className = cls;
      },

      getDocumentElement = getter('documentElement'),
      getResponseDocumentElement = function(request) {
        try { return getDocumentElement(request.responseXML); }
        catch (e) { }
      },

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

      addScript = function(src) {
        node = createElement('script');
        node.async = TRUE;
        node.src = 'https://' + src;
        i.appendChild(node);
      },

      str_a = 'a',
      str_load_more = 'l',

      node,
      i = D.head;

  /* Google Analytics */
  addScript('www.google-analytics.com/ga.js');

  /* Social */
  addScript('apis.google.com/js/plusone.js');
  addScript('platform.twitter.com/widgets.js');

  /* AJAX */
  W.opera || prepareMoreLinks(D.links);
})(document, window);
