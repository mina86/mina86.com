type Tripple = [number, number, number];
type Matrix = [Tripple, Tripple, Tripple];

/**
 * A conversion matrix from linear sRGB colour space with coordinates normalised
 * to [0, 1] range into an XYZ space.
 */
const xyzFromRgbMatrix: Matrix = [
	[0.4123865632529917,   0.35759149092062537, 0.18045049120356368],
	[0.21263682167732384,  0.7151829818412507,  0.07218019648142547],
	[0.019330620152483987, 0.11919716364020845, 0.9503725870054354]
];

/**
 * A conversion matrix from XYZ colour space to a linear sRGB space with
 * coordinates normalised to [0, 1] range.
 */
const rgbFromXyzMatrix: Matrix = [
	[ 3.2410032329763587,   -1.5373989694887855,  -0.4986158819963629],
	[-0.9692242522025166,    1.875929983695176,    0.041554226340084724],
	[ 0.055639419851975444, -0.20401120612390997,  1.0571489771875335]
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
