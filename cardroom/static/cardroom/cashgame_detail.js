function standPatOrDiscard() {
	cashGameSocket.send(JSON.stringify(`sd ${discardedCards.value}`));

	discardedCards.value = "";
}

function fold() {
	cashGameSocket.send(JSON.stringify("f"));
}

function checkOrCall() {
	cashGameSocket.send(JSON.stringify("cc"));
}

function postBringIn() {
	cashGameSocket.send(JSON.stringify("pbi"));
}

function completeBetOrRaise() {
	cashGameSocket.send(JSON.stringify(`cbr ${amount.value}`));

	amount.value = "";
}

function showHoleCards() {
	cashGameSocket.send(JSON.stringify(`sm ${holeCards.join("")}`));
}

function muckHoleCards() {
	cashGameSocket.send(JSON.stringify("sm"));
}

const canvas = document.getElementById("felt");
const discardedCards = document.getElementById("discarded-cards");
const amount = document.getElementById("amount");
const pk = JSON.parse(document.getElementById("pk").textContent);
const settings = JSON.parse(document.getElementById("settings").textContent);
const data = JSON.parse(document.getElementById("data").textContent);
const dataGetter = () => data;
const holeCards = [];
const felt = new Felt(1024, 768, 1000, canvas, settings, dataGetter);
let protocol;

if (location.protocol === "http:")
	protocol = "ws:"
else if (location.protocol === "https:")
	protocol = "wss:";
else
	protocol = "";

const cashGameSocket = new WebSocket(`${protocol}//${location.host}/ws/cash-game/${pk}/`);
cashGameSocket.onmessage = function(event) {
	const data = JSON.parse(event.data);

	// TODO: set data
	console.log(data);
}
cashGameSocket.onclose = function(event) {
	console.error("Cash game socket closed unexpectedly");
}
