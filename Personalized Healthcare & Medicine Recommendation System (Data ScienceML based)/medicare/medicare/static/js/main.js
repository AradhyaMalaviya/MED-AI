// ==========================================
// GLOBALS & COMMON LOGIC
// ==========================================
const API_URL = '/predict';

// Intersection Observer for scroll animations
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
    
    // Hamburger menu logic
    const hamburger = document.querySelector(".hamburger");
    const navMenu = document.querySelector(".nav-links");
    
    if (hamburger && navMenu) {
        hamburger.addEventListener("click", () => {
            const isOpen = navMenu.classList.toggle("active");
            hamburger.setAttribute("aria-expanded", String(isOpen));
        });
        
        navMenu.querySelectorAll("a").forEach((link) =>
            link.addEventListener("click", () => navMenu.classList.remove("active"))
        );
    }
});

// Toast Helper
function showToast(toastId, hideAfter = 4000) {
    const toast = document.getElementById(toastId);
    if (!toast) return;
    toast.classList.add('show');
    if (hideAfter > 0) {
        setTimeout(() => toast.classList.remove('show'), hideAfter);
    }
}

// ==========================================
// INDEX.HTML (Diagnosis Form) LOGIC
// ==========================================
const diagnosisState = {
    symptoms: { fever: 0, cough: 0, fatigue: 0, breathing: 0 },
    model: 'rf'
};

function toggleSymptom(symptom, el) {
    diagnosisState.symptoms[symptom] = diagnosisState.symptoms[symptom] === 1 ? 0 : 1;
    el.classList.toggle('selected');
}

function selectModel(model, el) {
    diagnosisState.model = model;
    document.querySelectorAll('.model-card').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
}

