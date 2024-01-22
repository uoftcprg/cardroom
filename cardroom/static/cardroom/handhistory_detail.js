let index = 0;

function decrementIndex() {
	index = Math.max(0, index - 1);
}

function incrementIndex() {
	index = Math.min(index + 1, data.length - 1);
}

const canvas = document.getElementById('felt');
const settings = JSON.parse(document.getElementById('settings').textContent);
const data = JSON.parse(document.getElementById('data').textContent);
const dataGetter = () => data[index];
const felt = new Felt(canvas.width, canvas.height, 1000, canvas, settings, dataGetter);
