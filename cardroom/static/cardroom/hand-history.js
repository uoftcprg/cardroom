let index = 0;

function update() {
	previousButton.disabled = index === 0;
	nextButton.disabled = index === data.length - 1;
	indexSpan.innerText = index + 1;
	maxIndexSpan.innerText = data.length;
}

function decrementIndex() {
	index = Math.max(0, index - 1);

	update();
}

function incrementIndex() {
	index = Math.min(index + 1, data.length - 1);

	update();
}

const canvas = document.getElementById("felt");
const previousButton = document.getElementById("previous");
const nextButton = document.getElementById("next");
const indexSpan = document.getElementById("index");
const maxIndexSpan = document.getElementById("max-index");
const configuration = JSON.parse(document.getElementById("configuration").textContent);
const data = JSON.parse(document.getElementById("data").textContent);
const dataGetter = () => data[index];
const felt = new Felt(canvas.width, canvas.height, canvas, configuration, dataGetter);

update();
