type Tripple = [number, number, number];
type Matrix = [Tripple, Tripple, Tripple];

/**
 * A conversion matrix from linear sRGB colour space with coordinates normalised
 * to [0, 1] range into an XYZ space.
 */
const xyzFromRgbMatrix: Matrix = [
	[0.4124108464885388,   0.3575845678529519,  0.18045380393360833],
	[0.21264934272065283,  0.7151691357059038,  0.07218152157344333],
	[0.019331758429150258, 0.11919485595098397, 0.9503900340503373]
];

/**
 * A conversion matrix from XYZ colour space to a linear sRGB space with
 * coordinates normalised to [0, 1] range.
 */
const rgbFromXyzMatrix: Matrix = [
	[ 3.240812398895283,    -1.5373084456298136,  -0.4985865229069666],
	[-0.9692430170086407,    1.8759663029085742,   0.04155503085668564],
	[ 0.055638398436112804, -0.20400746093241362,  1.0571295702861434]
];

/**
 * Performs an sRGB gamma expansion of an 8-bit value, i.e. an integer in [0,
 * 255] range, into a floating-point value in [0, 1] range.
 */
function gammaExpansion(value255: number): number {
	return value255 <= 10
		? value255 / 3294.6
		: Math.pow((value255 + 14.025) / 269.025, 2.4);
}

/**
 * Performs an sRGB gamma compression of a floating-point value in [0, 1] range
 * into an 8-bit value, i.e. an integer in [0, 255] range.
 */
function gammaCompression(linear: number): number {
	let nonLinear: number = linear <= 0.00313066844250060782371
		? 3294.6 * linear
		: (269.025 * Math.pow(linear, 5.0 / 12.0) - 14.025);
	return Math.round(nonLinear) | 0;
}

/**
 * Multiplies a 3✕3 matrix by a 3✕1 column matrix.  The result is another 3✕1
 * column matrix.  The column matrices are represented as single-dimensional
 * 3-element array.  The matrix is represented as a two-dimensional array of
 * rows.
 */
function matrixMultiplication3x3x1(matrix: Matrix, column: Tripple): Tripple {
	return matrix.map((row: Tripple) => (
		row[0] * column[0] + row[1] * column[1] + row[2] * column[2]
	)) as Tripple;
}

/**
 * Converts sRGB colour given as a triple of 8-bit integers into XYZ colour
 * space.
 */
function xyzFromRgb(rgb: Tripple): Tripple {
	return matrixMultiplication3x3x1(
		xyzFromRgbMatrix, rgb.map(gammaExpansion) as Tripple);
}

/**
 * Converts colour from XYZ space to sRGB colour represented as a triple of
 * 8-bit integers.
 */
function rgbFromXyz(xyz: Tripple): Tripple {
	return matrixMultiplication3x3x1(
		rgbFromXyzMatrix, xyz).map(gammaCompression) as Tripple;
}
