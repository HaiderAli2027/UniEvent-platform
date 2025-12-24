// 1. Access Control
const user = JSON.parse(localStorage.getItem('user') || '{}');
const allowedRoles = ['admin', 'society'];

if (!user.id || !allowedRoles.includes(user.role)) {
    alert('Access denied. You do not have permission to view this page.');
    window.location.href = '/';
}

// 2. State Management
let dbSocieties = [];

// 3. Initialization Logic (MERGED FIX)
window.onload = () => {
    // Determine which section to show first based on role
    if (user.role === 'society') {
        switchRole('society'); 
    } else {
        showSection('societies'); 
    }
};

// 4. Core Navigation
function switchRole(role) {
    const adminNav = document.getElementById('admin-nav');
    const societyNav = document.getElementById('society-nav');
    const indicator = document.getElementById('role-indicator');

    if (role === 'admin') {
        adminNav.classList.remove('hidden');
        societyNav.classList.add('hidden');
        indicator.className = "w-8 h-8 rounded-full bg-emerald-400 border-2 border-white/20";
        document.getElementById('user-name').innerText = "Admin Panel";
        showSection('societies');
    } else {
        adminNav.classList.add('hidden');
        societyNav.classList.remove('hidden');
        indicator.className = "w-8 h-8 rounded-full bg-indigo-400 border-2 border-white/20";
        document.getElementById('user-name').innerText = user.username || "Verified Society";
        showSection('create-event');
    }
}

function showSection(sectionId) {
    const sections = ['societies-section', 'create-event-section', 'events-section'];
    sections.forEach(s => document.getElementById(s).classList.add('hidden'));
    document.getElementById(sectionId + '-section').classList.remove('hidden');

    const titleMap = {
        'societies': ["Society Management", "Review pending registration requests."],
        'create-event': ["Create New Event", "Input details strictly following the database schema."],
        'events': ["Active Campus Events", "Currently published events for students."]
    };
    document.getElementById('section-title').innerText = titleMap[sectionId][0];
    document.getElementById('section-desc').innerText = titleMap[sectionId][1];

    if (sectionId === 'societies') loadSocieties();
    if (sectionId === 'events') renderEvents();
}

// 5. Society Management (Admin only)
async function loadSocieties() {
    try {
        const response = await fetch('http://localhost:5000/api/societies');
        dbSocieties = await response.json();
        renderSocieties();
    } catch (error) {
        console.error('Error loading societies:', error);
    }
}

function renderSocieties() {
    const list = document.getElementById('society-list');
    if (dbSocieties.length === 0) {
        list.innerHTML = `<tr><td colspan="4" class="py-12 text-center text-slate-400">No societies registered yet</td></tr>`;
        return;
    }
    list.innerHTML = dbSocieties.map(s => `
        <tr class="border-b border-slate-50 hover:bg-slate-50 transition">
            <td class="py-6">
                <div><p class="font-bold text-slate-800">${s.name}</p><p class="text-xs text-slate-400">${s.email || 'No email'}</p></div>
            </td>
            <td class="py-6">${s.member_count} Members</td>
            <td class="py-6"><span class="px-3 py-1 ${s.is_verified ? 'bg-emerald-100 text-emerald-600' : 'bg-yellow-100 text-yellow-600'} rounded-full text-[10px] font-black uppercase">${s.is_verified ? '✓ Verified' : '⏳ Pending'}</span></td>
            <td class="py-6 text-right">
                ${!s.is_verified ? `<button onclick="approve(${s.id})" class="px-5 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-md">Approve</button>` : '<span class="text-slate-300">Approved ✓</span>'}
            </td>
        </tr>`).join('');
}

async function approve(id) {
    if (!confirm('Approve this society?')) return;
    try {
        const response = await fetch(`http://localhost:5000/api/societies/${id}/verify`, { method: 'POST' });
        if (response.ok) { alert('Verified!'); loadSocieties(); }
    } catch (error) { console.error(error); }
}

// 6. Event Management (Society/Admin)
async function renderEvents() {
    const list = document.getElementById('events-section');
    list.innerHTML = '<p class="text-slate-400">Loading events...</p>';
    try {
        const response = await fetch('http://localhost:5000/api/events');
        const events = await response.json();
        if (events.length === 0) {
            list.innerHTML = '<p class="text-slate-400 p-8">No active events found.</p>';
            return;
        }
        list.innerHTML = events.map(e => `
            <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                <div class="flex justify-between items-start">
                    <span class="text-[10px] font-black text-indigo-500 uppercase">${e.category || 'Event'}</span>
                    <span class="text-[10px] font-bold text-slate-400">${e.organizer?.name || ''}</span>
                </div>
                <h4 class="text-xl font-bold text-slate-800 mt-1">${e.title}</h4>
                <p class="text-slate-500 text-sm mt-2 line-clamp-2">${e.short_description || ''}</p>
                <div class="mt-4 pt-4 border-t border-slate-50 flex flex-col gap-1">
                    <p class="text-slate-400 text-xs"><i class="fa-solid fa-location-dot mr-2"></i>${e.venue}</p>
                    <p class="text-slate-400 text-xs"><i class="fa-solid fa-calendar mr-2"></i>${new Date(e.event_date).toLocaleDateString()}</p>
                </div>
            </div>`).join('');
    } catch (error) { list.innerHTML = '<p class="text-red-400">Failed to load events.</p>'; }
}

async function publishEvent() {
    const societyId = user.society?.id;
    if (!societyId) {
        showStatus("Error: Society profile not found.", "red");
        return;
    }

    const formData = new FormData();
    formData.append('society_id', societyId);
    formData.append('title', document.getElementById('db-title').value);
    formData.append('category', document.getElementById('db-category').value);
    formData.append('event_date', document.getElementById('db-date').value);
    formData.append('venue', document.getElementById('db-venue').value);
    formData.append('description', document.getElementById('db-short-desc').value);
    formData.append('short_description', document.getElementById('db-short-desc').value);
    formData.append('google_form_link', document.getElementById('db-form').value);

    try {
        const response = await fetch('http://localhost:5000/api/events', { method: 'POST', body: formData });
        if (response.ok) {
            showStatus("🎉 Event Created Successfully!", "indigo");
            document.querySelectorAll('#create-event-section input, #create-event-section textarea').forEach(i => i.value = "");
            setTimeout(() => showSection('events'), 2000);
        } else {
            const res = await response.json();
            showStatus(res.error || "Creation failed", "red");
        }
    } catch (error) { showStatus("Connection error", "red"); }
}

function showStatus(msg, color) {
    let statusDiv = document.getElementById('status-msg');
    if(!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.id = 'status-msg';
        statusDiv.className = `fixed bottom-10 right-10 px-6 py-3 rounded-2xl text-white font-bold shadow-2xl z-[1000] transition-all`;
        document.body.appendChild(statusDiv);
    }
    statusDiv.style.backgroundColor = color === 'red' ? '#ef4444' : '#4f46e5';
    statusDiv.innerText = msg;
    statusDiv.style.display = 'block';
    setTimeout(() => { statusDiv.style.display = 'none'; }, 4000);
}