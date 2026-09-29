// Application State
let currentTab = 'tasks';
let allTasks = [];
let allNotes = [];
let searchDebounceTimer = null;
let noteSearchDebounceTimer = null;

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  loadMetrics();
  loadTasks();
  lucide.createIcons();
});

// Toast Notification
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toast-message');
  msgEl.textContent = message;
  toast.classList.add('toast-visible');
  setTimeout(() => {
    toast.classList.remove('toast-visible');
  }, 3000);
}

// Tab Switching
function switchTab(tab) {
  currentTab = tab;
  const tabs = ['tasks', 'notes', 'backup'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-${t}-btn`);
    const content = document.getElementById(`tab-${t}-content`);
    if (t === tab) {
      btn.classList.add('active', 'border-indigo-600', 'text-indigo-600');
      btn.classList.remove('border-transparent', 'text-slate-500');
      content.classList.remove('hidden');
    } else {
      btn.classList.remove('active', 'border-indigo-600', 'text-indigo-600');
      btn.classList.add('border-transparent', 'text-slate-500');
      content.classList.add('hidden');
    }
  });

  if (tab === 'tasks') {
    loadTasks();
  } else if (tab === 'notes') {
    loadNotes();
  }
  loadMetrics();
  lucide.createIcons();
}

// ----------------- METRICS -----------------
async function loadMetrics() {
  try {
    const res = await fetch('/api/metrics');
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('metric-total').textContent = data.total_tasks;
    document.getElementById('metric-pending').textContent = data.pending_tasks;
    document.getElementById('metric-progress').textContent = data.in_progress_tasks;
    document.getElementById('metric-completed').textContent = data.completed_tasks;
    document.getElementById('metric-overdue').textContent = data.overdue_tasks;
    document.getElementById('metric-rate').textContent = `${data.completion_rate_percentage}%`;
  } catch (err) {
    console.error('Failed to load metrics', err);
  }
}

// ----------------- TASKS -----------------
async function loadTasks() {
  const listEl = document.getElementById('tasks-list');
  const search = document.getElementById('task-search').value.trim();
  const status = document.getElementById('filter-status').value;
  const priority = document.getElementById('filter-priority').value;

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (status) params.append('status', status);
  if (priority) params.append('priority', priority);

  try {
    const res = await fetch(`/api/tasks?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    allTasks = await res.json();
    renderTasks(allTasks);
  } catch (err) {
    listEl.innerHTML = `<div class="text-center py-10 text-rose-500 font-medium">Failed to load tasks. Please try again.</div>`;
  }
}

function onSearchInput() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    loadTasks();
  }, 250);
}

