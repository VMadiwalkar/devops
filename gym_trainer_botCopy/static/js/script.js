document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatArea = document.getElementById('chat-area');
    const fileInput = document.getElementById('file-input');
    const fileCount = document.getElementById('file-count');
    const filePreviewArea = document.getElementById('file-preview-area');

    // Handle File Selection
    fileInput.addEventListener('change', () => {
        const files = fileInput.files;
        if (files.length > 0) {
            fileCount.textContent = files.length;
            fileCount.classList.remove('hidden');

            // Show previews
            filePreviewArea.innerHTML = '';
            Array.from(files).forEach(file => {
                const tag = document.createElement('div');
                tag.className = 'file-tag';
                tag.innerHTML = `<i class="fa-solid fa-file"></i> ${file.name}`;
                filePreviewArea.appendChild(tag);
            });
        } else {
            fileCount.classList.add('hidden');
            filePreviewArea.innerHTML = '';
        }
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        const files = fileInput.files;

        if (!message && files.length === 0) return;

        // 1. Add User Message to Chat
        if (message) {
            appendMessage('user', message);
        }
        if (files.length > 0) {
            appendMessage('user', `Uploaded ${files.length} file(s).`);
        }

        userInput.value = '';

        // Loader for Bot
        const loaderId = appendLoader();

        // 2. Prepare Data
        const formData = new FormData();
        formData.append('message', message);
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Remove loader
            document.getElementById(loaderId).remove();

            // 3. Add Bot Response
            if (data.response) {
                appendMessage('bot', data.response);
            } else if (data.error) {
                appendMessage('bot', `Error: ${data.error}`);
            }

        } catch (error) {
            document.getElementById(loaderId).remove();
            appendMessage('bot', 'Sorry, I lost connection to the server.');
        }

        // Reset Files
        fileInput.value = '';
        fileCount.classList.add('hidden');
        filePreviewArea.innerHTML = '';

        scrollToBottom();
    });

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}-message`;

        const avatar = role === 'bot' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';

        // Simple Markdown parsing for bold text
        const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');

        msgDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="content">${formattedText}</div>
        `;

        chatArea.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendLoader() {
        const id = 'loader-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message bot-message`;
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="content"><i class="fa-solid fa-circle-notch fa-spin"></i> Thinking...</div>
        `;
        chatArea.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }
});
