// Data Mockup based on your Schema
let dbSocieties = [
{ id: 1, name: "Debating Society", member_count: 45, is_active: false },
{ id: 2, name: "Tech Society", member_count: 120, is_active: true }
];

let dbEvents = [
{ title: "The Great Showdown", venue: "Multipurpose Hall", date: "2025-10-30", category: "Debating" }
];

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
    document.getElementById('user-name').innerText = "Verified Society";
    showSection('create-event');
}
}

function showSection(sectionId) {
const sections = ['societies-section', 'create-event-section', 'events-section'];
sections.forEach(s => document.getElementById(s).classList.add('hidden'));
document.getElementById(sectionId + '-section').classList.remove('hidden');

// Update Header
const titleMap = {
    'societies': ["Society Management", "Review pending registration requests."],
    'create-event': ["Create New Event", "Input details strictly following the database schema."],
    'events': ["Active Campus Events", "Currently published events for students."]
};
document.getElementById('section-title').innerText = titleMap[sectionId][0];
document.getElementById('section-desc').innerText = titleMap[sectionId][1];

if(sectionId === 'societies') renderSocieties();
if(sectionId === 'events') renderEvents();
}

function renderSocieties() {
const list = document.getElementById('society-list');
list.innerHTML = dbSocieties.map(s => `
    <tr class="border-b border-slate-50 hover:bg-slate-50 transition">
        <td class="py-6 font-bold text-slate-800">${s.name}</td>
        <td class="py-6">${s.member_count} Members</td>
        <td class="py-6"><span class="px-3 py-1 ${s.is_active ? 'bg-indigo-100 text-indigo-600' : 'bg-yellow-100 text-yellow-600'} rounded-full text-[10px] font-black uppercase">${s.is_active ? 'Active' : 'Pending'}</span></td>
        <td class="py-6 text-right">
            ${!s.is_active ? `<button onclick="approve(${s.id})" class="px-5 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold shadow-md">Approve</button>` : '<span class="text-slate-300">Verified</span>'}
        </td>
    </tr>
`).join('');
}

function approve(id) {
dbSocieties = dbSocieties.map(s => s.id === id ? {...s, is_active: true} : s);
renderSocieties();
}

function renderEvents() {
const list = document.getElementById('events-section');
list.innerHTML = dbEvents.map(e => `
    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <span class="text-[10px] font-black text-indigo-500 uppercase">${e.category}</span>
        <h4 class="text-xl font-bold text-slate-800 mt-1">${e.title}</h4>
        <p class="text-slate-400 text-sm mt-2"><i class="fa-solid fa-location-dot mr-2"></i>${e.venue}</p>
        <p class="text-slate-400 text-sm"><i class="fa-solid fa-calendar mr-2"></i>${e.date}</p>
    </div>
`).join('');
}

function publishEvent() {
const newEvent = {
    title: document.getElementById('db-title').value,
    venue: document.getElementById('db-venue').value,
    date: document.getElementById('db-date').value,
    category: document.getElementById('db-category').value
};
if(!newEvent.title) return alert("Title is required");
dbEvents.push(newEvent);
alert("Event saved to database schema logic!");
showSection('events');
}

window.onload = () => showSection('societies');