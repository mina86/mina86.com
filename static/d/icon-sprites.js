(function() {
    var rects = [
        [  82, 52, 999, 999, '#FCC' ],
        [ 107, 27, 999, 999, '#FCF' ],
        [ 132,  2, 999, 999, '#CFF' ],
        [  31,  1, 156,  71, '#CFC' ]
    ],
        idx = -1,

        D = document,
        B = D.body,

        img = D.getElementById ? D.getElementById('iconsprites') : null,
        bgDiv,
        div,

        px = function(n) {
            return '' + n + 'px';
        },

        handler = function(e) {
            e = e || window.event;
            var x = 0, y = 0,
                el = img,
                width = el.offsetWidth, height = el.offsetHeight,
                i = 0, r;

            if (e.pageX || e.pageY) {
                x = e.pageX;
                y = e.pageY;
            } else if (e.clientX || e.clientY) {
                x = e.clientX + B.scrollLeft + D.documentElement.scrollLeft;
                y = e.clientY + B.scrollTop + D.documentElement.scrollTop;
            } else {
                B.removeEventListener('mousemove', handler, false);
                return;
            }

            do {
                x -= el.offsetLeft;
                y -= el.offsetTop;
            } while ((el = el.offsetParent));

            if (x >= 0 && x <= width && y >= 0 && y <= height) {
                while ((r = rects[i++])) {
                    if (x >= r[0] && x <= r[2] && y >= r[1] && y <= r[3]) {
                        if (idx !== i) {
                            bgDiv.style.left = px(r[0]);
                            bgDiv.style.top = px(r[1])
                            bgDiv.style.width =
                                px(Math.min(width, r[2]) - r[0]);
                            bgDiv.style.height =
                                px(Math.min(height, r[3]) - r[1]);
                            bgDiv.style.background = r[4];
                            if (idx === -1) {
                                div.appendChild(bgDiv);
                            }
                            idx = i;
                        }
                        return;
                    }
                }
            }

            if (idx !== -1) {
                bgDiv.parentNode.removeChild(bgDiv);
                idx = -1;
            }
        };

    if (img) {
        div = img.parentNode;
        div.style.position = 'relative';
        img.style.position = 'relative';
        img.style.zIndex = '2';
        bgDiv = D.createElement('div');
        bgDiv = D.createElement('div');
        bgDiv.style.position = 'absolute';
        bgDiv.style.zIndex = '1';

        B.addEventListener('mousemove', handler, false);
    }
})();
