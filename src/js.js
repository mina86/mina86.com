var _gaq = [
  ['_setAccount', 'UA-240278-1'],
  ['_trackPageview'],
  ['_setCustomVar', 1, 'user_type', window.mina86_user_type || 'guest']
];

(function(D, W) {
  W.___gcfg = {lang: 'en-GB'};

  D.addEventListener('DOMContentLoaded', W.onload = function() {
    W.onload = function(){};

    var NULL = null,
        TRUE = !0,

        T, xml, nodes,

        byId = function(id) { return D.getElementById(id); },
        getParent = function(node) { return node.parentNode; },
        getElementsByTag = function(element, tag) {
          return element.getElementsByTagName(tag)
        },
        getLength = function(obj) { return obj.length; },
        removeId = function(element) {
          element.id = '';
          element.removeAttribute('id');
        },
        removeElement = function(child) {
          getParent(child).removeChild(child);
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
              try {
                request = new ActiveXObject("Microsoft.XMLHTTP");
              }
              catch (e) {
              }
            }
          }
          if (request) {
            request.onreadystatechange = callback;
            request.open('GET', url, TRUE);
            request.responseType = 'document';
            request.send();
          }
          return request;
        },

        getDocumentElement = function(x) { return x.documentElement; },
        getResponseDocumentElement = function(request) {
          return request.responseXML ?
            getDocumentElement(request.responseXML) : null;
        },

        /* Load contents of article when “more” link is clicked. */
        prepareMoreLinks = function(links) {
          for (i = getLength(links); i--; ) {
            var node = links[i], url  = node.href, new_link;
            if (node.getAttribute('href') != '#m' &&
                url.substring(getLength(url) - 2) == '#m') {
              new_link = D.createElement(str_a);
              new_link.href = url;
              new_link.className = str_load_more;
              new_link.innerHTML = 'load content';
              new_link.onclick = function(infoNode) {
                T = this;
                infoNode = D.createElement('span');
                url = T.href.substring(0, getLength(T.href) - 2);
                if (makeRequest(url, function() {
                  T = this;
                  if (T.readyState == 4) {
                    if (T.status == 200 &&
                        (node = getResponseDocumentElement(T))) {
                      for (nodes = getElementsByTag(node, str_div), i = getLength(nodes); i--; ) {
                        node = nodes[i];
                        if (node.id == 'm') {
                          infoNode.previousSibling.innerHTML = 'Add comment';
                          url = getParent(infoNode);
                          removeElement(infoNode);
                          removeId(node);
                          getParent(url).insertBefore(node, url);
                          return;
                        }
                      }
                    }
                    W.location = url;
                  }
                })) {
                  infoNode.className = str_load_more;
                  infoNode.innerHTML = 'loading…';
                  T = this;
                  getParent(T).replaceChild(infoNode, T);
                  return !1;
                }
                return TRUE;
              };
              getParent(node).insertBefore(new_link, node.nextSibling);
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
          } else if (getDocumentElement(D) &&
                     getDocumentElement(D).clientHeight) {
            i -= getDocumentElement(D).clientHeight;
          } else if (node.clientHeight) {
            i -= node.clientHeight;
          } else {
            return;
          }

          if (self.pageYOffset != str_undefined) {
            i -= self.pageYOffset;
          } else if (getDocumentElement(D) &&
                     getDocumentElement(D).scrollTop != str_undefined) {
            i -= getDocumentElement(D).scrollTop;
          } else if (node.scrollTop != str_undefined) {
            i -= node.scrollTop;
          } else {
            return;
          }

          if (i >= 750) {
            W.setTimeout(scrollerUpdate, i > 1500 ? 1000 : 500);
          } else {
            makeRequest(scrollerLink.href, function() {
              T = this;
              if (T.readyState == 4 && T.status == 200 &&
                  (xml = getResponseDocumentElement(T))) {
                for (nodes = getElementsByTag(xml, str_div), i = getLength(nodes); i--; ){
                  node = nodes[i];
                  if (node.id == str_scroller_content) {
                    prepareMoreLinks(getElementsByTag(node, str_a));

                    while ((i = node.firstChild)) {
                      scrollerContent.appendChild(i);
                      try { gapi.plusone.go(i); } catch (e) {}
                    }

                    nodes = getElementsByTag(xml, str_a);
                    for (i = getLength(nodes); i--; ) {
                      node = nodes[i];
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
          }
        },

        addScript = function(src) {
          node = D.createElement('script');
          node.type = 'text/javascript';
          node.async = TRUE;
          node.src = src;
          i.appendChild(node);
        },

        str_a = 'a',
        str_div = 'div',
        str_undefined = 'undefined',
        str_scroller_content = 'sc',
        str_scroller_link = 'sl',
        str_load_more = 'l',

        commentTextarea = byId('commbody'),

        scrollerLink    = byId(str_scroller_link),
        scrollerLink2   = byId('sp'),
        scrollerContent = byId(str_scroller_content),

        node,
        i = D.head;

    /* Google Analytics */
    window.mina86_skip_ga || addScript('http' +
        ('https:' == document.location.protocol ? 's://ssl' : '://www') +
        '.google-analytics.com/ga.js');

    /* Google+ */
    addScript('https://apis.google.com/js/plusone.js');

    /* AJAX */
    if (!W.opera) {
      prepareMoreLinks(D.links);
      scrollerLink && scrollerContent && scrollerUpdate();
    }

    /* Comment's body textarea resize */
    if (commentTextarea) {
      commentTextarea.onkeydown = function(e) {
        for (xml = commentTextarea.cols, nodes = commentTextarea.value.split('\n'), i = getLength(nodes), node = 1; i--;) {
          node += Math.floor(getLength(nodes[i]) / xml + 1);
        }

        node < 6 && (node = 6);
        commentTextarea.rows = node > 60 ? 60 : node;
        return TRUE;
      };
    }
  }, !1); /* window.onload */
})(document, window);
