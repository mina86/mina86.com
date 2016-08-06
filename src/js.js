(function(D, W) {
  var T, nodes,

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
            return !0;
          }
        }
        request.onreadystatechange = function() {
          T = this;
          T.readyState === 4 && T.status === 200 && callback();
        };
        request.open('GET', url, 1);
        request.responseType = 'document';
        request.send();
      },

      addScript = function(src) {
        node = createElement('script');
        node.src = 'https://' + src;
        i.appendChild(node);
      },

      str_a = 'a',
      str_load_more = 'l',

      node,
      i = D.head;

  /* Spot.IM Comments */
  W['SPOTIM'] = {
    'spotId': 'sp_yH01UA8B'
  };
  addScript('www.spot.im/launcher/bundle.js');

  /* Google Analytics */
  W['_gaq'] = [
    ['_setAccount', 'UA-240278-1'],
    ['_trackPageview'],
  ];
  addScript('www.google-analytics.com/ga.js');

  /* Social */
  W['___gcfg'] = { lang: 'en-GB' };
  addScript('apis.google.com/js/plusone.js');
  addScript('platform.twitter.com/widgets.js');

  /* Google Custom Search */
  addScript('cse.google.com/cse.js?cx=005697715059674104273:zluc68s5jow');
})(document, window);
