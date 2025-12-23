document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('societyForm');
    
    // Label Interaction
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            const label = input.closest('.form-group')?.querySelector('label');
            if(label) label.style.color = '#4f46e5';
        });
        input.addEventListener('blur', () => {
            const label = input.closest('.form-group')?.querySelector('label');
            if(label) label.style.color = '#94a3b8';
        });
    });

    // Handle Submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = form.querySelector('.submit-btn');
        const span = btn.querySelector('span');
        
        span.innerText = "Syncing Core Data...";
        btn.style.pointerEvents = "none";

        setTimeout(() => {
            span.innerText = "Society Registered! ✨";
            btn.style.background = "#059669";
            
            setTimeout(() => {
                alert("Boom! Registration complete. Welcome to the Network.");
                window.location.reload();
            }, 1000);
        }, 1800);
    });
});