function renderTasks(tasks) {
  const listEl = document.getElementById('tasks-list');
  if (tasks.length === 0) {
    listEl.innerHTML = `
      <div class="text-center py-16 bg-white border border-slate-200 rounded-xl space-y-2">
        <div class="w-12 h-12 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <i data-lucide="inbox" class="w-6 h-6"></i>
        </div>
        <p class="text-sm font-semibold text-slate-700">No tasks found</p>
        <p class="text-xs text-slate-400">Create a task or change your search/filter criteria.</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  const todayStr = new Date().toISOString().split('T')[0];

  listEl.innerHTML = tasks.map(task => {
    const isCompleted = task.status === 'COMPLETED';
    const isOverdue = !isCompleted && task.due_date && task.due_date < todayStr;

    // Priority badge styling
    let priorityBadge = '';
    if (task.priority === 'HIGH') {
      priorityBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">High</span>`;
    } else if (task.priority === 'MEDIUM') {
      priorityBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">Medium</span>`;
    } else {
      priorityBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">Low</span>`;
    }

    // Status badge styling
    let statusBadge = '';
    if (task.status === 'COMPLETED') {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">Completed</span>`;
    } else if (task.status === 'IN_PROGRESS') {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">In Progress</span>`;
    } else {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">Pending</span>`;
    }

    // Due date badge
    let dateBadge = '';
    if (task.due_date) {
      dateBadge = isOverdue
        ? `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200"><i data-lucide="alert-circle" class="w-3 h-3"></i> Overdue: ${task.due_date}</span>`
        : `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded"><i data-lucide="calendar" class="w-3 h-3"></i> Due: ${task.due_date}</span>`;
    }

    // Category badge
    const catBadge = task.category 
      ? `<span class="text-[11px] font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">#${escapeHtml(task.category)}</span>`
      : '';

    return `
      <div class="task-card bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-start justify-between gap-3">
        <div class="flex items-start gap-3 flex-1">
          <!-- Toggle completion button -->
          <button onclick="toggleTaskStatus(${task.id})" class="mt-0.5 flex-shrink-0 w-5 h-5 rounded border ${isCompleted ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-300 hover:border-indigo-500'} flex items-center justify-center transition">
            ${isCompleted ? '<i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>' : ''}
          </button>
          
          <div class="space-y-1 flex-1 min-w-0">
            <h4 class="text-sm font-semibold ${isCompleted ? 'line-through text-slate-400' : 'text-slate-800'} break-words">
              ${escapeHtml(task.title)}
            </h4>
            ${task.description ? `<p class="text-xs text-slate-500 line-clamp-2 break-words">${escapeHtml(task.description)}</p>` : ''}
            
            <div class="flex flex-wrap items-center gap-2 pt-1">
              ${statusBadge}
              ${priorityBadge}
              ${dateBadge}
              ${catBadge}
            </div>
          </div>
        </div>

        <div class="flex items-center gap-1 flex-shrink-0">
          <button onclick="openEditTaskModal(${task.id})" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition" title="Edit">
            <i data-lucide="edit-3" class="w-4 h-4"></i>
          </button>
          <button onclick="deleteTask(${task.id})" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition" title="Delete">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

async function toggleTaskStatus(id) {
  try {
    const res = await fetch(`/api/tasks/${id}/toggle`, { method: 'PATCH' });
    if (!res.ok) throw new Error('Toggle failed');
    await loadTasks();
    await loadMetrics();
    showToast('Task status updated');
  } catch (err) {
    showToast('Failed to update task status', 'error');
  }
}

async function deleteTask(id) {
  if (!confirm('Are you sure you want to delete this task?')) return;
  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
    await loadTasks();
    await loadMetrics();
    showToast('Task deleted');
  } catch (err) {
    showToast('Failed to delete task', 'error');
  }
}

// Task Modal Handlers
function openTaskModal() {
  document.getElementById('task-id').value = '';
  document.getElementById('task-form').reset();
  document.getElementById('task-priority-input').value = 'MEDIUM';
  document.getElementById('task-status-input').value = 'PENDING';
  document.getElementById('task-modal-title').textContent = 'Add New Task';
  document.getElementById('task-modal').classList.remove('hidden');
}

function openEditTaskModal(id) {
  const task = allTasks.find(t => t.id === id);
  if (!task) return;
  document.getElementById('task-id').value = task.id;
  document.getElementById('task-title-input').value = task.title;
  document.getElementById('task-desc-input').value = task.description || '';
  document.getElementById('task-priority-input').value = task.priority;
  document.getElementById('task-status-input').value = task.status;
  document.getElementById('task-date-input').value = task.due_date || '';
  document.getElementById('task-category-input').value = task.category || '';
  document.getElementById('task-modal-title').textContent = 'Edit Task';
  document.getElementById('task-modal').classList.remove('hidden');
}

function closeTaskModal() {
  document.getElementById('task-modal').classList.add('hidden');
}

async function submitTaskForm(e) {
  e.preventDefault();
  const id = document.getElementById('task-id').value;
  const payload = {
    title: document.getElementById('task-title-input').value.trim(),
    description: document.getElementById('task-desc-input').value.trim() || null,
    priority: document.getElementById('task-priority-input').value,
    status: document.getElementById('task-status-input').value,
    due_date: document.getElementById('task-date-input').value || null,
    category: document.getElementById('task-category-input').value.trim() || null,
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Failed to save task');
    }

    closeTaskModal();
    await loadTasks();
    await loadMetrics();
    showToast(id ? 'Task updated successfully' : 'Task created successfully');
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// ----------------- NOTES -----------------
async function loadNotes() {
  const gridEl = document.getElementById('notes-grid');
  const search = document.getElementById('note-search').value.trim();

  const params = new URLSearchParams();
  if (search) params.append('search', search);

  try {
    const res = await fetch(`/api/notes?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch notes');
    allNotes = await res.json();
    renderNotes(allNotes);
  } catch (err) {
    gridEl.innerHTML = `<div class="col-span-full text-center py-10 text-rose-500 font-medium">Failed to load notes. Please try again.</div>`;
  }
}

function onNoteSearchInput() {
  clearTimeout(noteSearchDebounceTimer);
  noteSearchDebounceTimer = setTimeout(() => {
    loadNotes();
  }, 250);
}

