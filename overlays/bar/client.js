// Start ws connection after document is loaded
$(document).ready(function () {

    // Connect if API_Key is inserted
    // Else show an error on the overlay
    if (typeof API_Key === "undefined") {
        $("body").html("No API Key found or load!<br>Rightclick on the script in ChatBot and select \"Insert API Key\"");
        $("body").css({ "font-size": "20px", "color": "#ff8080", "text-align": "center" });
    }
    else {
        connectWebsocket();
    }

});

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {

    //-------------------------------------------
    //  Create WebSocket
    //-------------------------------------------
    var socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");

    //-------------------------------------------
    //  Websocket Event: OnOpen
    //-------------------------------------------
    socket.onopen = function () {

        // AnkhBot Authentication Information
        var auth = {
            author: "EncryptedThoughts",
            website: "twitch.tv/encryptedthoughts",
            api_key: API_Key,
            events: [
                "EVENT_QUEUE_UPDATE",
                "EVENT_QUEUE_STATUS"
            ]
        };

        // Send authentication data to ChatBot ws server
        socket.send(JSON.stringify(auth));
    };

    //-------------------------------------------
    //  Websocket Event: OnMessage
    //-------------------------------------------
    socket.onmessage = function (message) {

        // Parse message
        var socketMessage = JSON.parse(message.data);
        console.log(socketMessage);

        //EVENT_QUEUE_DISPLAY
        if (socketMessage.event === "EVENT_QUEUE_UPDATE") {
            var queueData = JSON.parse(socketMessage.data);
            var total = Object.keys(queueData).length;

            if (total > 0)
                $("#current").html("Current: " + queueData[0].username);     
            if (total > 1)
                $("#next").html("Next: " + queueData[1].username);
            
            $("#total").html("Total: " + total);     
        }

        //EVENT_QUEUE_STATUS
        if (socketMessage.event === "EVENT_QUEUE_STATUS") {
            var statusData = JSON.parse(socketMessage.data);
            $("#status").html("Queue: " + statusData.status);
        }
    };

    //-------------------------------------------
    //  Websocket Event: OnError
    //-------------------------------------------
    socket.onerror = function (error) {
        console.log("Error: " + error);
    };

    //-------------------------------------------
    //  Websocket Event: OnClose
    //-------------------------------------------
    socket.onclose = function () {
        // Clear socket to avoid multiple ws objects and EventHandlings
        socket = null;
        // Try to reconnect every 5s
        setTimeout(function () { connectWebsocket() }, 5000);
    };

}
