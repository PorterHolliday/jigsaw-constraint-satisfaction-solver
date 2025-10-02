class PuzzleLayout {
	constructor(width, height) {
		this.width = width;
		this.height = height;
		this.pieces = [];
		for (let x = 0; x < width; x++) {
			this.pieces.push([]);
			for (let y = 0; y < height; y++) {
				this.pieces[x].push(null);
			}
		}
		this.innerPieceX = 1;
		this.innerPieceY = 1;
	}
	getPieceCoordinates(piece) {
		let tempX;
		let tempY;
		for (tempX = 0; tempX < this.width; tempX++) {
			if (this.pieces[tempX].indexOf(piece) > -1) {
				tempY = this.pieces[tempX].indexOf(piece);
				break;
			}
		}
		if (!tempY) return null;
		return { x: tempX, y: tempY };
	}
	getPieceOn(direction, piece) {
		if (piece.x == -1 || piece.y == -1) return null;
		if (direction == TOP) {
			if (piece.y <= 1) return null;
			return this.pieces[piece.x][piece.y - 1];
		}
		if (direction == BOTTOM) {
			if (piece.y >= this.height - 2) return null;
			return this.pieces[piece.x][piece.y + 1];
		}
		if (direction == LEFT) {
			if (piece.x <= 1) return null;
			return this.pieces[piece.x - 1][piece.y];
		}
		if (direction == RIGHT) {
			if (piece.x >= this.width - 2) return null;
			return this.pieces[piece.x + 1][piece.y];
		}
		return null;
	}
	fitsWithPieceOn(direction, piece) {
		let otherPiece = this.getPieceOn(direction, piece);
		if (!otherPiece) return true;
		otherPiece.goToSide2();
		return piece.edges[direction].fitsWith(otherPiece.edges[getOpposite(direction)]);
	}
	addInnerPiece(piece) {
		piece.x2 = this.innerPieceX;
		piece.y2 = this.innerPieceY;
		this.pieces[this.innerPieceX][this.innerPieceY] = piece;
		//if (this.innerPieceX == this.width - 2 && this.innerPieceY == this.height - 2) return;

		this.innerPieceX++;
		if (this.innerPieceX == this.width - 1) {
			this.innerPieceX = 1;
			this.innerPieceY++;
		}
	}
	removeInnerPiece() {
		if (this.innerPieceX == 1 && this.innerPieceY == 1) return;
		this.innerPieceX--;
		if (this.innerPieceX == 0) {
			this.innerPieceX = this.width - 2;
			this.innerPieceY--;
		}

		let piece = this.pieces[this.innerPieceX][this.innerPieceY];
		piece.x2 = -1;
		piece.y2 = -1;
		this.pieces[this.innerPieceX][this.innerPieceY] = null;
	}
	isOnOuterEdge(piece, direction) {
		let coordinates = this.getPieceCoordinates(piece);
		if (!coordinates) return null;
		if (direction == TOP && coordinates.y == 1) return true;
		if (direction == BOTTOM && coordinates.y == this.height - 2) return true;
		if (direction == LEFT && coordinates.x == 1) return true;
		if (direction == RIGHT && coordinates.x == this.width - 2) return true;
		return false;
	}
}