function join_() {
	cashGameSocket.send(JSON.stringify(`j ${jSeatIndex.value}`));

	jSeatIndex.value = "";
}

function leave() {
	cashGameSocket.send(JSON.stringify("l"));
}

function sitOut() {
	cashGameSocket.send(JSON.stringify("s"));
}

function beBack() {
	cashGameSocket.send(JSON.stringify("b"));
}

function buyRebuyTopOffOrRateHole() {
	cashGameSocket.send(JSON.stringify(`brtr ${brtrAmount.value}`));

	brtrAmount.value = "";
}

function standPatOrDiscard() {
	cashGameSocket.send(JSON.stringify(`sd ${sdCards.value}`));

	sdCards.value = "";
}

function fold() {
	cashGameSocket.send(JSON.stringify("f"));
}

function checkOrCall() {
	cashGameSocket.send(JSON.stringify("cc"));
}

function postBringIn() {
	cashGameSocket.send(JSON.stringify("pb"));
}

function completeBetOrRaise() {
	cashGameSocket.send(JSON.stringify(`cbr ${cbrAmount.value}`));

	cbrAmount.value = "";
}

function showHoleCards() {
	cashGameSocket.send(JSON.stringify(`sm ${smCards.value}`));

	smCards.value = "";
}

function getData() {
	dataGuard = false;

	return data[0];
}

function shifter() {
	if (!dataGuard && data.length > 1)
		data.shift();
}

function watchdog() {
}

const canvas = document.getElementById("felt");
const jSeatIndex = document.getElementById("j-seat-index");
const brtrAmount = document.getElementById("brtr-amount");
const sdCards = document.getElementById("sd-cards");
const cbrAmount = document.getElementById("cbr-amount");
const smCards = document.getElementById("sm-cards");
const pk = JSON.parse(document.getElementById("pk").textContent);
const settings = JSON.parse(document.getElementById("settings").textContent);
let dataGuard = true;
let data = [JSON.parse(document.getElementById("data").textContent)];
const felt = new Felt(canvas.width, canvas.height, 1000, canvas, settings, getData);
let protocol;

if (location.protocol === "http:")
	protocol = "ws:"
else if (location.protocol === "https:")
	protocol = "wss:";
else
	protocol = "";

const cashGameSocket = new WebSocket(`${protocol}//${location.host}/ws/cash-game/${pk}/`);
cashGameSocket.onmessage = function(event) {
	dataGuard = true;

	data.push(...JSON.parse(event.data).data);
}
cashGameSocket.onclose = function(event) {
	console.error("Cash game socket closed unexpectedly");
}

setInterval(shifter, settings["shifter_timeout"] * 1000);
