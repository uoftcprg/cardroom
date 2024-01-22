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

	constructor(width, height, frameRate, canvas, settings, dataGetter) {
		this.width = width;
		this.height = height;
		this.frameRate = frameRate;
		this.canvas = canvas;
		this.settings = settings;
		this.dataGetter = dataGetter;
	}

	get data() {
		return this.dataGetter();
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
		frameRate(this.frameRate);
		textAlign(CENTER, CENTER);
		textureMode(NORMAL);
		rectMode(CENTER);
		imageMode(CENTER);
	}

	draw() {
		const data = this.data;

		push();

		translate(width / 2, height / 2);
		scale(min(width, height), -min(width, height));

		background(settings["background_color"]);
		this.drawTable(data);

		for (let i = 0; i < data["names"].length; ++i)
			this.drawSeat(data, i);

		pop();
	}

	drawTable(data) {
		push();

		translate(settings["table_x"], settings["table_y"]);

		push();
		fill(settings["table_border_color"]);
		stroke(settings["table_border_color"]);
		strokeWeight(0);
		ellipse(0, 0, settings["table_outer_width"], settings["table_outer_height"]);
		pop();

		push();
		fill(settings["table_felt_color"]);
		stroke(settings["table_felt_color"]);
		strokeWeight(0);
		ellipse(0, 0, settings["table_inner_width"], settings["table_inner_height"]);
		pop();

		pop();

		push();

		translate(settings["board_x"], settings["board_y"]);

		push();
		fill(settings["board_color"]);
		stroke(settings["board_color"]);
		strokeWeight(0);
		rect(0, 0, settings["board_width"], settings["board_height"], settings["board_radius"]);
		pop();

		push();
		fill(settings["board_pot_text_color"]);
		stroke(settings["board_pot_text_color"]);
		strokeWeight(0);
		textStyle(settings["board_pot_text_style"]);
		textFont(settings["board_pot_text_font"], settings["board_pot_text_size"]);
		this.text(settings["board_pot_text"] + data["pots"].join(", "), 0, 0);
		pop();

		if (data["board_count"] > 0) {
			const boardCardWidth = (settings["board_width"] - 2 * settings["board_radius"] - (data["board_count"] - 1) * settings["board_card_margin"]) / data["board_count"];
			let boardCardX = -settings["board_width"] / 2 + settings["board_radius"] + boardCardWidth / 2;
			const boardCardY = settings["board_height"] / 2 + settings["board_card_height"] / 2 + settings["board_card_margin"];

			for (const card of data["board"]) {
				push();

				translate(boardCardX, boardCardY);

				push();
				fill(settings["board_card_color"]);
				stroke(settings["board_card_color"]);
				strokeWeight(0);
				rect(0, 0, boardCardWidth, settings["board_card_height"], settings["board_card_radius"]);
				pop();

				push();
				fill(settings[Felt.suitColorKeys[card["suit"]]]);
				stroke(settings[Felt.suitColorKeys[card["suit"]]]);
				strokeWeight(0);
				textStyle(settings["board_card_text_style"]);
				textFont(settings["board_card_text_font"], settings["board_card_text_size"]);
				this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
				pop();

				pop();

				boardCardX += boardCardWidth + settings["board_card_margin"];
			}
		}

		pop();
	}

	drawSeat(data, index) {
		const angle = -TAU * index / data["names"].length;

		push();

		translate(settings["table_x"], settings["table_y"]);

		if (data["button"] === index) {
			let point = this.getPointOnEllipse(0, 0, settings["button_ring_width"], settings["button_ring_height"], angle + settings["button_angle"]);

			push();

			translate(point.x, point.y);

			push();
			fill(settings["button_color"]);
			stroke(settings["button_color"]);
			strokeWeight(0);
			circle(0, 0, settings["button_diameter"]);
			pop();

			push();
			fill(settings["button_text_color"]);
			stroke(settings["button_text_color"]);
			strokeWeight(0);
			textStyle(settings["button_text_style"]);
			textFont(settings["button_text_font"], settings["button_text_size"]);
			this.text(settings["button_text"], 0, 0);
			pop();

			pop();
		}

		if (data["bets"][index] !== null && data["bets"][index] !== 0) {
			let point = this.getPointOnEllipse(0, 0, settings["bet_ring_width"], settings["bet_ring_height"], angle + settings["bet_angle"]);

			push();

			translate(point.x, point.y);

			textStyle(settings["bet_text_style"]);
			textFont(settings["bet_text_font"], settings["bet_text_size"]);

			const betText = data["bets"][index];
			const betBoxWidth = textWidth(betText) + settings["bet_box_x_padding"];

			push();
			fill(settings["bet_box_color"]);
			stroke(settings["bet_box_color"]);
			strokeWeight(0);
			rect(0, 0, betBoxWidth, settings["bet_box_height"], settings["bet_box_radius"]);
			pop();

			push();
			fill(settings["bet_text_color"]);
			stroke(settings["bet_text_color"]);
			strokeWeight(0);
			this.text(betText, 0, 0);
			pop();

			pop();
		}

		let point = this.getPointOnEllipse(0, 0, settings["seat_ring_width"], settings["seat_ring_height"], angle + settings["seat_angle"]);

		push();

		translate(point.x, point.y);

		if (data["holes"][index] !== null) {
			push();

			translate(settings["hole_x"], settings["hole_y"]);

			push();
			fill(settings["hole_color"]);
			stroke(settings["hole_color"]);
			strokeWeight(0);
			rect(0, 0, settings["hole_width"], settings["hole_height"], settings["hole_radius"]);
			pop();

			let cardCount = data["hole_statuses"].reduce((a, b) => a + b, 0);
			cardCount = Math.max(cardCount, data["hole_statuses"].length - cardCount);
			const holeCardWidth = (settings["hole_width"] - 2 * settings["hole_radius"] - (cardCount - 1) * settings["hole_card_margin"]) / cardCount;
			const initialHoleCardX = -settings["hole_width"] / 2 + settings["hole_radius"] + holeCardWidth / 2;
			let holeCardX = initialHoleCardX;
			let holeCardY = settings["hole_height"] / 2 + settings["hole_card_height"] / 2 + settings["hole_card_margin"];

			for (const status_ of [false, true]) {
				for (let i = 0; i < data["holes"][index].length; ++i) {
					if (data["hole_statuses"][i] !== status_)
						continue;

					const card = data["holes"][index][i];

					push();

					translate(holeCardX, holeCardY);

					push();
					fill(settings["hole_card_color"]);
					stroke(settings["hole_card_color"]);
					strokeWeight(0);
					rect(0, 0, holeCardWidth, settings["hole_card_height"], settings["hole_card_radius"]);
					pop();

					push();
					fill(settings[Felt.suitColorKeys[card["suit"]]]);
					stroke(settings[Felt.suitColorKeys[card["suit"]]]);
					strokeWeight(0);
					textStyle(settings["hole_card_text_style"]);
					textFont(settings["hole_card_text_font"], settings["hole_card_text_size"]);
					this.text(card["rank"] + Felt.suitChars[card["suit"]], 0, 0);
					pop();

					pop();

					holeCardX += holeCardWidth + settings["hole_card_margin"];
				}

				holeCardX = initialHoleCardX;
				holeCardY += settings["hole_card_height"] + settings["hole_card_margin"];
			}

			pop();
		}

		if (data["names"][index] !== null) {
			push();

			translate(settings["name_x"], settings["name_y"]);

			push();
			fill(settings["name_box_color"]);
			stroke(settings["name_box_color"]);
			strokeWeight(0);
			rect(0, 0, settings["name_box_width"], settings["name_box_height"], settings["name_box_radius"]);
			pop();

			push();
			fill(settings["name_text_color"]);
			stroke(settings["name_text_color"]);
			strokeWeight(0);
			textStyle(settings["name_text_style"]);
			textFont(settings["name_text_font"], settings["name_text_size"]);
			this.text(data["names"][index], 0, 0);
			pop();

			pop();
		}

		if (data["stacks"][index] !== null) {
			push();

			translate(settings["stack_x"], settings["stack_y"]);

			push();
			fill(settings["stack_box_color"]);
			stroke(settings["stack_box_color"]);
			strokeWeight(0);
			rect(0, 0, settings["stack_box_width"], settings["stack_box_height"], settings["stack_box_radius"]);
			pop();

			push();
			fill(settings["stack_text_color"]);
			stroke(settings["stack_text_color"]);
			strokeWeight(0);
			textStyle(settings["stack_text_style"]);
			textFont(settings["stack_text_font"], settings["stack_text_size"]);
			this.text(data["stacks"][index], 0, 0);
			pop();

			pop();
		}

		if (data["previous_action"] !== null && data["previous_action"][0] === index) {
			push();

			translate(settings["previous_action_x"], settings["previous_action_y"]);

			push();
			fill(settings["previous_action_box_color"]);
			stroke(settings["previous_action_box_color"]);
			strokeWeight(0);
			rect(0, 0, settings["previous_action_box_width"], settings["previous_action_box_height"], settings["previous_action_box_radius"]);
			pop();

			push();
			fill(settings["previous_action_text_color"]);
			stroke(settings["previous_action_text_color"]);
			strokeWeight(0);
			textStyle(settings["previous_action_text_style"]);
			textFont(settings["previous_action_text_font"], settings["previous_action_text_size"]);
			this.text(data["previous_action"][1], 0, 0);
			pop();

			pop();
		}

		pop();

		pop();
	}
}
