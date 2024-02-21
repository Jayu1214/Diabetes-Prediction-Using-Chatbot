function sendMessage() {
  var userInput = document.getElementById("user-input").value;
  var chatBox = document.getElementById("chat-box");

  // Display user message
  var userMessage = document.createElement("div");
  userMessage.className = "message user-message";
  userMessage.innerHTML = userInput;
  chatBox.appendChild(userMessage);

  // Send user message to server for processing
  fetch("/process-message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: userInput }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Display bot response
      var botMessage = document.createElement("div");
      botMessage.className = "message bot-message";
      botMessage.innerHTML = data.message;
      chatBox.appendChild(botMessage);
    });

  // Clear input field
  document.getElementById("user-input").value = "";
}
