document.getElementById('ai-suggest-btn').addEventListener('click', async () => {
    try {
        // First get current tasks
        const tasksResponse = await fetch('/api/tasks');
        const tasksData = await tasksResponse.json();
        const tasks = tasksData.tasks;

        // Then get AI suggestions
        const suggestionsResponse = await fetch('/api/ai/suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tasks: tasks })
        });
        const suggestionsData = await suggestionsResponse.json();
        const suggestions = suggestionsData.suggestions;

        const suggestionsDiv = document.getElementById('suggestions');
        const suggestionsList = document.getElementById('suggestions-list');

        if (suggestions.length === 0) {
            suggestionsList.innerHTML = '<p class="col-span-full text-center text-gray-500">No suggestions available</p>';
        } else {
            suggestionsList.innerHTML = suggestions.map(suggestion => `
                <div class="bg-white shadow-md rounded-lg p-4 border-l-4 border-purple-500">
                    <h3 class="text-lg font-semibold text-gray-900">${suggestion.title}</h3>
                    <p class="text-sm text-gray-600">Duration: ${suggestion.duration} hours</p>
                </div>
            `).join('');
        }

        suggestionsDiv.classList.remove('hidden');
        if (suggestions.length > 0) {
            document.getElementById('add-all-btn').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error getting AI suggestions:', error);
    }
});

document.getElementById('add-all-btn').addEventListener('click', async () => {
    const suggestionsResponse = await fetch('/api/ai/suggestions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tasks: [] }) // Get suggestions again, or cache them
    });
    const suggestionsData = await suggestionsResponse.json();
    const suggestions = suggestionsData.suggestions;

    let addedCount = 0;
    for (const suggestion of suggestions) {
        try {
            await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(suggestion)
            });
            addedCount++;
        } catch (error) {
            console.error('Error adding suggestion:', error);
        }
    }
    document.getElementById('add-message').textContent = `Added ${addedCount} suggested tasks!`;
    document.getElementById('add-all-btn').classList.add('hidden');
});
