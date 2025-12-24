

// document.addEventListener('DOMContentLoaded', () => {
//     const form = document.getElementById('societyForm');
    
//     // Label Interaction
//     const inputs = document.querySelectorAll('.form-input');
//     inputs.forEach(input => {
//         input.addEventListener('focus', () => {
//             const label = input.closest('.form-group')?.querySelector('label');
//             if(label) label.style.color = '#4f46e5';
//         });
//         input.addEventListener('blur', () => {
//             const label = input.closest('.form-group')?.querySelector('label');
//             if(label) label.style.color = '#94a3b8';
//         });
//     });

//     // Handle Submission
//     form.addEventListener('submit', (e) => {
//         e.preventDefault();
//         const btn = form.querySelector('.submit-btn');
//         const span = btn.querySelector('span');
        
//         span.innerText = "Syncing Core Data...";
//         btn.style.pointerEvents = "none";

//         setTimeout(() => {
//             span.innerText = "Society Registered! ✨";
//             btn.style.background = "#059669";
            
//             setTimeout(() => {
//                 alert("Boom! Registration complete. Welcome to the Network.");
//                 window.location.reload();
//             }, 1000);
//         }, 1800);
//     });
// });
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('societyForm');
    
    // Check if user is logged in
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!user.id) {
        alert('Please login first to register a society');
        window.location.href = '/';
        return;
    }
    
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
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = form.querySelector('.submit-btn');
        const span = btn.querySelector('span');
        
        span.innerText = "Syncing Core Data...";
        btn.style.pointerEvents = "none";

        const formData = new FormData(form);
        formData.append('user_id', user.id);
        
        try {
            const response = await fetch('http://localhost:5000/api/societies', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                span.innerText = "Society Registered! ✨";
                btn.style.background = "#059669";
                
                // Update user role to society in localStorage
                user.role = 'society';
                user.society = data.society;
                localStorage.setItem('user', JSON.stringify(user));
                
                setTimeout(() => {
                    alert("Boom! Registration complete. Welcome to the Network.");
                    window.location.href = '/app';
                }, 1500);
            } else {
                span.innerText = "Registration Failed";
                btn.style.background = "#dc2626";
                btn.style.pointerEvents = "auto";
                alert(data.error || 'Registration failed. Please try again.');
                
                setTimeout(() => {
                    span.innerText = "Register Society Now";
                    btn.style.background = "";
                }, 2000);
            }
        } catch (error) {
            span.innerText = "Connection Error";
            btn.style.background = "#dc2626";
            btn.style.pointerEvents = "auto";
            alert('Network error. Please check your connection.');
            
            setTimeout(() => {
                span.innerText = "Register Society Now";
                btn.style.background = "";
            }, 2000);
        }
    });
});