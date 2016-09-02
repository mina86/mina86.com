(function(D, W) {
	var addScript = function(src) {
		node = D.createElement('script');
		node.src = 'https://' + src;
		D.head.appendChild(node);
	},
	    node;

	/* Spot.IM Comments */
	W['SPOTIM'] = {spotId: 'sp_yH01UA8B'};
	addScript('www.spot.im/launcher/bundle.js');

	/* Google Analytics */
	W['_gaq'] = [['_setAccount', 'UA-240278-1'], ['_trackPageview']];
	addScript('www.google-analytics.com/ga.js');

	/* Social */
	W['___gcfg'] = {lang: 'en-GB'};
	addScript('apis.google.com/js/plusone.js');
	addScript('platform.twitter.com/widgets.js');

	/* Google Custom Search */
	addScript('cse.google.com/cse.js?cx=005697715059674104273:zluc68s5jow');
})(document, window);
