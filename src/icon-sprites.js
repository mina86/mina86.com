(function(D) {
    var rects = [
        [  81, 51, 270, 85, '#FCC' ],
        [ 106, 26, 270, 85, '#FCF' ],
        [ 131,  1, 270, 85, '#CFF' ],
        [  30,  0, 156, 71, '#CFC' ]
    ],
        B = D.body,
        idx = 0,
        img = D.getElementById('iconsprites'),
        div,
        bgDiv,

        handler = function(e) {
            e = e || window.event;
            var x = e.pageX, y = e.pageY, i = D.documentElement;

            if (x || y) {
            } else if ((x = e.clientX) || (y = e.clientY)) {
                x += B.scrollLeft + i.scrollLeft;
                y += B.scrollTop + i.scrollTop;
            } else {
                B.removeEventListener('mousemove', handler, false);
                return;
            }

            for (i = img; i; i = i.offsetParent) {
                x -= i.offsetLeft;
                y -= i.offsetTop;
            }

            if (x > 0 && x < 270 && y > 0 && y < 85) {
                for (i = 0; e = rects[i++]; ) {
                    if (x > e[0] && x < e[2] && y > e[1] && y < e[3]) {
                        if (idx != i) {
                            idx = i;
                            i = bgDiv.style;
                            i.left = img.offsetLeft + e[0] + 'px';
                            i.top = img.offsetTop + e[1] + 'px'
                            i.width = e[2] - e[0] + 'px';
                            i.height = e[3] - e[1] + 'px';
                            i.background = e[4];
                            div.appendChild(bgDiv);
                        }
                        return;
                    }
                }
            }

            if (idx) {
                div.removeChild(bgDiv);
                idx = 0;
            }
        };

    if (img) {
        bgDiv = D.createElement('div');
        bgDiv.style.position = 'absolute';
        bgDiv.style.zIndex = 1;
        img.style.position = (div = img.parentNode).style.position = 'relative';
        img.style.zIndex = 2;

        B.addEventListener('mousemove', handler, false);
    }
})(document);
