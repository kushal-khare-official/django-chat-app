function getOnlineUsers(authToken, user_id) {
    fetch("http://localhost:8000/api/online-users/", {
        headers: {
            Authorization: `Token ${authToken}`
      },
    })
    .then(response => response.json())
    .then(result => {
        result.forEach(user => {
            if(user.id == user_id) return

            const userEl = new DOMParser().parseFromString(
            `<li class="flex items-center space-x-2 mb-2 cursor-pointer"
                onclick="startChat('${authToken}', '${user_id}', '${user.username}')"
            >
                <div class="bg-green-400 w-4 h-4 rounded-full"></div>
                <span class="text-gray-800">${user.username}</span>
            </li>`, 'text/html').body.firstChild;

            document.getElementById('online-users').appendChild(userEl);
        })
    })
    .catch(error => console.log('error', error));
}

function startChat(authToken, user_id, username) {
    fetch("http://localhost:8000/api/chat/start/", {
        method: 'POST',
        headers: {
            Authorization: `Token ${authToken}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "recipient_username": username
        })
    })
    .then(response => response.json())
    .then(result => {
        document.location.href='/chat/' + result.chat_room_id
    })
    .catch(error => console.log('error', error));
}

function openSocket(authToken, user_id, room_id) {
    const socket = new WebSocket(`ws://${window.location.host}/api/chat/send/${room_id}?token=${authToken}`);

    socket.addEventListener('open', (event) => {
        console.log('WebSocket connection opened');
    });

    socket.addEventListener('message', (event) => {
        const message = JSON.parse(event.data);
        handleMessage(message, user_id);
    });

    socket.addEventListener('close', (event) => {
        console.log('WebSocket connection closed');
    });

    document.getElementById('chat-form').addEventListener('submit', (event) => {
        event.preventDefault();
        const chatInput = document.getElementById('chat-input');
        const messageText = chatInput.value.trim();
        if (messageText) {
            sendMessage(socket, user_id, messageText);
            chatInput.value = '';
        }
    });
}

function sendMessage(socket, user_id, message) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ message, user_id }));
    }
}

function handleMessage(message, user_id) {
    const messageElement = new DOMParser().parseFromString(
            `<div class="mb-2 ${message.sender_id == user_id ? 'text-right': ''}">
                <div class="text-sm text-gray-600">
                    ${message.sender}
                </div>
                <div class="bg-${message.sender_id == user_id ? 'green': 'blue'}-500 text-white py-2 px-4 rounded-lg inline-block max-w-[70%]">
                    ${message.text}
                </div>
            </div>`, 'text/html').body.firstChild;
    document.getElementById('chat-messages').appendChild(messageElement);
}

