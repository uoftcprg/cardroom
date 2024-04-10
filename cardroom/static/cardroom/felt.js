function setup() {
	felt.setup();
}

function draw() {
	felt.draw();
}

class Felt {
	static suitChars = {
		"c": "♣",
		"d": "♦",
		"h": "♥",
		"s": "♠",
		"?": " ",
	};
	static suitColorKeys = {
		"c": "club_color",
		"d": "diamond_color",
		"h": "heart_color",
		"s": "spade_color",
		"?": "unknown_color",
	};

	constructor(width, height, canvas, style, frameGetter) {
		this.width = width;
		this.height = height;
		this.canvas = canvas;
		this.style = style;
		this.frameGetter = frameGetter;
	}

	get frame() {
		return this.frameGetter();
	}

	getPointOnEllipse(x, y, w, h, angle) {
		angle = ((angle % TAU) + TAU) % TAU;
		let rx = w / 2;
		let ry = h / 2;
		let dx = rx * ry / sqrt(ry ** 2 + rx ** 2 * tan(angle) ** 2);
		let dy = rx * ry / sqrt(rx ** 2 + ry ** 2 / tan(angle) ** 2);

		if (HALF_PI <= angle && angle < PI + HALF_PI)
			dx *= -1;

		if (PI <= angle && angle < TAU)
			dy *= -1;

		return createVector(x + dx, y + dy);
	}

	text(str, x, y) {
		push();
		translate(x, y);
		scale(1, -1);
		text(str, 0, 0);
		pop();
	}

	setup() {
		createCanvas(this.width, this.height, canvas);
		frameRate(style["frame_rate"]);
		textAlign(CENTER, CENTER);
		textureMode(NORMAL);
		rectMode(CENTER);
		imageMode(CENTER);
	}

	draw() {
		const frame = this.frame;

		push();

		translate(width / 2, height / 2);
		scale(min(width, height), -min(width, height));

		background(style["background_color"]);
		this.drawTable(frame);

		for (let i = 0; i < frame["seats"].length; ++i)
			this.drawSeat(frame, i);

		pop();
	}

	drawTable(frame) {
		push();

		translate(style["table_x"], style["table_y"]);

		push();
		fill(style["table_border_color"]);
		stroke(style["table_border_color"]);
		strokeWeight(0);
		ellipse(0, 0, style["table_outer_width"], style["table_outer_height"]);
		pop();

		push();
		fill(style["table_felt_color"]);
		stroke(style["table_felt_color"]);
		strokeWeight(0);
		ellipse(0, 0, style["table_inner_width"], style["table_inner_height"]);
		pop();

		pop();

		push();

		translate(style["board_x"], style["board_y"]);

		push();
		fill(style["board_color"]);
		stroke(style["board_color"]);
		strokeWeight(0);
		rect(0, 0, style["board_width"], style["board_height"], style["board_radius"]);
		pop();

		push();
		fill(style["board_pot_text_color"]);
		stroke(style["board_pot_text_color"]);
		strokeWeight(0);
		textStyle(style["board_pot_text_style"]);
		textFont(style["board_pot_text_font"], style["board_pot_text_size"]);
		this.text(style["board_pot_text"] + frame["pot"].join(", "), 0, 0);
		pop();

		let boardCount = 0;

		for (const count of frame["game"]["board"])
			boardCount += count;

		if (boardCount > 0) {
			const boardCardWidth = (style["board_width"] - 2 * style["board_radius"] - (boardCount - 1) * style["board_card_margin"]) / boardCount;
			let boardCardX = -style["board_width"] / 2 + style["board_radius"] + boardCardWidth / 2;
			const boardCardY = style["board_height"] / 2 + style["board_card_height"] / 2 + style["board_card_margin"];

			for (const card of frame["board"]) {
				push();

				translate(boardCardX, boardCardY);

				push();
				fill(style["board_card_color"]);
				stroke(style["board_card_color"]);
				strokeWeight(0);
				rect(0, 0, boardCardWidth, style["board_card_height"], style["board_card_radius"]);
				pop();

				push();
				fill(style[Felt.suitColorKeys[card["suit"]]]);
				stroke(style[Felt.suitColorKeys[card["suit"]]]);
				strokeWeight(0);
				textStyle(style["board_card_text_style"]);
				textFont(style["board_card_text_font"], style["board_card_text_size"]);
				this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
				pop();

				pop();

				boardCardX += boardCardWidth + style["board_card_margin"];
			}
		}

		pop();
	}

