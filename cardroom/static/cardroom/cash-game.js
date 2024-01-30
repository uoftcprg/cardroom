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

function createWebSocket() {
	return new WebSocket(`${protocol}//${location.host}${websocketURL}`);
}

function watchdog() {
	if (webSocket.readyState == webSocket.CLOSED)
		webSocket = createWebSocket();
}

function updateActions() {
	const subData = data[data.length - 1];

	jButton.innerText = "Join";

	if (subData["join"] === null)
		jSeatIndex.value = "";
	else
		jSeatIndex.value = subData["join"].join(", ");

	jButton.disabled = subData["join"] === null;
	jSeatIndex.disabled = subData["join"] === null;
	lButton.innerText = "Leave";
	lButton.disabled = !subData["leave"];
	sButton.innerText = "Sit out";
	sButton.disabled = !subData["sit_out"];
	bButton.innerText = "I'm back";
	bButton.disabled = !subData["be_back"];
	brtrButton.innerText = "Override stack";
	brtrButton.disabled = subData["buy_rebuy_top_off_or_rat_hole"] === null;

	if (subData["buy_rebuy_top_off_or_rat_hole"] === null)
		brtrAmount.value = "";
	else
		brtrAmount.value = subData["buy_rebuy_top_off_or_rat_hole"].join(" - ");

	brtrAmount.disabled = subData["buy_rebuy_top_off_or_rat_hole"] === null;
	sdButton.innerText = "Stand pat/Discard";
	sdButton.disabled = subData["stand_pat_or_discard"] === null;
	
	if (subData["stand_pat_or_discard"] === null)
		sdCards.value = "";
	else
		sdCards.value = subData["stand_pat_or_discard"].join("");

	sdCards.disabled = subData["stand_pat_or_discard"] === null;
	fButton.innerText = "Fold";
	fButton.disabled = !subData["fold"];

	if (subData["check_or_call"] === null)
		ccButton.innerText = "Check/Call";
	else if (subData["check_or_call"] === 0)
		ccButton.innerText = "Check";
	else
		ccButton.innerText = `Call ${subData["check_or_call"]}`;

	ccButton.disabled = subData["check_or_call"] === null;

	if (subData["post_bring_in"] === null)
		pbButton.innerText = "Bring-in";
	else
		pbButton.innerText = `Bring-in ${subData["post_bring_in"]}`;

	pbButton.disabled = subData["post_bring_in"] === null;

	if (subData["complete_bet_or_raise_to"] === null)
		cbrButton.innerText = "Complete/Bet/Raise to";
	else if (subData["complete_bet_or_raise_to"][0])
		cbrButton.innerText = "Complete";
	else if (subData["complete_bet_or_raise_to"][1])
		cbrButton.innerText = "Raise";
	else
		cbrButton.innerText = "Bet";

	if (subData["complete_bet_or_raise_to"] === null)
		cbrAmount.value = "";
	else
		cbrAmount.value = `${subData["complete_bet_or_raise_to"][2]} - ${subData["complete_bet_or_raise_to"][3]}`;

	cbrButton.disabled = subData["complete_bet_or_raise_to"] === null;
	cbrAmount.disabled = subData["complete_bet_or_raise_to"] === null;
	smButton.innerText = "Show/Muck";
	smCards.value = subData["show_or_muck_hole_cards"] ? "-" : "";
	smButton.disabled = subData["show_or_muck_hole_cards"] === null;
	smCards.disabled = subData["show_or_muck_hole_cards"] === null;
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
const configuration = JSON.parse(document.getElementById("configuration").textContent);
let dataGuard = true;
let data = [JSON.parse(document.getElementById("data").textContent)];
const felt = new Felt(canvas.width, canvas.height, canvas, configuration, getData);
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
	case "data":
		dataGuard = true;

		data.push(...eventData["data"]);
		updateActions();

		break;
	case "message":
		alert(eventData["message"]);

		break;
	}
}
webSocket.onclose = function(event) {
	console.error("Cash game socket closed unexpectedly");
}

setInterval(shifter, configuration["shifter_timeout"] * 1000);
setInterval(watchdog, configuration["watchdog_timeout"] * 1000);
updateActions();
