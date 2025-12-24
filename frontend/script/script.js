// script.js


document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    // 1. 3D Card Effect
    let isFieldSelected = false;
    document.addEventListener('mousemove', (e) => {
        if (isFieldSelected) return;
        const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
        container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    });

    // Inputs focus pe 3D effect rokna
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', () => isFieldSelected = true);
        input.addEventListener('blur', () => isFieldSelected = false);
    });

    // 2. Sliding Animation
    signUpButton.addEventListener('click', () => container.classList.add('right-panel-active'));
    signInButton.addEventListener('click', () => container.classList.remove('right-panel-active'));

    // 3. Login Logic (Backend Connection)
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = loginForm.querySelector('.fill-button');
        const formData = new FormData(loginForm);
        
        btn.classList.add('loading');
        
        try {
            const response = await fetch('http://localhost:5000/api/login', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('user', JSON.stringify(data.user));
                setTimeout(() => { window.location.href = '/app'; }, 1000);
            } else {
                alert(data.error || 'Login Error');
                btn.classList.remove('loading');
            }
        } catch (error) {
            alert('Connection to server failed');
            btn.classList.remove('loading');
        }
    });

    // 4. Signup Logic (Backend Connection)
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = signupForm.querySelector('.fill-button');
        const formData = new FormData(signupForm);
        btn.classList.add('loading');

        try {
            const response = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                alert('Account Created!');
                window.location.href = '/app';
            } else {
                const data = await response.json();
                alert(data.error || 'Registration failed');
                btn.classList.remove('loading');
            }
        } catch (error) {
            alert('Connection error');
            btn.classList.remove('loading');
        }
    });
});

document.querySelectorAll('.password-toggle').forEach(eye => {
    eye.addEventListener('click', () => {
        const input = document.getElementById(eye.dataset.target);
        if (input.type === 'password') {
            input.type = 'text';
            eye.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
            input.type = 'password';
            eye.classList.replace('fa-eye-slash', 'fa-eye');
        }
    });
});