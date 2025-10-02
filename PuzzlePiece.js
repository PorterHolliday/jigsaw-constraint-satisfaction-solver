let TOP = 0;
let RIGHT = 1;
let BOTTOM = 2;
let LEFT = 3;
function getOpposite(direction) {
	return (direction + 2) % 4;
}
class PuzzlePiece {
	constructor(id, x1, y1) {
		this.id = id;
		this.x = x1;
		this.y = y1;
		this.x1 = x1;
		this.y1 = y1;
		this.x2 = -1;
		this.y2 = -1;
		this.edges = [new PieceEdge(), new PieceEdge(), new PieceEdge(), new PieceEdge()];
		this.side2Index = 0;
		this.side = 1;
	}
	goToSide1() {
		if (this.side == 1) return;
		this.side = 1;
		this.x = this.x1;
		this.y = this.y1;
		//if (this.side2Index > 0)
		//alert('goToSide1() Side2Index: ' + this.side2Index + ' Piece: ' + this);
		this.edges = this.edges.slice(4 - this.side2Index).concat(this.edges.slice(0, 4 - this.side2Index));
		//if (this.side2Index > 0)
		//alert('After: ' + this);
	}
	goToSide2() {
		if (this.side == 2) return;
        this.side = 2;
		this.x = this.x2;
		this.y = this.y2;
		//if (this.side2Index > 0)
		//alert('goToSide2() Side2Index: ' + this.side2Index + ' Piece: ' + this);
		this.edges = this.edges.slice(this.side2Index).concat(this.edges.slice(0, this.side2Index));
		//if (this.side2Index > 0)
		//alert('After: ' + this);
	}
	rotateSide2() {
        let side2 = false;
        if (this.side == 2) {
            side2 = true;
            this.goToSide1();
        }
		this.side2Index = (this.side2Index + 1) % 4;
        if (side2) this.goToSide2();
	}
	getEdgeDirection(edge) {
		return this.edges.indexOf(edge);
	}
	toString() {
		let string = this.id;
		for (let i = 0; i < this.edges.length; i++) {
			string += "," + this.edges[i].toString();
		}
		return string;
	}
}
