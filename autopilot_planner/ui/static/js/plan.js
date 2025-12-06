async function loadPlan() {
    try {
        const response = await fetch('/api/plan');
        const data = await response.json();
        const plan = data.plan;
        const container = document.getElementById('plan-container');
        if (plan.length === 0) {
            container.innerHTML = '<div class="col-span-full text-center py-12"><p class="text-gray-500 text-lg">No tasks scheduled yet. <a href="/add" class="text-blue-600 hover:text-blue-800">Add a task</a> to get started.</p></div>';
        } else {
            container.innerHTML = plan.map(item => `
                <div class="bg-white shadow-md rounded-lg p-6 border-l-4 border-blue-500">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-lg font-semibold text-gray-900">${item.task}</h3>
                        <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">${item.start} - ${item.end}</span>
                    </div>
                    <div class="text-sm text-gray-600">
                        <strong>Start:</strong> ${item.start}<br>
                        <strong>End:</strong> ${item.end}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        document.getElementById('plan-container').innerHTML = '<div class="col-span-full text-center text-red-500">Error loading plan</div>';
    }
}

document.getElementById('send-chat-btn').addEventListener('click', async () => {
    const message = document.getElementById('chat-input').value.trim();
    if (!message) return;

    // Clear input
    document.getElementById('chat-input').value = '';

    // Show user message
    const chatOutput = document.getElementById('chat-output');
    chatOutput.innerHTML += `<div class="mb-2"><strong>You:</strong> ${message}</div>`;

    try {
        // Get current tasks
        const tasksResponse = await fetch('/api/tasks');
        const tasksData = await tasksResponse.json();
        const tasks = tasksData.tasks;

        // Send chat request
        const chatResponse = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, tasks: tasks })
        });
        const chatData = await chatResponse.json();
        const reply = chatData.reply;

        // Show AI response
        chatOutput.innerHTML += `<div class="mb-2"><strong>AI:</strong> ${reply}</div>`;

        // Scroll to bottom
        chatOutput.scrollTop = chatOutput.scrollHeight;
    } catch (error) {
        console.error('Error sending chat message:', error);
        chatOutput.innerHTML += `<div class="mb-2 text-red-500"><strong>AI:</strong> Sorry, I couldn't process your request right now.</div>`;
    }
});

// Allow Enter key to send message
document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('send-chat-btn').click();
    }
});

// Load plan on page load
loadPlan();
