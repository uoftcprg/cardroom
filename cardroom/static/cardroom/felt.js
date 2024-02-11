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

	constructor(width, height, canvas, configuration, frameGetter) {
		this.width = width;
		this.height = height;
		this.canvas = canvas;
		this.configuration = configuration;
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
		frameRate(configuration["frame_rate"]);
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

		background(configuration["background_color"]);
		this.drawTable(frame);

		for (let i = 0; i < frame["names"].length; ++i)
			this.drawSeat(frame, i);

		pop();
	}

	drawTable(frame) {
		push();

		translate(configuration["table_x"], configuration["table_y"]);

		push();
		fill(configuration["table_border_color"]);
		stroke(configuration["table_border_color"]);
		strokeWeight(0);
		ellipse(0, 0, configuration["table_outer_width"], configuration["table_outer_height"]);
		pop();

		push();
		fill(configuration["table_felt_color"]);
		stroke(configuration["table_felt_color"]);
		strokeWeight(0);
		ellipse(0, 0, configuration["table_inner_width"], configuration["table_inner_height"]);
		pop();

		pop();

		push();

		translate(configuration["board_x"], configuration["board_y"]);

		push();
		fill(configuration["board_color"]);
		stroke(configuration["board_color"]);
		strokeWeight(0);
		rect(0, 0, configuration["board_width"], configuration["board_height"], configuration["board_radius"]);
		pop();

		push();
		fill(configuration["board_pot_text_color"]);
		stroke(configuration["board_pot_text_color"]);
		strokeWeight(0);
		textStyle(configuration["board_pot_text_style"]);
		textFont(configuration["board_pot_text_font"], configuration["board_pot_text_size"]);
		this.text(configuration["board_pot_text"] + frame["pots"].join(", "), 0, 0);
		pop();

		if (frame["board_count"] > 0) {
			const boardCardWidth = (configuration["board_width"] - 2 * configuration["board_radius"] - (frame["board_count"] - 1) * configuration["board_card_margin"]) / frame["board_count"];
			let boardCardX = -configuration["board_width"] / 2 + configuration["board_radius"] + boardCardWidth / 2;
			const boardCardY = configuration["board_height"] / 2 + configuration["board_card_height"] / 2 + configuration["board_card_margin"];

			for (const card of frame["board"]) {
				push();

				translate(boardCardX, boardCardY);

				push();
				fill(configuration["board_card_color"]);
				stroke(configuration["board_card_color"]);
				strokeWeight(0);
				rect(0, 0, boardCardWidth, configuration["board_card_height"], configuration["board_card_radius"]);
				pop();

				push();
				fill(configuration[Felt.suitColorKeys[card["suit"]]]);
				stroke(configuration[Felt.suitColorKeys[card["suit"]]]);
				strokeWeight(0);
				textStyle(configuration["board_card_text_style"]);
				textFont(configuration["board_card_text_font"], configuration["board_card_text_size"]);
				this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
				pop();

				pop();

				boardCardX += boardCardWidth + configuration["board_card_margin"];
			}
		}

		pop();
	}

	drawSeat(frame, index) {
		const angle = -TAU * index / frame["names"].length;

		push();

		translate(configuration["table_x"], configuration["table_y"]);

		if (frame["button"] === index) {
			let point = this.getPointOnEllipse(0, 0, configuration["button_ring_width"], configuration["button_ring_height"], angle + configuration["button_angle"]);

			push();

			translate(point.x, point.y);

			push();
			fill(configuration["button_color"]);
			stroke(configuration["button_color"]);
			strokeWeight(0);
			circle(0, 0, configuration["button_diameter"]);
			pop();

			push();
			fill(configuration["button_text_color"]);
			stroke(configuration["button_text_color"]);
			strokeWeight(0);
			textStyle(configuration["button_text_style"]);
			textFont(configuration["button_text_font"], configuration["button_text_size"]);
			this.text(configuration["button_text"], 0, 0);
			pop();

			pop();
		}

		if (frame["bets"][index] !== null && frame["bets"][index] !== 0) {
			let point = this.getPointOnEllipse(0, 0, configuration["bet_ring_width"], configuration["bet_ring_height"], angle + configuration["bet_angle"]);

			push();

			translate(point.x, point.y);

			textStyle(configuration["bet_text_style"]);
			textFont(configuration["bet_text_font"], configuration["bet_text_size"]);

			const betText = frame["bets"][index];
			const betBoxWidth = textWidth(betText) + configuration["bet_box_x_padding"];

			push();
			fill(configuration["bet_box_color"]);
			stroke(configuration["bet_box_color"]);
			strokeWeight(0);
			rect(0, 0, betBoxWidth, configuration["bet_box_height"], configuration["bet_box_radius"]);
			pop();

			push();
			fill(configuration["bet_text_color"]);
			stroke(configuration["bet_text_color"]);
			strokeWeight(0);
			this.text(betText, 0, 0);
			pop();

			pop();
		}

		let point = this.getPointOnEllipse(0, 0, configuration["seat_ring_width"], configuration["seat_ring_height"], angle + configuration["seat_angle"]);

		push();

		translate(point.x, point.y);

		if (frame["holes"][index] !== null) {
			push();

			translate(configuration["hole_x"], configuration["hole_y"]);

			push();
			fill(configuration["hole_color"]);
			stroke(configuration["hole_color"]);
			strokeWeight(0);
			rect(0, 0, configuration["hole_width"], configuration["hole_height"], configuration["hole_radius"]);
			pop();

			let cardCount = frame["hole_statuses"].reduce((a, b) => a + b, 0);
			cardCount = Math.max(cardCount, frame["hole_statuses"].length - cardCount);
			const holeCardWidth = (configuration["hole_width"] - 2 * configuration["hole_radius"] - (cardCount - 1) * configuration["hole_card_margin"]) / cardCount;
			const initialHoleCardX = -configuration["hole_width"] / 2 + configuration["hole_radius"] + holeCardWidth / 2;
			let holeCardX = initialHoleCardX;
			let holeCardY = configuration["hole_height"] / 2 + configuration["hole_card_height"] / 2 + configuration["hole_card_margin"];

			for (const status_ of [false, true]) {
				for (let i = 0; i < frame["holes"][index].length; ++i) {
					if (frame["hole_statuses"][i] !== status_)
						continue;

					const card = frame["holes"][index][i];

					push();

					translate(holeCardX, holeCardY);

					push();
					fill(configuration["hole_card_color"]);
					stroke(configuration["hole_card_color"]);
					strokeWeight(0);
					rect(0, 0, holeCardWidth, configuration["hole_card_height"], configuration["hole_card_radius"]);
					pop();

					push();
					fill(configuration[Felt.suitColorKeys[card["suit"]]]);
					stroke(configuration[Felt.suitColorKeys[card["suit"]]]);
					strokeWeight(0);
					textStyle(configuration["hole_card_text_style"]);
					textFont(configuration["hole_card_text_font"], configuration["hole_card_text_size"]);
					this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
					pop();

					pop();

					holeCardX += holeCardWidth + configuration["hole_card_margin"];
				}

				holeCardX = initialHoleCardX;
				holeCardY += configuration["hole_card_height"] + configuration["hole_card_margin"];
			}

			pop();
		}

		if (frame["names"][index] !== null) {
			push();

			translate(configuration["name_x"], configuration["name_y"]);

			push();
			fill(configuration["name_box_color"]);
			stroke(configuration["name_box_color"]);
			strokeWeight(0);
			rect(0, 0, configuration["name_box_width"], configuration["name_box_height"], configuration["name_box_radius"]);
			pop();

			push();
			fill(configuration["name_text_color"]);
			stroke(configuration["name_text_color"]);
			strokeWeight(0);
			textStyle(configuration["name_text_style"]);
			textFont(configuration["name_text_font"], configuration["name_text_size"]);
			this.text(frame["names"][index], 0, 0);
			pop();

			pop();
		}

		if (frame["stacks"][index] !== null) {
			push();

			translate(configuration["stack_x"], configuration["stack_y"]);

			push();
			fill(configuration["stack_box_color"]);
			stroke(configuration["stack_box_color"]);
			strokeWeight(0);
			rect(0, 0, configuration["stack_box_width"], configuration["stack_box_height"], configuration["stack_box_radius"]);
			pop();

			push();
			fill(configuration["stack_text_color"]);
			stroke(configuration["stack_text_color"]);
			strokeWeight(0);
			textStyle(configuration["stack_text_style"]);
			textFont(configuration["stack_text_font"], configuration["stack_text_size"]);
			this.text(frame["stacks"][index], 0, 0);
			pop();

			pop();
		}

		if (frame["previous_action"] !== null && frame["previous_action"][0] === index) {
			push();

			translate(configuration["previous_action_x"], configuration["previous_action_y"]);

			push();
			fill(configuration["previous_action_box_color"]);
			stroke(configuration["previous_action_box_color"]);
			strokeWeight(0);
			rect(0, 0, configuration["previous_action_box_width"], configuration["previous_action_box_height"], configuration["previous_action_box_radius"]);
			pop();

			push();
			fill(configuration["previous_action_text_color"]);
			stroke(configuration["previous_action_text_color"]);
			strokeWeight(0);
			textStyle(configuration["previous_action_text_style"]);
			textFont(configuration["previous_action_text_font"], configuration["previous_action_text_size"]);
			this.text(frame["previous_action"][1], 0, 0);
			pop();

			pop();
		}

		pop();

		pop();
	}
}
