let index = 0;

function update() {
	previousButton.disabled = index === 0;
	nextButton.disabled = index === frames.length - 1;
	indexSpan.innerText = index + 1;
	maxIndexSpan.innerText = frames.length;
}

function decrementIndex() {
	index = Math.max(0, index - 1);

	update();
}

function incrementIndex() {
	index = Math.min(index + 1, frames.length - 1);

	update();
}

const canvas = document.getElementById("felt");
const previousButton = document.getElementById("previous");
const nextButton = document.getElementById("next");
const indexSpan = document.getElementById("index");
const maxIndexSpan = document.getElementById("max-index");
const configuration = JSON.parse(document.getElementById("configuration").textContent);
const frames = JSON.parse(document.getElementById("frames").textContent);
const frameGetter = () => frames[index];
const felt = new Felt(canvas.width, canvas.height, canvas, configuration, frameGetter);

update();