// Ripple effect on predict button
const predictBtn = document.getElementById('predictBtn');
if (predictBtn) {
    predictBtn.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute; left: ${x}px; top: ${y}px;
            width: 0; height: 0; border-radius: 50%;
            background: rgba(255,255,255,0.4);
            transform: translate(-50%, -50%);
            animation: ripple 0.6s ease-out; pointer-events: none;
        `;
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
        
        predict();
    });
}

const ageInput = document.getElementById('age');
if (ageInput) {
    ageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') predict();
    });
}

function showErrorToast(msg) {
    const toastMsg = document.getElementById('errorMsg');
    if (toastMsg) toastMsg.innerText = msg;
    showToast('errorToast', 5000);
}

async function predict() {
    const ageEl = document.getElementById('age');
    if (!ageEl) return;
    
    let age = parseInt(ageEl.value);
    if (isNaN(age) || age < 1 || age > 120) {
        ageEl.focus();
        showErrorToast("Please enter a valid age between 1 and 120");
        return;
    }

    const errorToast = document.getElementById('errorToast');
    if(errorToast) errorToast.classList.remove('show');
    
    document.getElementById('formSection').style.display = 'none';
    document.getElementById('results').style.display = 'none';
    
    const loadingState = document.getElementById('loadingState');
    loadingState.style.display = 'block';

    const loadingText = document.getElementById('loadingText');
    const texts = ["Analyzing symptoms...", "Running AI models...", "Generating recommendations..."];
    let tIdx = 0;
    const tInterval = setInterval(() => {
        tIdx = (tIdx + 1) % texts.length;
        if(loadingText) loadingText.innerText = texts[tIdx];
    }, 800);

    const payload = {
        fever: diagnosisState.symptoms.fever,
        cough: diagnosisState.symptoms.cough,
        fatigue: diagnosisState.symptoms.fatigue,
        breathing: diagnosisState.symptoms.breathing,
        age: age,
        gender: parseInt(document.getElementById('gender').value),
        bloodPressure: parseInt(document.getElementById('bloodPressure').value),
        cholesterol: parseInt(document.getElementById('cholesterol').value),
        model: diagnosisState.model
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();
        if (data.success) {
            clearInterval(tInterval);
            loadingState.style.display = 'none';
            renderResults(data);
        } else {
            throw new Error(data.message || "Prediction failed");
        }
    } catch (err) {
        console.error(err);
        clearInterval(tInterval);
        loadingState.style.display = 'none';
        showErrorToast("Could not connect to AI service. Using Demo Mode.");
        
        const mockData = getMockPrediction(payload);
        renderResults(mockData);
    }
}

function renderResults(data) {
    const resultsDiv = document.getElementById('results');
    if(!resultsDiv) return;
    
    resultsDiv.style.display = 'block';
    
    const riskEmoji = data.risk === 'high' ? '🔴' : data.risk === 'medium' ? '🟡' : '🟢';
    const riskClass = `risk-${data.risk}`;

    const top5HTML = data.top5.map((item, i) => `
        <div class="diff-item">
            <div class="diff-name">${i+1}. ${item.disease}</div>
            <div class="diff-bar-container">
                <div class="diff-bar" style="width: 0%" data-width="${item.confidence}%"></div>
            </div>
            <div class="diff-pct">${item.confidence}%</div>
        </div>
    `).join('');

    const medsHTML = data.medicines.map(m => `<li><span>💊</span> <span>${m}</span></li>`).join('');
    const adviceHTML = data.advice.map(a => `<li><span>💡</span> <span>${a}</span></li>`).join('');

    const modelName = data.model_used === 'rf' ? 'Random Forest' : data.model_used === 'gb' ? 'Gradient Boosting' : 'Logistic Regression';

    resultsDiv.innerHTML = `
        <div style="margin-bottom: 2rem;">
            <button onclick="resetForm()" style="background:none; border:none; color:var(--primary-400); cursor:pointer; font-weight:600; font-size:1rem;">← New Diagnosis</button>
        </div>

        <div class="primary-diagnosis">
            <div class="diagnosis-info">
                <div style="color: var(--neutral-300); margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:1px; font-size:0.85rem;">AI Diagnosis Result</div>
                <h2>${data.disease}</h2>
                <div class="risk-badge ${riskClass}">${riskEmoji} ${data.risk.toUpperCase()} RISK</div>
            </div>
            <div class="confidence-meter">
                <div class="confidence-circle" id="confCircle" style="background: conic-gradient(var(--accent-400) 0%, rgba(255,255,255,0.1) 0%);">
                    <span class="confidence-value">${data.confidence}%</span>
                </div>
                <div style="color:var(--neutral-300); font-size:0.9rem;">Confidence</div>
            </div>
        </div>

        <h3 class="section-title">📊 Differential Diagnosis</h3>
        <div class="diff-diagnosis">
            ${top5HTML}
        </div>

        <h3 class="section-title">🩺 Treatment Plan</h3>
        <div class="treatment-grid">
            <div class="treatment-card">
                <h4 style="color:white; margin-bottom:1rem; font-size:1.2rem;">Recommended Medicines</h4>
                <ul class="treatment-list">${medsHTML}</ul>
            </div>
            <div class="treatment-card">
                <h4 style="color:white; margin-bottom:1rem; font-size:1.2rem;">Medical Advice</h4>
                <ul class="treatment-list">${adviceHTML}</ul>
            </div>
        </div>

        <div class="info-cards">
            <div class="info-card">
                <div style="font-size:2rem; margin-bottom:0.5rem;">⏱️</div>
                <h4>Recovery Time</h4>
                <p>Typically 7-14 days</p>
            </div>
            <div class="info-card">
                <div style="font-size:2rem; margin-bottom:0.5rem;">👨‍⚕️</div>
                <h4>Follow-Up</h4>
                <p>Consult if worse</p>
            </div>
            <div class="info-card">
                <div style="font-size:2rem; margin-bottom:0.5rem;">📞</div>
                <h4>Emergency</h4>
                <p>Call 911 for severe symptoms</p>
            </div>
        </div>

        <div class="model-footer">
            Model: ${modelName} | Analysis Time: ${new Date().toLocaleTimeString()}
        </div>
    `;

    setTimeout(() => {
        const confCircle = document.getElementById('confCircle');
        if(confCircle) {
            confCircle.style.background = `conic-gradient(var(--accent-400) ${data.confidence}%, rgba(255,255,255,0.1) 0%)`;
        }
        document.querySelectorAll('.diff-bar').forEach(bar => {
            bar.style.width = bar.getAttribute('data-width');
        });
    }, 100);

    const diagSection = document.getElementById('diagnosis');
    if(diagSection) diagSection.scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('formSection').style.display = 'block';
    document.getElementById('diagnosis').scrollIntoView({ behavior: 'smooth' });
}

function getMockPrediction(payload) {
    let disease = 'Common Cold';
    let confidence = 75 + Math.random() * 15;
    let risk = 'low';
    const symCount = payload.fever + payload.cough + payload.fatigue + payload.breathing;

    if (payload.fever && payload.cough && payload.breathing) {
        disease = 'Pneumonia'; confidence = 85 + Math.random() * 10; risk = payload.age > 60 ? 'high' : 'medium';
    } else if (payload.cough && payload.breathing) {
        disease = 'Asthma'; confidence = 82 + Math.random() * 12; risk = 'medium';
    } else if (symCount >= 2) {
        disease = 'Influenza'; confidence = 78 + Math.random() * 15; risk = payload.age > 60 ? 'medium' : 'low';
    }

    return {
        success: true, disease, confidence: Number(confidence.toFixed(2)), risk, model_used: payload.model,
        top5: [
            { disease, confidence: Number(confidence.toFixed(2)) },
            { disease: 'Bronchitis', confidence: Number((confidence - 10).toFixed(2)) },
            { disease: 'Common Cold', confidence: Number((confidence - 20).toFixed(2)) },
            { disease: 'Sinusitis', confidence: Number((confidence - 25).toFixed(2)) },
            { disease: 'Allergic Rhinitis', confidence: Number((confidence - 30).toFixed(2)) }
        ],
        medicines: [
            'Acetaminophen 500mg - Every 6 hours',
            'Pseudoephedrine 30mg - Every 6 hours',
            'Vitamin C 1000mg - Once daily'
        ],
        advice: [
            'REST: Get 8-10 hours of sleep per night',
            'HYDRATION: Drink at least 8-10 glasses of water daily',
            'MONITOR: Check temperature twice daily'
        ]
    };
}

// ==========================================
// CONTACT.HTML LOGIC
// ==========================================
const contactForm = document.getElementById('contactForm');
if (contactForm) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');

    function showFieldError(inputId, errorId) {
        document.getElementById(inputId).style.borderColor = 'var(--danger)';
        document.getElementById(errorId).style.display = 'block';
    }

    function hideFieldError(inputId, errorId) {
        document.getElementById(inputId).style.borderColor = '';
        document.getElementById(errorId).style.display = 'none';
    }

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;

        const name = document.getElementById('name').value.trim();
        if (!name) { showFieldError('name', 'nameError'); isValid = false; }
        else { hideFieldError('name', 'nameError'); }

        const email = document.getElementById('email').value.trim();
        if (!email || !validateEmail(email)) { showFieldError('email', 'emailError'); isValid = false; }
        else { hideFieldError('email', 'emailError'); }

        const subject = document.getElementById('subject').value;
        if (!subject) { showFieldError('subject', 'subjectError'); isValid = false; }
        else { hideFieldError('subject', 'subjectError'); }

        const message = document.getElementById('message').value.trim();
        if (!message) { showFieldError('message', 'messageError'); isValid = false; }
        else { hideFieldError('message', 'messageError'); }

        if (isValid) {
            submitBtn.disabled = true;
            btnText.innerHTML = 'Sending... ⏳';

            setTimeout(() => {
                submitBtn.disabled = false;
                btnText.innerHTML = 'Send Message';
                contactForm.reset();
                showToast('successToast', 4000);
            }, 1500);
        }
    });

    ['name', 'email', 'subject', 'message'].forEach(id => {
        const el = document.getElementById(id);
        if(el) {
            el.addEventListener('input', function() {
                hideFieldError(this.id, this.id + 'Error');
            });
        }
    });

    // FAQ Accordion
    const accordionItems = document.querySelectorAll('.accordion-item');
    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        header.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            accordionItems.forEach(otherItem => otherItem.classList.remove('active'));
            if (!isActive) item.classList.add('active');
        });
    });
}