function renderNotes(notes) {
  const gridEl = document.getElementById('notes-grid');
  if (notes.length === 0) {
    gridEl.innerHTML = `
      <div class="col-span-full text-center py-16 bg-white border border-slate-200 rounded-xl space-y-2">
        <div class="w-12 h-12 mx-auto rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <i data-lucide="file-text" class="w-6 h-6"></i>
        </div>
        <p class="text-sm font-semibold text-slate-700">No notes found</p>
        <p class="text-xs text-slate-400">Click "New Note" to jot down your thoughts or meeting minutes.</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  gridEl.innerHTML = notes.map(note => {
    // Parse tags
    const tagsList = note.tags 
      ? note.tags.split(',').map(t => t.trim()).filter(Boolean)
      : [];

    const tagsHtml = tagsList.map(tag => 
      `<span class="text-[10px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">#${escapeHtml(tag)}</span>`
    ).join(' ');

    const dateStr = new Date(note.updated_at).toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric'
    });

    const taskBadge = note.task_id
      ? `<span class="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded"><i data-lucide="link" class="w-3 h-3"></i> Task #${note.task_id}</span>`
      : '';

    return `
      <div class="note-card bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3">
        <div class="space-y-2">
          <div class="flex items-start justify-between gap-2">
            <h4 class="text-sm font-bold text-slate-900 break-words">${escapeHtml(note.title)}</h4>
            <div class="flex items-center gap-1 flex-shrink-0">
              <button onclick="openEditNoteModal(${note.id})" class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition" title="Edit">
                <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
              </button>
              <button onclick="deleteNote(${note.id})" class="p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition" title="Delete">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
          <p class="text-xs text-slate-600 whitespace-pre-wrap break-words leading-relaxed">${escapeHtml(note.content)}</p>
        </div>

        <div class="pt-3 border-t border-slate-100 space-y-2">
          ${taskBadge ? `<div>${taskBadge}</div>` : ''}
          ${tagsHtml ? `<div class="flex flex-wrap gap-1">${tagsHtml}</div>` : ''}
          <div class="text-[10px] text-slate-400 font-medium text-right">${dateStr}</div>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

async function deleteNote(id) {
  if (!confirm('Are you sure you want to delete this note?')) return;
  try {
    const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Delete failed');
    await loadNotes();
    await loadMetrics();
    showToast('Note deleted');
  } catch (err) {
    showToast('Failed to delete note', 'error');
  }
}

async function populateTaskSelectDropdown(selectedTaskId = null) {
  const selectEl = document.getElementById('note-task-select');
  selectEl.innerHTML = '<option value="">No task linked</option>';

  if (allTasks.length === 0) {
    try {
      const res = await fetch('/api/tasks');
      if (res.ok) allTasks = await res.json();
    } catch (e) {}
  }

  allTasks.forEach(task => {
    const option = document.createElement('option');
    option.value = task.id;
    option.textContent = `#${task.id} - ${task.title}`;
    if (selectedTaskId && Number(selectedTaskId) === task.id) {
      option.selected = true;
    }
    selectEl.appendChild(option);
  });
}

function openNoteModal() {
  document.getElementById('note-id').value = '';
  document.getElementById('note-form').reset();
  populateTaskSelectDropdown();
  document.getElementById('note-modal-title').textContent = 'Add New Note';
  document.getElementById('note-modal').classList.remove('hidden');
}

function openEditNoteModal(id) {
  const note = allNotes.find(n => n.id === id);
  if (!note) return;
  document.getElementById('note-id').value = note.id;
  document.getElementById('note-title-input').value = note.title;
  document.getElementById('note-content-input').value = note.content;
  document.getElementById('note-tags-input').value = note.tags || '';
  populateTaskSelectDropdown(note.task_id);
  document.getElementById('note-modal-title').textContent = 'Edit Note';
  document.getElementById('note-modal').classList.remove('hidden');
}

function closeNoteModal() {
  document.getElementById('note-modal').classList.add('hidden');
}

async function submitNoteForm(e) {
  e.preventDefault();
  const id = document.getElementById('note-id').value;
  const taskIdVal = document.getElementById('note-task-select').value;
  const payload = {
    title: document.getElementById('note-title-input').value.trim(),
    content: document.getElementById('note-content-input').value.trim(),
    tags: document.getElementById('note-tags-input').value.trim() || null,
    task_id: taskIdVal ? Number(taskIdVal) : null,
  };

  try {
    let res;
    if (id) {
      res = await fetch(`/api/notes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Failed to save note');
    }

    closeNoteModal();
    await loadNotes();
    await loadMetrics();
    showToast(id ? 'Note updated successfully' : 'Note created successfully');
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// ----------------- BACKUP / EXPORT / IMPORT -----------------
async function exportBackupData() {
  try {
    const res = await fetch('/api/backup/export');
    if (!res.ok) throw new Error('Export failed');
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `todo-app-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Backup downloaded successfully');
  } catch (err) {
    showToast('Export failed', 'error');
  }
}

async function handleFileImport(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (event) => {
    try {
      const backupJson = JSON.parse(event.target.result);
      const res = await fetch('/api/backup/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(backupJson)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to import backup');
      }

      const result = await res.json();
      showToast(`Imported ${result.imported_tasks} tasks and ${result.imported_notes} notes!`);
      await loadTasks();
      await loadNotes();
      await loadMetrics();
    } catch (err) {
      alert(`Import error: ${err.message}`);
    }
  };
  reader.readAsText(file);
}

// Utilities
function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
