async function loadPlan() {
  const res = await fetch('/api/plan');
  const data = await res.json();
  renderPlan(data.plan || []);
}

function renderPlan(plan) {
  const container = document.getElementById('plan-container');
  container.innerHTML = '';
  plan.forEach((item, idx) => {
    const li = document.createElement('li');
    li.className = 'task-card bg-white p-4 shadow rounded mb-4';
    li.innerHTML = `
      <h3 class="text-lg font-semibold"><span class="task-text">${item.text}</span> <span class="category-pill">${item.category}</span></h3>
      <select onchange="changeStatus(${idx}, this.value)">
        <option value="todo" ${item.status === "todo" ? "selected" : ""}>Todo</option>
        <option value="in-progress" ${item.status === "in-progress" ? "selected" : ""}>In Progress</option>
        <option value="done" ${item.status === "done" ? "selected" : ""}>Done</option>
      </select>
      <select onchange="changeCategory(${idx}, this.value)">
        <option value="general" ${item.category === "general" ? "selected" : ""}>General</option>
        <option value="work" ${item.category === "work" ? "selected" : ""}>Work</option>
        <option value="college" ${item.category === "college" ? "selected" : ""}>College</option>
        <option value="personal" ${item.category === "personal" ? "selected" : ""}>Personal</option>
      </select>
      <p><strong>Start:</strong> ${item.start} &nbsp; <strong>End:</strong> ${item.end}</p>
      <input type="date" value="${item.due || ''}" onchange="changeDue(${idx}, this.value)">
      <ul class="subtask-list">
        ${item.subtasks.map((s, i) => `
          <li>
             <input type="checkbox" ${s.done ? "checked" : ""} onchange="toggleSubtask(${idx}, ${i})">
             <span class="${s.done ? 'sub-done' : ''}">${s.text}</span>
             <button onclick="deleteSubtask(${idx}, ${i})">X</button>
          </li>
        `).join("")}
      </ul>
      <input type="text" id="subtask-input-${idx}" placeholder="Add subtask...">
      <button onclick="addSubtask(${idx})">Add</button>
      <button onclick="editTask(${idx})">Edit</button>
      <button class="delete-btn bg-red-500 hover:bg-red-600 text-white px-4 py-1 rounded mt-2" data-idx="${idx}">
        Delete
      </button>
    `;
    container.appendChild(li);
  });

  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async e => {
      const idx = e.target.dataset.idx;
      const res = await fetch(`/api/tasks/${idx}`, { method: 'DELETE' });
      const json = await res.json();
      if (res.ok) {
        loadPlan();
      } else {
        alert("Failed to delete task: " + (json.error || "Unknown error"));
      }
    });
  });
}

async function addAllSuggestions(suggestions) {
  if (!suggestions || !suggestions.length) return;
  let added = 0;
  for (const s of suggestions) {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(s)
    });
    if (res.ok) added++;
  }
  alert(`${added} tasks added.`);
  loadPlan();
}

function editTask(index) {
    const li = document.querySelector(`#plan-container li:nth-child(${index + 1})`);
    const span = li.querySelector(".task-text");
    const oldText = span.textContent;

    span.innerHTML = `<input id="edit-input-${index}" value="${oldText}">`;
    li.innerHTML += `<button onclick="saveEdit(${index})">Save</button>`;
}

async function changeStatus(index, newStatus) {
    await fetch(`/api/tasks/${index}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
    });
    loadPlan();
}

async function changeCategory(index, newCategory) {
    await fetch(`/api/tasks/${index}/category`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: newCategory })
    });
    loadPlan();
}

async function changeDue(index, newDate) {
    await fetch(`/api/tasks/${index}/due`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ due: newDate || null })
    });
    loadPlan();
}

async function addSubtask(index) {
    const input = document.querySelector(`#subtask-input-${index}`);
    const value = input.value.trim();
    if (!value) return;

    await fetch(`/api/tasks/${index}/subtasks/add`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value })
    });

    input.value = "";
    loadPlan();
}

async function toggleSubtask(index, subIndex) {
    await fetch(`/api/tasks/${index}/subtasks/${subIndex}/toggle`, {
        method: "PATCH"
    });
    loadPlan();
}

async function deleteSubtask(index, subIndex) {
    await fetch(`/api/tasks/${index}/subtasks/${subIndex}`, {
        method: "DELETE"
    });
    loadPlan();
}

async function saveEdit(index) {
    const newText = document.querySelector(`#edit-input-${index}`).value;

    await fetch(`/api/tasks/${index}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: newText })
    });

    loadPlan();
}

document.addEventListener('DOMContentLoaded', () => {
  loadPlan();
});
