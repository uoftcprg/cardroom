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

function getFrame() {
	frameGuard = false;

	return frames[0];
}

function shifter() {
	if (!frameGuard && frames.length > 1)
		frames.shift();
}

function createWebSocket() {
	return new WebSocket(`${protocol}//${location.host}${websocketURL}`);
}

function watchdog() {
	if (webSocket.readyState == webSocket.CLOSED)
		webSocket = createWebSocket();
}

function updateActions() {
	const frame = frames[frames.length - 1];

	jButton.innerText = "Join";

	if (frame["action"]["j"] === null)
		jSeatIndex.value = "";
	else
		jSeatIndex.value = frame["action"]["j"].join(", ");

	jButton.disabled = frame["action"]["j"] === null;
	jSeatIndex.disabled = frame["action"]["j"] === null;
	lButton.innerText = "Leave";
	lButton.disabled = frame["action"]["l"] === null;
	sButton.innerText = "Sit out";
	sButton.disabled = frame["action"]["s"] === null;
	bButton.innerText = "I'm back";
	bButton.disabled = frame["action"]["b"] === null;
	brtrButton.innerText = "Override stack";
	brtrButton.disabled = frame["action"]["brtr"] === null;

	if (frame["action"]["brtr"] === null)
		brtrAmount.value = "";
	else
		brtrAmount.value = frame["action"]["brtr"].join(" - ");

	brtrAmount.disabled = frame["action"]["brtr"] === null;
	sdButton.innerText = "Stand pat/Discard";
	sdButton.disabled = frame["action"]["sd"] === null;
	
	if (frame["action"]["sd"] === null)
		sdCards.value = "";
	else
		sdCards.value = frame["action"]["sd"].join("");

	sdCards.disabled = frame["action"]["sd"] === null;
	fButton.innerText = "Fold";
	fButton.disabled = frame["action"]["f"] === null;

	if (frame["action"]["cc"] === null)
		ccButton.innerText = "Check/Call";
	else if (frame["action"]["cc"] === 0)
		ccButton.innerText = "Check";
	else
		ccButton.innerText = `Call ${frame["action"]["cc"]}`;

	ccButton.disabled = frame["action"]["cc"] === null;

	if (frame["action"]["pb"] === null)
		pbButton.innerText = "Bring-in";
	else
		pbButton.innerText = `Bring-in ${frame["action"]["pb"]}`;

	pbButton.disabled = frame["action"]["pb"] === null;

	if (frame["action"]["cbr"] === null)
		cbrButton.innerText = "Complete/Bet/Raise to";
	else if (frame["action"]["cbr"][0])
		cbrButton.innerText = "Complete";
	else if (frame["action"]["cbr"][1])
		cbrButton.innerText = "Raise";
	else
		cbrButton.innerText = "Bet";

	if (frame["action"]["cbr"] === null)
		cbrAmount.value = "";
	else
		cbrAmount.value = `${frame["action"]["cbr"][2]} - ${frame["action"]["cbr"][3]}`;

	cbrButton.disabled = frame["action"]["cbr"] === null;
	cbrAmount.disabled = frame["action"]["cbr"] === null;
	smButton.innerText = "Show/Muck";
	smCards.value = frame["action"]["sm"] ? "-" : "";
	smButton.disabled = frame["action"]["sm"] === null;
	smCards.disabled = frame["action"]["sm"] === null;
}

const canvas = document.getElementById("felt");
const jButton = document.getElementById("j");
const jSeatIndex = document.getElementById("j-seat-index");
const lButton = document.getElementById("l");
const sButton = document.getElementById("s");
const bButton = document.getElementById("b");
const brtrButton = document.getElementById("brtr");
const brtrAmount = document.getElementById("brtr-amount");
const sdButton = document.getElementById("sd");
const sdCards = document.getElementById("sd-cards");
const fButton = document.getElementById("f");
const ccButton = document.getElementById("cc");
const pbButton = document.getElementById("pb");
const cbrButton = document.getElementById("cbr");
const cbrAmount = document.getElementById("cbr-amount");
const smButton = document.getElementById("sm");
const smCards = document.getElementById("sm-cards");
const pk = JSON.parse(document.getElementById("pk").textContent);
const websocketURL = JSON.parse(document.getElementById("websocket_url").textContent);
const style = JSON.parse(document.getElementById("style").textContent);
let frameGuard = true;
let frames = [JSON.parse(document.getElementById("frame").textContent)];
const felt = new Felt(canvas.width, canvas.height, canvas, style, getFrame);
let protocol;

if (location.protocol === "http:")
	protocol = "ws:"
else if (location.protocol === "https:")
	protocol = "wss:";
else
	protocol = "";

let webSocket = createWebSocket();
webSocket.onmessage = function(event) {
	eventData = JSON.parse(event.data);

	switch (eventData.type) {
	case "update":
		frameGuard = true;

		frames.push(...eventData["frames"]);
		updateActions();

		break;
	case "notify":
		alert(eventData["message"]);

		break;
	}
}
webSocket.onclose = function(event) {
	console.error("Cash game socket closed unexpectedly");
}

setInterval(shifter, style["shifter_timeout"] * 1000);
setInterval(watchdog, style["watchdog_timeout"] * 1000);
updateActions();
