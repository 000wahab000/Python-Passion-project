document.getElementById('add-task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        title: formData.get('title'),
        duration: parseInt(formData.get('duration'))
    };

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        document.getElementById('message').textContent = result.status === 'ok' ? 'Task added successfully!' : 'Error adding task';
    } catch (error) {
        document.getElementById('message').textContent = 'Error adding task';
    }
});
