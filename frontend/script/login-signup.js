document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const dynamicFields = document.getElementById('dynamicFields');
    const signUpForm = document.getElementById('signUpForm');
    const signInForm = document.getElementById('signInForm');
    const allInputs = document.querySelectorAll('input');

    let isFieldSelected = false;

    // --- 3D MOVING EFFECT ---
    document.addEventListener('mousemove', (e) => {
        if (isFieldSelected) {
            container.style.transform = `rotateX(0deg) rotateY(0deg)`;
            return;
        }
        const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
        container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    });

    // --- STATIC ON FOCUS ---
    allInputs.forEach(input => {
        input.addEventListener('focus', () => isFieldSelected = true);
        input.addEventListener('blur', () => isFieldSelected = false);
    });

    const resetForms = () => {
        signUpForm.reset();
        signInForm.reset();
        document.getElementById('passwordRecommendations').innerHTML = '';
        dynamicFields.innerHTML = `
            <div class="input-group">
                <input type="text" placeholder="Society Name" id="extraField" required />
            </div>`;
    };

    signUpButton.addEventListener('click', () => {
        resetForms();
        container.classList.add('right-panel-active');
    });

    signInButton.addEventListener('click', () => {
        resetForms();
        container.classList.remove('right-panel-active');
    });

    // --- UPDATED: URL MODE DETECTION ---
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');

    if (mode === 'signup') {
        // 1. Temporarily disable transitions so it doesn't "slide" while the page is white
        container.style.transition = 'none'; 
        container.classList.add('right-panel-active');
        
        // 2. Force a repaint, then turn transitions back on for future clicks
        setTimeout(() => {
            container.style.transition = ''; 
        }, 100);
    } else {
        // Login is the default, so we do nothing (it opens direct)
        container.classList.remove('right-panel-active');
    }

    roleRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'admin') {
                dynamicFields.innerHTML = ''; 
            } else {
                dynamicFields.innerHTML = `
                    <div class="input-group">
                        <input type="text" placeholder="Society Name" id="extraField" required />
                    </div>`;
            }
        });
    });

    document.querySelectorAll('.password-toggle').forEach(eye => {
        eye.addEventListener('click', () => {
            const input = document.getElementById(eye.dataset.target);
            input.type = input.type === 'password' ? 'text' : 'password';
            eye.classList.toggle('fa-eye-slash');
        });
    });

    const handleFormSubmit = (e, msg) => {
        e.preventDefault();
        const btn = e.target.querySelector('.fill-button');
        btn.classList.add('loading');
        setTimeout(() => {
            btn.classList.remove('loading');
            alert(msg);
        }, 1200);
    };

    signUpForm.addEventListener('submit', (e) => handleFormSubmit(e, 'Account Created!'));
    signInForm.addEventListener('submit', (e) => handleFormSubmit(e, 'Signed In!'));

    const signUpPassword = document.getElementById('signUpPassword');
    const recommendations = document.getElementById('passwordRecommendations');
    signUpPassword.addEventListener('input', () => {
        const val = signUpPassword.value;
        const criteria = [
            { label: '8+ Chars', test: val.length >= 8 },
            { label: 'Upper', test: /[A-Z]/.test(val) },
            { label: 'Num', test: /[0-9]/.test(val) }
        ];
        recommendations.innerHTML = criteria.map(c => 
            `<div class="${c.test ? 'fulfilled' : ''}">${c.test ? '✓' : '○'} ${c.label}</div>`
        ).join('');
    });
});