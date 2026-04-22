// ---------- STATE ----------
let array = [];
let stepsA = [];
let stepsB = [];
let currentStep = 0;
let isPlaying = false;
let animationDelay = 50;
let finalStatsA = {};
let finalStatsB = {};

// ---------- DOM ELEMENTS ----------
const vizA = document.getElementById('viz-a');
const vizB = document.getElementById('viz-b');
const compA = document.getElementById('comp-a');
const swapA = document.getElementById('swap-a');
const accessA = document.getElementById('access-a');
const compB = document.getElementById('comp-b');
const swapB = document.getElementById('swap-b');
const accessB = document.getElementById('access-b');
const algoAName = document.getElementById('algo-a-name');
const algoBName = document.getElementById('algo-b-name');
const headerA = document.getElementById('header-a');
const headerB = document.getElementById('header-b');
const winnerDisplay = document.getElementById('winner-display');
const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');
const stepBtn = document.getElementById('step-btn');
const sizeSlider = document.getElementById('array-size');
const sizeValue = document.getElementById('size-value');
const presetSelect = document.getElementById('array-preset');
const algoASelect = document.getElementById('algo-a');
const algoBSelect = document.getElementById('algo-b');
const panelA = document.getElementById('panel-a');
const panelB = document.getElementById('panel-b');

// ---------- HELPER FUNCTIONS ----------
function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}

function generateNewArray() {
    const size = parseInt(sizeSlider.value);
    const preset = presetSelect.value;
    // Generate locally for instant preview (will be replaced by backend later)
    array = [];
    for (let i = 0; i < size; i++) {
        array.push(Math.floor(Math.random() * 380) + 20);
    }
    renderBars(array, vizA);
    renderBars(array, vizB);
    resetStats();
}

function renderBars(arr, container) {
    container.innerHTML = '';
    const barContainer = document.createElement('div');
    barContainer.className = 'bar-container';
    const maxVal = Math.max(...arr, 1);
    arr.forEach(val => {
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = `${(val / maxVal) * 100}%`;
        barContainer.appendChild(bar);
    });
    container.appendChild(barContainer);
}

function updateStats(side, stats) {
    if (side === 'A') {
        compA.textContent = stats.comparisons || 0;
        swapA.textContent = stats.swaps || 0;
        accessA.textContent = stats.array_accesses || 0;
    } else {
        compB.textContent = stats.comparisons || 0;
        swapB.textContent = stats.swaps || 0;
        accessB.textContent = stats.array_accesses || 0;
    }
}

function resetStats() {
    updateStats('A', { comparisons: 0, swaps: 0, array_accesses: 0 });
    updateStats('B', { comparisons: 0, swaps: 0, array_accesses: 0 });
    winnerDisplay.innerHTML = '—';
}

function setButtonsState(playing) {
    playBtn.disabled = playing;
    pauseBtn.disabled = !playing;
    stepBtn.disabled = playing;
    playBtn.innerHTML = playing ? '<i class="fas fa-spinner fa-spin"></i> Running' : '<i class="fas fa-play"></i> Start Battle';
}

// ---------- BATTLE EXECUTION ----------
async function startBattle() {
    if (isPlaying) return;
    resetBattle(); // Clear previous run

    const algoA = algoASelect.value;
    const algoB = algoBSelect.value;
    const size = parseInt(sizeSlider.value);
    const preset = presetSelect.value;

    playBtn.disabled = true;
    playBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

    const res = await fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ algoA, algoB, size, preset, array })
    });
    const data = await res.json();

    array = data.array;
    stepsA = data.algoA.steps;
    stepsB = data.algoB.steps;
    finalStatsA = data.algoA.finalStats;
    finalStatsB = data.algoB.finalStats;

    // Update UI with algorithm names and colors
    algoAName.textContent = data.algoA.name;
    algoBName.textContent = data.algoB.name;
    panelA.style.borderTop = `4px solid ${data.algoA.color}`;
    panelB.style.borderTop = `4px solid ${data.algoB.color}`;

    renderBars(array, vizA);
    renderBars(array, vizB);
    resetStats();

    playBtn.disabled = false;
    playBtn.innerHTML = '<i class="fas fa-play"></i> Start Battle';

    currentStep = 0;
    isPlaying = true;
    setButtonsState(true);
    animationDelay = 101 - document.getElementById('speed-slider').value;

    const maxSteps = Math.max(stepsA.length, stepsB.length);
    while (currentStep < maxSteps && isPlaying) {
        if (currentStep < stepsA.length) await applyStep('A', stepsA[currentStep]);
        if (currentStep < stepsB.length) await applyStep('B', stepsB[currentStep]);
        currentStep++;
        if (currentStep >= maxSteps) {
            declareWinner();
            isPlaying = false;
            setButtonsState(false);
            break;
        }
        await sleep(animationDelay);
    }
}

