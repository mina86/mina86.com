(function(W, D) {
	const form = D.getElementById('demo');
	if (!form) {
		return;
	}

	const xyzFromRgbMatrix = [
		[0.4124108464885388,   0.3575845678529519,  0.18045380393360833],
		[0.21264934272065283,  0.7151691357059038,  0.07218152157344333],
		[0.019331758429150258, 0.11919485595098397, 0.9503900340503373]
	];
	const rgbFromXyzMatrix = [
		[ 3.240812398895283,    -1.5373084456298136,  -0.4985865229069666],
		[-0.9692430170086407,    1.8759663029085742,   0.04155503085668564],
		[ 0.055638398436112804, -0.20400746093241362,  1.0571295702861434]
	];
	function gammaExpansion(value) {
		return value <= 0.040448236277108191703776
			? value / 12.92
			: Math.pow((value + 0.055) / 1.055, 2.4);
	}
	function gammaCompression(linear) {
		return linear <= 0.0031306684425006340328
		    ? 12.92 * linear
		    : (1.055 * Math.pow(linear, 5.0 / 12.0) - 0.055);
	}
	function matrixMultiplication3x3x1(matrix, column) {
		return matrix.map(row => (
			row[0] * column[0] +
			row[1] * column[1] +
			row[2] * column[2]
		));
	}
	function xyzFromLinear(linear) {
		return allValid(linear)
			? matrixMultiplication3x3x1(xyzFromRgbMatrix, linear)
			: linear.map(v => null);
	}
	function linearFromXyz(xyz) {
		return allValid(xyz)
			? matrixMultiplication3x3x1(rgbFromXyzMatrix, xyz)
			: xyz.map(v => null);
	}


	function allValid(arr) {
		return arr[0] != null && arr[1] != null && arr[2] != null;
	}


	const nameColour = 'c';
	const names255 = ['r8', 'g8', 'b8'];
	const namesRgb = ['r', 'g', 'b'];
	const namesLinear = ['lr', 'lg', 'lb'];
	const namesXyz = ['x', 'y', 'z'];


	function parseElement(name, parser) {
		const input = form.elements[name];
		const result = parser.call(null, input.value);
		input.style.background =
			result.ok && result.value != null ? '' : '#fcc';
		return result.value;
	}

	function parseNumbers(names, opt_max) {
		return names.map(name => parseElement(name, string => {
			const value = parseFloat(string);
			return isFinite(value) ? {
				ok: opt_max == -1 || (value >= 0 && value <= (opt_max || 1.0)),
				value: value
			} : {
				value: null
			};
		}));
	}

	function parseColour() {
		const m = parseElement(nameColour, string => ({
			value: string.match(/^\s*#([0-9a-fA-F]{6})\s*$/),
			ok: true
		}));
		return [0, 2, 4].map(
			i => m ? parseInt(m[1].substr(i, 2), 16) : null);
	}


	function setElement(name, value, ok) {
		const input = form.elements[name];
		input.style.background = !ok || value == null ? '#fcc' : '';
		input.value = value == null ? '' : value;
	}

	function setNumbers(names, values, func, max) {
		if (func) {
			values = values.map(
				v => v == null ? v : func.call(null, v));
		}
		max = max | 1;
		names.forEach((name, i) => {
			const v = values[i];
			setElement(name, Math.round(v * 1000) / 1000,
				   max < 0 || (v >= 0 && v <= max));
		});
		return values;
	}

	function setColour(rgb) {
		const digits = '0123456789ABCDEF';
		let ok = true;
		const colour = allValid(rgb) ? '#' + rgb.map(v => {
			v = (v < 255 ? v <= 0 ? 0 : Math.round(v) : 255) | 0;
			ok = ok && v >= 0 && v <= 255;
			return digits.charAt(v >> 4) + digits.charAt(v & 15);
		}).join('') : null;
		setElement(nameColour, colour, ok);
	}


	function onChange(ev) {
		let el = ev.target;
		while (el && el.nodeName != 'INPUT') {
			el = el.parentNode;
		}
		if (!el) {
			return;
		}

		let rgb255, rgb, linear, xyz;
		const index = [
			[[nameColour],
			 () => (rgb255 = parseColour())],
			[names255,
			 () => (rgb255 = parseNumbers(names255, 255))],
			[namesRgb,
			 () => (rgb = parseNumbers(namesRgb))],
			[namesLinear,
			 () => (linear = parseNumbers(namesLinear))],
			[namesXyz,
			 () => (xyz = parseNumbers(namesXyz, -1))]
		].findIndex(spec => {
			if (spec[0].indexOf(el.name) == -1) {
				return false;
			}
			spec[1].call(null);
			return true;
		});
		if (index == -1) {
			return;
		}
		if (index < 1) {
			setNumbers(names255, rgb255, null, 255);
		}
		if (index < 2) {
			rgb = setNumbers(namesRgb, rgb255, v => v / 255);
		}
		if (index < 3) {
			linear = setNumbers(namesLinear, rgb, gammaExpansion);
		}
		if (index < 4) {
			setNumbers(namesXyz, xyzFromLinear(linear), null, -1);
		}
		if (index > 3) {
			linear = setNumbers(namesLinear, linearFromXyz(xyz));
		}
		if (index > 2) {
			rgb = setNumbers(namesRgb, linear, gammaCompression);
		}
		if (index > 1) {
			rgb255 = setNumbers(names255, rgb, v => v * 255, 255);
		}
		if (index > 0) {
			setColour(rgb255);
		}
		form.elements['x'].style.background =
			form.elements['y'].style.background =
			form.elements['z'].style.background =
			form.elements['r'].style.background ||
			form.elements['g'].style.background ||
			form.elements['b'].style.background;
	}

	form.style.display = '';
	form.addEventListener('change', onChange, false);
	form.addEventListener('input', onChange, false);
	form.onSubmit = () => false;
})(window, document);
