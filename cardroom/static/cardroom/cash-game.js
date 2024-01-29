function join_() {
	webSocket.send(JSON.stringify(`j ${jSeatIndex.value}`));

	jSeatIndex.value = "";
}

function leave() {
	webSocket.send(JSON.stringify("l"));
}

function sitOut() {
	webSocket.send(JSON.stringify("s"));
}

function beBack() {
	webSocket.send(JSON.stringify("b"));
}

function buyRebuyTopOffOrRateHole() {
	webSocket.send(JSON.stringify(`brtr ${brtrAmount.value}`));

	brtrAmount.value = "";
}

function standPatOrDiscard() {
	webSocket.send(JSON.stringify(`sd ${sdCards.value}`));

	sdCards.value = "";
}

function fold() {
	webSocket.send(JSON.stringify("f"));
}

function checkOrCall() {
	webSocket.send(JSON.stringify("cc"));
}

function postBringIn() {
	webSocket.send(JSON.stringify("pb"));
}

function completeBetOrRaise() {
	webSocket.send(JSON.stringify(`cbr ${cbrAmount.value}`));

	cbrAmount.value = "";
}

function showHoleCards() {
	webSocket.send(JSON.stringify(`sm ${smCards.value}`));

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
const websocketURL = JSON.parse(document.getElementById("websocket_url").textContent);
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

const webSocket = new WebSocket(`${protocol}//${location.host}${websocketURL}`);
webSocket.onmessage = function(event) {
	eventData = JSON.parse(event.data);

	switch (eventData.type) {
	case "data":
		dataGuard = true;

		data.push(...eventData["data"]);

		break;
	case "message":
		alert(eventData["message"]);

		break;
	}
}
webSocket.onclose = function(event) {
	console.error("Cash game socket closed unexpectedly");
}

setInterval(shifter, settings["shifter_timeout"] * 1000);