async function applyStep(side, step) {
    const container = side === 'A' ? vizA : vizB;
    const bars = container.querySelectorAll('.bar');

    // Reset colors (keep sorted green)
    bars.forEach(bar => {
        if (!bar.classList.contains('sorted')) {
            bar.className = 'bar';
        }
    });

    if (step.type === 'compare') {
        const [i, j] = step.indices;
        bars[i]?.classList.add('compare');
        bars[j]?.classList.add('compare');
        updateStats(side, step.stats);
    } else if (step.type === 'swap') {
        const [i, j] = step.indices;
        const maxVal = Math.max(...step.array, 1);
        if (bars[i]) bars[i].style.height = `${(step.array[i] / maxVal) * 100}%`;
        if (bars[j]) bars[j].style.height = `${(step.array[j] / maxVal) * 100}%`;
        bars[i]?.classList.add('swap');
        bars[j]?.classList.add('swap');
        updateStats(side, step.stats);
    } else if (step.type === 'sorted') {
        bars[step.index]?.classList.add('sorted');
        updateStats(side, step.stats);
    } else if (step.type === 'pivot') {
        bars[step.index]?.classList.add('pivot');
        updateStats(side, step.stats);
    }
}

function declareWinner() {
    const scoreA = finalStatsA.comparisons + finalStatsA.swaps * 2;
    const scoreB = finalStatsB.comparisons + finalStatsB.swaps * 2;
    const diff = Math.abs(scoreA - scoreB);
    const maxScore = Math.max(scoreA, scoreB);
    const percent = maxScore > 0 ? (diff / maxScore) * 100 : 0;

    if (scoreA < scoreB) {
        winnerDisplay.innerHTML = `🏆 ${algoAName.textContent} wins by ${percent.toFixed(0)}% fewer ops`;
    } else if (scoreB < scoreA) {
        winnerDisplay.innerHTML = `🏆 ${algoBName.textContent} wins by ${percent.toFixed(0)}% fewer ops`;
    } else {
        winnerDisplay.innerHTML = `🤝 Perfect Tie`;
    }
}

function pauseBattle() {
    isPlaying = false;
    setButtonsState(false);
}

function stepBattle() {
    if (currentStep < Math.max(stepsA.length, stepsB.length)) {
        if (currentStep < stepsA.length) applyStep('A', stepsA[currentStep]);
        if (currentStep < stepsB.length) applyStep('B', stepsB[currentStep]);
        currentStep++;
        if (currentStep >= Math.max(stepsA.length, stepsB.length)) {
            declareWinner();
            setButtonsState(false);
            isPlaying = false;
        }
    }
}

function resetBattle() {
    isPlaying = false;
    setButtonsState(false);
    currentStep = 0;
    stepsA = [];
    stepsB = [];
    if (array.length) {
        renderBars(array, vizA);
        renderBars(array, vizB);
    }
    resetStats();
    panelA.style.borderTop = 'none';
    panelB.style.borderTop = 'none';
}

// ---------- EVENT LISTENERS ----------
sizeSlider.addEventListener('input', () => {
    sizeValue.textContent = sizeSlider.value;
    generateNewArray();
});

presetSelect.addEventListener('change', generateNewArray);

document.getElementById('speed-slider').addEventListener('input', (e) => {
    animationDelay = 101 - e.target.value;
});

algoASelect.addEventListener('change', () => {
    algoAName.textContent = algoASelect.options[algoASelect.selectedIndex].text;
    resetBattle();
});

algoBSelect.addEventListener('change', () => {
    algoBName.textContent = algoBSelect.options[algoBSelect.selectedIndex].text;
    resetBattle();
});

// ---------- GLOBAL FUNCTIONS ----------
window.generateNewArray = generateNewArray;
window.startBattle = startBattle;
window.pauseBattle = pauseBattle;
window.stepBattle = stepBattle;
window.resetBattle = resetBattle;

// ---------- INITIALIZATION ----------
generateNewArray();
algoAName.textContent = algoASelect.options[algoASelect.selectedIndex].text;
algoBName.textContent = algoBSelect.options[algoBSelect.selectedIndex].text;
sizeValue.textContent = sizeSlider.value;