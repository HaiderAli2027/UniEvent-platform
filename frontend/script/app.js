/**
 * UNIEVENT - Main Application Logic
 * Combined Shashky, Interactive Cards, and Database-Aligned Filters
 */

// --- 1. Typing Effect (Hero Section) ---
function typeWriter(text, elementId, speed, callback) {
    let i = 0;
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Clear previous text if starting fresh
    if (i === 0) element.innerHTML = ""; 

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        } else if (callback) {
            callback();
        }
    }
    type();
}

// Start Hero Sequence on Load
window.addEventListener('load', () => {
    typeWriter("Every Event.", "typing-text", 80, () => {
        typeWriter("One Platform.", "typing-gradient", 80, () => {
            const grad = document.getElementById('typing-gradient');
            if (grad) grad.classList.remove('cursor-active');
        });
    });
});

// --- 2. Parallax Shashky ---
function handleParallax(e) {
    const items = document.querySelectorAll('.parallax-item');
    items.forEach(item => {
        const speed = item.getAttribute('data-speed');
        const x = (window.innerWidth - e.pageX * speed) / 100;
        const y = (window.innerHeight - e.pageY * speed) / 100;
        item.style.transform = `translateX(${x}px) translateY(${y}px)`;
    });
}

// --- 3. Flip Card Handler ---
function flip(button) {
    // Targets the inner container for the 3D flip effect
    const cardInner = button.closest('.flip-card-inner');
    if (cardInner.style.transform === 'rotateY(180deg)') {
        cardInner.style.transform = 'rotateY(0deg)';
    } else {
        cardInner.style.transform = 'rotateY(180deg)';
    }
}
// --- 4. Combined Search & Category Filter ---
function runFilters() {
    // 1. Get values from both inputs
    const searchInput = document.getElementById('eventSearch').value.toLowerCase();
    const categorySelect = document.getElementById('filterCategory').value;
    
    // 2. Target only the upcoming event cards
    const cards = document.querySelectorAll('#eventGrid .flip-card');

    cards.forEach(card => {
        // Get text from the front of the card (Title + Society Name)
        const cardText = card.querySelector('.flip-card-front').innerText.toLowerCase();
        const cardCategory = card.getAttribute('data-category');

        // Check if card matches search AND matches category
        const matchesSearch = cardText.includes(searchInput);
        const matchesCategory = (categorySelect === 'all' || cardCategory === categorySelect);

        // 3. Show/Hide based on both conditions
        if (matchesSearch && matchesCategory) {
            card.style.display = 'block';
            // Optional: Add a small fade-in animation
            card.style.opacity = '1';
        } else {
            card.style.display = 'none';
            card.style.opacity = '0';
        }
    });
    
    // Check if no results found to show a message (Optional)
    toggleNoResults(cards);
}

// Attach the listener to the search input in the NAV
document.getElementById('eventSearch').addEventListener('input', runFilters);

// Helper for "No Results" visual feedback
function toggleNoResults(cards) {
    const visibleCards = Array.from(cards).filter(c => c.style.display !== 'none');
    let msg = document.getElementById('no-results-msg');
    
    if (visibleCards.length === 0) {
        if (!msg) {
            msg = document.createElement('p');
            msg.id = 'no-results-msg';
            msg.className = 'text-center text-slate-400 py-10 col-span-full font-bold';
            msg.innerText = "No events match your search...";
            document.getElementById('eventGrid').appendChild(msg);
        }
    } else if (msg) {
        msg.remove();
    }
}

// --- 5. Interest Toggle (Star & Status Label) ---
function toggleInterest(button, eventId) {
    const container = button.closest('.flip-card-back');
    const statusLabel = container.querySelector('.status-label');
    
    // Toggle active state
    const isInterested = button.classList.toggle('is-active');
    
    if (isInterested) {
        // UI Update to "Going"
        button.classList.remove('bg-white/10');
        button.classList.add('bg-pink-500', 'text-white');
        
        statusLabel.innerText = 'Going';
        statusLabel.classList.remove('bg-white/20');
        statusLabel.classList.add('bg-pink-500/40');
        
        console.log(`Database sync: Event ${eventId} status -> Interested`);
    } else {
        // UI Update back to "Interested"
        button.classList.add('bg-white/10');
        button.classList.remove('bg-pink-500', 'text-white');
        
        statusLabel.innerText = 'Interested';
        statusLabel.classList.add('bg-white/20');
        statusLabel.classList.remove('bg-pink-500/40');
        
        console.log(`Database sync: Event ${eventId} status -> Default`);
    }
}

// --- 6. Modal Toggle ---
function toggleModal(id) {
    const modal = document.getElementById(id);
    if (modal.classList.contains('hidden')) {
        modal.classList.remove('hidden');
        // Small timeout to allow 'hidden' to vanish before starting opacity transition
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            modal.classList.add('opacity-100');
        }, 10);
    } else {
        modal.classList.remove('opacity-100');
        modal.classList.add('opacity-0');
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300); // Matches the duration-300 class
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('container');
    
    // 1. Get the mode from the URL (e.g., ?mode=signup)
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');

    // 2. If the mode is signup, slide to the signup side immediately
    if (mode === 'signup') {
        container.classList.add("right-panel-active");
    } else {
        // Default or 'login' mode
        container.classList.remove("right-panel-active");
    }
});