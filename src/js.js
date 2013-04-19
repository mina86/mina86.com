(function(D, W) {
  W._gaq = [
    ['_setAccount', 'UA-240278-1'],
    ['_trackPageview'],
    ['_setCustomVar', 1, 'user_type', W.mina86_user_type || 'guest']
  ];

  W.___gcfg = { lang: 'en-GB' };

  D.addEventListener('DOMContentLoaded', W.onload = function() {
    delete W.onload;

    var NULL = null,
        TRUE = !0,
        UNDEF,

        T, xml, nodes,

        byId = function(id) {
          return D.getElementById(id);
        },
        byTag = function(element, tag) {
          return element.getElementsByTagName(tag || 'div');
        },
        getParent = function(node) { return node.parentNode; },
        getLength = function(obj) { return obj.length; },
        removeId = function(element) {
          element.id = '';
          element.removeAttribute('id');
        },
        removeElement = function(child) {
          getParent(child).removeChild(child);
        },

        createElement = function(tag) {
          return D.createElement(tag);
        },

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
          request.onreadystatechange = callback;
          request.open('GET', url, TRUE);
          request.responseType = 'document';
          request.send();
        },

        getDocumentElement = function(x) { return x.documentElement; },
        getResponseDocumentElement = function(request) {
          try { return getDocumentElement(request.responseXML); }
          catch (e) { }
        },

        /* Load contents of article when “more” link is clicked. */
        prepareMoreLinks = function(links) {
          for (i = getLength(links); i--; ) {
            var node = links[i], url = node.href, node2;
            if (node.getAttribute('href') != '#m' &&
                url.substring(getLength(url) - 2) == '#m') {
              node2 = createElement(str_a);
              node2.href = url;
              node2.className = str_load_more;
              node2.innerHTML = 'load content';
              node2.onclick = function() {
                T = this;
                i = T.href;
                node2 = createElement('span');
                return makeRequest(url = i.substring(0, getLength(i) - 2),
                                   function() {
                  T = this;
                  if (T.readyState | T.status === 204) {
                    try {
                      for (nodes = byTag(getResponseDocumentElement(T)), i = 0;
                           (node = nodes[i++]).id != 'm';
                           /* nop */) {
                        /* nop */
                      }
                      removeId(node);
                      node2.previousSibling.innerHTML = 'Comment…';
                      url = getParent(node2);
                      removeElement(node2);
                      getParent(url).insertBefore(node, url);
                    }
                    catch (e) {
                      W.location = url;
                    }
                  }
                }) || (
                  (node2.className = str_load_more),
                  (node2.innerHTML = 'loading…'),
                  (T = this),
                  (getParent(T).replaceChild(node2, T)),
                  !1
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
          i = i > T ? i : T;

          if (self.innerHeight) {
            i -= self.innerHeight;
          } else if (documentElement && documentElement.clientHeight) {
            i -= documentElement.clientHeight;
          } else if (node.clientHeight) {
            i -= node.clientHeight;
          } else {
            return;
          }

          if (self.pageYOffset !== UNDEF) {
            i -= self.pageYOffset;
          } else if (documentElement && documentElement.scrollTop !== UNDEF) {
            i -= documentElement.scrollTop;
          } else if (node.scrollTop !== UNDEF) {
            i -= node.scrollTop;
          } else {
            return;
          }

          i > 750
            ? W.setTimeout(scrollerUpdate, i > 1500 ? 1000 : 500)
            : makeRequest(scrollerLink.href, function() {
              T = this;
              if (T.readyState | T.status === 204 &&
                  (xml = getResponseDocumentElement(T))) {
                for (nodes = byTag(xml), i = 0; node = nodes[i++]; ) {
                  if (node.id == str_scroller_content) {
                    prepareMoreLinks(byTag(node, str_a));

                    while ((i = node.firstChild)) {
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
                    scrollerLink = NULL;
                  }
                }
              }
            });
        },

        addScript = function(src) {
          node = createElement('script');
          node.type = 'text/javascript';
          node.async = TRUE;
          node.src = src;
          i.appendChild(node);
        },

        str_a = 'a',
        str_scroller_content = 'sc',
        str_scroller_link = 'sl',
        str_load_more = 'l',

        documentElement = getDocumentElement(D),

        commentTextarea = byId('commbody') || {},

        scrollerLink    = byId(str_scroller_link),
        scrollerLink2   = byId('sp'),
        scrollerContent = byId(str_scroller_content),

        node,
        i = D.head;

    /* Google Analytics */
    W.mina86_skip_ga || addScript('http' +
        ('https:' == document.location.protocol ? 's://ssl' : '://www') +
        '.google-analytics.com/ga.js');

    /* Google+ */
    addScript('https://apis.google.com/js/plusone.js');

    /* AJAX */
    W.opera || (
      prepareMoreLinks(D.links),
      scrollerLink && scrollerContent && scrollerUpdate()
    );

    /* Comment's body textarea resize */
    commentTextarea.onkeydown = function() {
      for (xml = commentTextarea.cols, nodes = commentTextarea.value.split('\n'), i = getLength(nodes), node = 1; i--;) {
        node += Math.floor(getLength(nodes[i]) / xml + 1);
      }

      node < 6 && (node = 6);
      commentTextarea.rows = node > 60 ? 60 : node;
      return TRUE;
    }
  }, !1); /* window.onload */
})(document, window);
