class PieceEdge {
	constructor() {
		this.id = 0;
		this.isOuterSide1 = false;
		this.otherPiece = null;
	}
	setConnectingId(otherEdgeId) {
		this.id = -otherEdgeId;
	}
	fitsWith(otherEdgeId) {
		return this.id == -otherEdgeId || this.id == 0 || otherEdgeId == 0;
	}
	isFlat() {
		return this.id == 0;
	}
	toString() {
		return this.id;
	}
}