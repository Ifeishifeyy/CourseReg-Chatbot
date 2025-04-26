
document.addEventListener('DOMContentLoaded', function () {

    // DOM Elements
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const toggleChatButton = document.getElementById('toggle-chat');
    const closeChatButton = document.getElementById('close-chat');
    const landingChatButton = document.getElementById('landing-chat-button');
    const heroChatButton = document.getElementById('hero-chat-button');
    const backOneStepBtn = document.getElementById('back-one-step');
    const backToStartBtn = document.getElementById('back-to-start');
    
    if (backOneStepBtn) {
        backOneStepBtn.addEventListener('click', goBackOneStep);
    }
    
    if (backToStartBtn) {
        backToStartBtn.addEventListener('click', goBackToBeginning);
    }

    // State
    const state = {
        isOpen: false,
        isTyping: false,
        userProgram: null,
        userLevel: null,
        userOption: null,
        history: [],
        messages: [
            {
                name: "bot",
                message: "Welcome! I am the Course Registration Advisor Chatbot. Let's start with your academic level."
            },
            {
                type: "buttons",
                buttons: [
                    { label: "100 Level", value: "100" },
                    { label: "200 Level", value: "200" },
                    { label: "300 Level", value: "300" },
                    { label: "400 Level", value: "400" }
                ]
            }
        ]
    };
    
    const programButtons = [
        { label: "Computer Science", value: "computer science" },
        {label: "MIS", value: "mis"},
        { label: "Industrial Mathematics", value: "industrial mathematics" }
    ];
    
    const optionTypeButtons = [
        { label: "Pure", value: "Pure" },
        { label: "Statistics", value: "Statistics" },
        { label: "Computer Science (Maths)", value: "Computer Science" }
    ];
    
    // Initialize chat
    renderMessages();
    
    // Event Listeners
    toggleChatButton.addEventListener('click', openChat);
    closeChatButton.addEventListener('click', closeChat);
    
    if (landingChatButton) {
        landingChatButton.addEventListener('click', openChat);
    }
    
    if (heroChatButton) {
        heroChatButton.addEventListener('click', openChat);
    }
    
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    chatInput.addEventListener('input', function () {
        sendButton.disabled = !chatInput.value.trim();
    });
    
    function openChat() {
        state.isOpen = true;
        chatContainer.classList.remove('hidden');
        toggleChatButton.classList.add('hidden');
        chatInput.focus();
    }
    
    function closeChat() {
        state.isOpen = false;
        chatContainer.classList.add('hidden');
        toggleChatButton.classList.remove('hidden');
    }
    
    function extractProgram(text) {
        const lowerText = text.toLowerCase().trim();
        
        const programKeywords = {
            "industrial mathematics": ["industrial mathematics", "industrial maths", "ind maths", "industrial math", "ind math"],
            "computer science": ["computer science", "cs", "comp science", "comp sci", "computer-science", "comp. sci"],
            "mis":["mis","m.i.s"]
        };
        
        for (const [program, keywords] of Object.entries(programKeywords)) {
            if (keywords.some(keyword => lowerText.includes(keyword))) {
                return program;
            }
        }
        
        return null;
    }
    
    function extractOption(text) {
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes("pure")) {
            return "Pure";
        } else if (lowerText.includes("statistics") || lowerText.includes("stats")) {
            return "Statistics";
        } else if (lowerText.includes("computer science") || lowerText.includes("cs")) {
            return "Computer Science";
        }
        
        return null;
    }
    
    function extractLevel(text) {
        const lowerText = text.toLowerCase();
        const words = lowerText.match(/\b(\d{3})\s*-?\s*(l|lvl|level)?\b/);
        
        if (words) {
            let level = parseInt(words[0]);
            if (level >= 100 && level <= 400) {
                return level.toString();
            }
        }
        if (lowerText.includes("penultimate")) {
            return "300";
        } else if (lowerText.includes("final")) {
            return "400";
        } else if (lowerText.includes("fresher") || lowerText.includes("freshman")) {
            return "100";
        } else if (lowerText.includes("sophomore")) {
            return "200";
        }
        
        return null;
    }
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        addMessage('User', message);
        chatInput.value = '';
        sendButton.disabled = true;
        
        simulateTyping();
        
        const program = extractProgram(message);
        const level = extractLevel(message);
        const option = extractOption(message);
        
        if (program) state.userProgram = program;
        if (level) state.userLevel = level;
        if (option) state.userOption = option;
        
        fetch('/predict', {
            method: 'POST',
            body: JSON.stringify({
                message,
                program: state.userProgram,
                level: state.userLevel,
                option: state.userOption
            }),
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => {
            return res.json();
        })
        .then(data => {
            stopTyping();
            
            if (data.response.includes("Please specify a valid option") && state.userProgram === "industrial mathematics") {
                addMessage('bot', "Please select your Industrial Mathematics option:");
                addMessage(null, null, 'buttons', optionTypeButtons);
            } else {
                addMessage('bot', data.response);
                
                if (state.userLevel && !state.userProgram && !data.response.includes("program")) {
                    setTimeout(() => {
                        addMessage('bot', "Please select your program");
                        addMessage(null, null, 'buttons', programButtons);
                    }, 500);
                }
                
                if (state.userProgram === "industrial mathematics" && !state.userOption && 
                    !data.response.includes("option") && !data.response.includes("Please specify")) {
                    setTimeout(() => {
                        addMessage('bot', "Please select your Industrial Mathematics option:");
                        addMessage(null, null, 'buttons', optionTypeButtons);
                    }, 500);
                }
            }
        })
        .catch(err => {
            stopTyping();
            console.error("Fetch error:", err);
            addMessage('bot', "Oops! Something went wrong connecting to the server.");
        });
    }
    function handleQuickReply(value, label) {
        addMessage('User', label);
        
        if (label.includes("Level")) {
            state.userLevel = value;
            simulateTyping();
            
            setTimeout(() => {
                stopTyping();
                addMessage('bot', "Great! Now, please select your program");
                addMessage(null, null, 'buttons', programButtons);
            }, 1000);
            return;
        }
        
    if (programButtons.find(btn => btn.label === label)) {
        state.userProgram = value.toLowerCase();
        state.userOption = null;
        simulateTyping();
        
        if (value.toLowerCase() === "industrial mathematics") {
            setTimeout(() => {
                stopTyping();
                addMessage('bot', "Nice! You're in Industrial Mathematics. Please select your option:");
                addMessage(null, null, 'buttons', optionTypeButtons);
            }, 1000);
        } else {
            sendOptionToServer(value, label);
        }
        return;
    }

    if (optionTypeButtons.find(btn => btn.label === label)) {
        if (state.userProgram === "industrial mathematics") {
            state.userOption = value;

            sendOptionToServer(value, label);
        }
        return;
    }
        sendOptionToServer(value, label);
    }

    function sendOptionToServer(label) {
        simulateTyping();
        
        const payload = {
            message: `Selected ${label}`,
            program: state.userProgram, 
            level: state.userLevel,
            option: state.userOption
        };

        fetch('/predict', {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            stopTyping();
            addMessage('bot', data.response);
        })
        .catch(err => {
            stopTyping();
            console.error("Error:", err);
            addMessage('bot', "Sorry, I had trouble processing your selection.");
        });
    }
    function addMessage(name, message, type, buttons) {
        state.history.push(JSON.parse(JSON.stringify(state.messages)));
        
        if (type === 'buttons') {
            state.messages.push({ type, buttons });
        } else if (name) {
            state.messages.push({ name, message });
        }
        
        renderMessages();
        scrollToBottom();
    }
    
    function goBackOneStep() {
        if (state.history.length > 0) {
            state.messages = state.history.pop();
            renderMessages();
            scrollToBottom();
        }
    }
    
    function goBackToBeginning() {
        if (state.history.length > 0) {
            state.messages = state.history[0]; 
            state.history = [];
            state.userLevel = null;
            state.userProgram = null;
            state.userOption = null;
            renderMessages();
            scrollToBottom();
        }
    }
    
    function simulateTyping() {
        state.isTyping = true;
        renderMessages();
        scrollToBottom();
    }
    
    function stopTyping() {
        state.isTyping = false;
        renderMessages();
        scrollToBottom();
    }
    
    function renderMessages() {
        chatMessages.innerHTML = '';
        state.messages.forEach((msg, index) => {
            if (msg.type === 'buttons') {
                const buttonWrapper = document.createElement('div');
                buttonWrapper.className = 'quick-replies';
                
                msg.buttons.forEach(btn => {
                    const button = document.createElement('button');
                    button.className = 'quick-reply-button';
                    button.textContent = btn.label;
                    button.addEventListener('click', () => handleQuickReply(btn.value, btn.label));
                    buttonWrapper.appendChild(button);
                });
                
                chatMessages.appendChild(buttonWrapper);
            } else {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.name === 'User' ? 'user-message' : 'bot-message'}`;
                
                if (msg.name !== 'User') {
                    const avatar = document.createElement('div');
                    avatar.className = 'bot-avatar';
                    avatar.innerHTML = `
                   <svg xmlns="http://www.w3.org/2000/svg" id="fi_11189317" data-name="Layer 1" viewBox="0 0 512 512"><path d="M465.448,180.963H457.9a66.766,66.766,0,0,0-66.324-59.844H268V97.032a49.26,49.26,0,1,0-24,0v24.088H120.425A66.766,66.766,0,0,0,54.1,180.963H46.552A43.776,43.776,0,0,0,2.826,224.69V326.733A43.776,43.776,0,0,0,46.552,370.46H54.1a66.767,66.767,0,0,0,66.324,59.845h81.48L245.608,506a12,12,0,0,0,20.785,0l43.7-75.695h81.48A66.767,66.767,0,0,0,457.9,370.46h7.549a43.776,43.776,0,0,0,43.726-43.727V224.69A43.776,43.776,0,0,0,465.448,180.963ZM230.742,49.258A25.259,25.259,0,1,1,256,74.517,25.287,25.287,0,0,1,230.742,49.258ZM26.826,326.733V224.69a19.749,19.749,0,0,1,19.726-19.727h7.2v141.5h-7.2A19.749,19.749,0,0,1,26.826,326.733Zm407.421,36.9a42.721,42.721,0,0,1-42.672,42.673H303.167a12,12,0,0,0-10.392,6L256,476l-36.775-63.695a12,12,0,0,0-10.392-6H120.425a42.721,42.721,0,0,1-42.672-42.673V187.792a42.721,42.721,0,0,1,42.672-42.673h271.15a42.721,42.721,0,0,1,42.672,42.673Zm50.927-36.9a19.749,19.749,0,0,1-19.726,19.727h-7.2v-141.5h7.2a19.749,19.749,0,0,1,19.726,19.727ZM160.038,206.577a41.037,41.037,0,1,0,41.037,41.036A41.083,41.083,0,0,0,160.038,206.577Zm0,58.073a17.037,17.037,0,1,1,17.037-17.037A17.056,17.056,0,0,1,160.038,264.65Zm191.925-58.073A41.037,41.037,0,1,0,393,247.613,41.083,41.083,0,0,0,351.963,206.577Zm0,58.073A17.037,17.037,0,1,1,369,247.613,17.055,17.055,0,0,1,351.963,264.65Zm-31.637,64.28a72.558,72.558,0,0,1-128.652,0,12,12,0,1,1,21.277-11.1,48.557,48.557,0,0,0,86.1,0,12,12,0,1,1,21.277,11.1Z"></path></svg>
                    `;
                    messageDiv.appendChild(avatar);
                }
                
                const content = document.createElement('div');
                content.className = 'message-content';
                content.innerHTML = msg.message.replace(/\n/g, "<br>");
                messageDiv.appendChild(content);
                
                chatMessages.appendChild(messageDiv);
            }
        });
        
        if (state.isTyping) {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            
            const avatar = document.createElement('div');
            avatar.className = 'bot-avatar';
            avatar.innerHTML = `
<svg xmlns="http://www.w3.org/2000/svg" id="fi_11189317" data-name="Layer 1" viewBox="0 0 512 512"><path d="M465.448,180.963H457.9a66.766,66.766,0,0,0-66.324-59.844H268V97.032a49.26,49.26,0,1,0-24,0v24.088H120.425A66.766,66.766,0,0,0,54.1,180.963H46.552A43.776,43.776,0,0,0,2.826,224.69V326.733A43.776,43.776,0,0,0,46.552,370.46H54.1a66.767,66.767,0,0,0,66.324,59.845h81.48L245.608,506a12,12,0,0,0,20.785,0l43.7-75.695h81.48A66.767,66.767,0,0,0,457.9,370.46h7.549a43.776,43.776,0,0,0,43.726-43.727V224.69A43.776,43.776,0,0,0,465.448,180.963ZM230.742,49.258A25.259,25.259,0,1,1,256,74.517,25.287,25.287,0,0,1,230.742,49.258ZM26.826,326.733V224.69a19.749,19.749,0,0,1,19.726-19.727h7.2v141.5h-7.2A19.749,19.749,0,0,1,26.826,326.733Zm407.421,36.9a42.721,42.721,0,0,1-42.672,42.673H303.167a12,12,0,0,0-10.392,6L256,476l-36.775-63.695a12,12,0,0,0-10.392-6H120.425a42.721,42.721,0,0,1-42.672-42.673V187.792a42.721,42.721,0,0,1,42.672-42.673h271.15a42.721,42.721,0,0,1,42.672,42.673Zm50.927-36.9a19.749,19.749,0,0,1-19.726,19.727h-7.2v-141.5h7.2a19.749,19.749,0,0,1,19.726,19.727ZM160.038,206.577a41.037,41.037,0,1,0,41.037,41.036A41.083,41.083,0,0,0,160.038,206.577Zm0,58.073a17.037,17.037,0,1,1,17.037-17.037A17.056,17.056,0,0,1,160.038,264.65Zm191.925-58.073A41.037,41.037,0,1,0,393,247.613,41.083,41.083,0,0,0,351.963,206.577Zm0,58.073A17.037,17.037,0,1,1,369,247.613,17.055,17.055,0,0,1,351.963,264.65Zm-31.637,64.28a72.558,72.558,0,0,1-128.652,0,12,12,0,1,1,21.277-11.1,48.557,48.557,0,0,0,86.1,0,12,12,0,1,1,21.277,11.1Z"></path></svg>
            `;
            typingDiv.appendChild(avatar);
            
            const content = document.createElement('div');
            content.className = 'message-content typing-indicator';
            content.innerHTML = `
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            typingDiv.appendChild(content);
            
            chatMessages.appendChild(typingDiv);
        }

        const navButtons = document.createElement('div');
    navButtons.className = 'chat-nav-buttons';
    navButtons.innerHTML = `
        <button id="back-one-step">Back</button>
        <button id="back-to-start">Restart</button>
    `;
    chatMessages.appendChild(navButtons);
    document.getElementById('back-one-step')?.addEventListener('click', goBackOneStep);
    document.getElementById('back-to-start')?.addEventListener('click', goBackToBeginning);
    
    scrollToBottom();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});