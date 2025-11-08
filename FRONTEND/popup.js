const API_URL = 'http://localhost:8000';

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const result = document.getElementById('result');

// Check backend connection
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
            return true;
        }
    } catch (err) {
        console.error('Connection error:', err);
    }
    
    statusDot.classList.remove('connected');
    statusText.textContent = 'Disconnected';
    return false;
}

// Analyze text
async function analyzeText() {
    const text = textInput.value.trim();
    if (text.length < 10) {
        alert('Please enter at least 10 characters');
        return;
    }

    loading.style.display = 'block';
    result.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        const data = await response.json();
        if (data.success) {
            displayResult(data.analysis);
        }
    } catch (err) {
        console.error('Analysis error:', err);
        alert('Analysis failed. Please try again.');
    } finally {
        loading.style.display = 'none';
    }
}

// Display results
function displayResult(analysis) {
    const { ai_score, confidence, detected_model, reasoning, risk_level } = analysis;
    
    document.getElementById('resultScore').textContent = `${ai_score}%`;
    document.getElementById('resultModel').textContent = detected_model;
    document.getElementById('resultConfidence').textContent = `${confidence}%`;
    document.getElementById('resultReasoning').textContent = reasoning;
    
    const riskBadge = document.getElementById('resultRisk');
    riskBadge.textContent = risk_level;
    riskBadge.className = `risk-badge risk-${risk_level.toLowerCase()}`;
    
    result.className = 'result';
    if (ai_score > 80) result.classList.add('high');
    else if (ai_score > 60) result.classList.add('medium');
    else result.classList.add('low');
    
    document.getElementById('resultEmoji').textContent = 
        ai_score > 80 ? '⚠️' : ai_score > 60 ? '⚡' : '✅';
    
    result.style.display = 'block';
}

// Event Listeners
analyzeBtn.addEventListener('click', analyzeText);

document.getElementById('testAi').addEventListener('click', () => {
    textInput.value = 'Let me delve into this comprehensive analysis and leverage my robust understanding to provide a paradigm-shifting perspective.';
    analyzeText();
});

document.getElementById('testHuman').addEventListener('click', () => {
    textInput.value = 'I think this is interesting. It makes sense to me and I would like to try it out. What do you think?';
    analyzeText();
});

// Initial connection check
checkConnection();
setInterval(checkConnection, 30000); // Check connection every 30 seconds