	drawSeat(frame, index) {
		const seat = frame["seats"][index];
		const angle = -TAU * index / frame["seats"].length;

		push();

		translate(style["table_x"], style["table_y"]);

		if (seat["button"]) {
			let point = this.getPointOnEllipse(0, 0, style["button_ring_width"], style["button_ring_height"], angle + style["button_angle"]);

			push();

			translate(point.x, point.y);

			push();
			fill(style["button_color"]);
			stroke(style["button_color"]);
			strokeWeight(0);
			circle(0, 0, style["button_diameter"]);
			pop();

			push();
			fill(style["button_text_color"]);
			stroke(style["button_text_color"]);
			strokeWeight(0);
			textStyle(style["button_text_style"]);
			textFont(style["button_text_font"], style["button_text_size"]);
			this.text(style["button_text"], 0, 0);
			pop();

			pop();
		}

		if (seat["bet"] !== null && seat["bet"] !== 0) {
			let point = this.getPointOnEllipse(0, 0, style["bet_ring_width"], style["bet_ring_height"], angle + style["bet_angle"]);

			push();

			translate(point.x, point.y);

			textStyle(style["bet_text_style"]);
			textFont(style["bet_text_font"], style["bet_text_size"]);

			const betText = seat["bet"];
			const betBoxWidth = textWidth(betText) + style["bet_box_x_padding"];

			push();
			fill(style["bet_box_color"]);
			stroke(style["bet_box_color"]);
			strokeWeight(0);
			rect(0, 0, betBoxWidth, style["bet_box_height"], style["bet_box_radius"]);
			pop();

			push();
			fill(style["bet_text_color"]);
			stroke(style["bet_text_color"]);
			strokeWeight(0);
			this.text(betText, 0, 0);
			pop();

			pop();
		}

		let point = this.getPointOnEllipse(0, 0, style["seat_ring_width"], style["seat_ring_height"], angle + style["seat_angle"]);

		push();

		translate(point.x, point.y);

		if (seat["hole"] !== null) {
			push();

			translate(style["hole_x"], style["hole_y"]);

			push();
			fill(style["hole_color"]);
			stroke(style["hole_color"]);
			strokeWeight(0);
			rect(0, 0, style["hole_width"], style["hole_height"], style["hole_radius"]);
			pop();

			let cardCount = frame["game"]["hole"].flat().reduce((a, b) => a + b, 0);
			cardCount = Math.max(cardCount, frame["game"]["hole"].flat().length - cardCount);
			const holeCardWidth = (style["hole_width"] - 2 * style["hole_radius"] - (cardCount - 1) * style["hole_card_margin"]) / cardCount;
			const initialHoleCardX = -style["hole_width"] / 2 + style["hole_radius"] + holeCardWidth / 2;
			let holeCardX = initialHoleCardX;
			let holeCardY = style["hole_height"] / 2 + style["hole_card_height"] / 2 + style["hole_card_margin"];

			for (const status_ of [false, true]) {
				for (let i = 0; i < seat["hole"].length; ++i) {
					if (frame["game"]["hole"].flat()[i] !== status_)
						continue;

					const card = seat["hole"][i];

					push();

					translate(holeCardX, holeCardY);

					push();
					fill(style["hole_card_color"]);
					stroke(style["hole_card_color"]);
					strokeWeight(0);
					rect(0, 0, holeCardWidth, style["hole_card_height"], style["hole_card_radius"]);
					pop();

					push();
					fill(style[Felt.suitColorKeys[card["suit"]]]);
					stroke(style[Felt.suitColorKeys[card["suit"]]]);
					strokeWeight(0);
					textStyle(style["hole_card_text_style"]);
					textFont(style["hole_card_text_font"], style["hole_card_text_size"]);
					this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
					pop();

					pop();

					holeCardX += holeCardWidth + style["hole_card_margin"];
				}

				holeCardX = initialHoleCardX;
				holeCardY += style["hole_card_height"] + style["hole_card_margin"];
			}

			pop();
		}

		if (seat["user"]) {
			push();

			translate(style["name_x"], style["name_y"]);

			push();
			fill(style["name_box_color"]);
			stroke(style["name_box_color"]);
			strokeWeight(0);
			rect(0, 0, style["name_box_width"], style["name_box_height"], style["name_box_radius"]);
			pop();

			push();
			fill(style["name_text_color"]);
			stroke(style["name_text_color"]);
			strokeWeight(0);
			textStyle(style["name_text_style"]);
			textFont(style["name_text_font"], style["name_text_size"]);
			this.text(seat["user"], 0, 0);
			pop();

			pop();
		}

		if (seat["stack"] !== null) {
			push();

			translate(style["stack_x"], style["stack_y"]);

			push();
			fill(style["stack_box_color"]);
			stroke(style["stack_box_color"]);
			strokeWeight(0);
			rect(0, 0, style["stack_box_width"], style["stack_box_height"], style["stack_box_radius"]);
			pop();

			push();
			fill(style["stack_text_color"]);
			stroke(style["stack_text_color"]);
			strokeWeight(0);
			textStyle(style["stack_text_style"]);
			textFont(style["stack_text_font"], style["stack_text_size"]);
			this.text(seat["stack"], 0, 0);
			pop();

			pop();
		}

		pop();

		pop();
	}
}
