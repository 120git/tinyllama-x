import { invoke } from '@tauri-apps/api/tauri';

// DOM elements
const commandInput = document.getElementById('command-input');
const proposeBtn = document.getElementById('propose-btn');
const runBtn = document.getElementById('run-btn');
const explainBtn = document.getElementById('explain-btn');
const historyBtn = document.getElementById('history-btn');
const output = document.getElementById('output');
const status = document.getElementById('status');

// State
let currentPlan = null;

// Utility functions
function appendOutput(text) {
    output.textContent += '\n' + text;
    output.scrollTop = output.scrollHeight;
}

function clearOutput() {
    output.textContent = '';
}

function updateStatus(text) {
    status.textContent = 'Status: ' + text;
}

// Event handlers
proposeBtn.addEventListener('click', async () => {
    const text = commandInput.value.trim();
    if (!text) {
        updateStatus('Please enter a command');
        return;
    }
    
    clearOutput();
    updateStatus('Classifying intent...');
    proposeBtn.disabled = true;
    
    try {
        // TODO: Call actual Tauri command
        // const result = await invoke('classify_intent', { text });
        
        // Placeholder
        appendOutput('⚠️ Not implemented yet');
        appendOutput('This would classify the intent: ' + text);
        appendOutput('\nTo implement:');
        appendOutput('1. Set up FastAPI bridge or shell integration');
        appendOutput('2. Implement classify_intent command in main.rs');
        appendOutput('3. Connect to TinyLlamaPresenter');
        
        updateStatus('Ready (placeholder)');
        runBtn.disabled = false;
    } catch (error) {
        appendOutput('Error: ' + error);
        updateStatus('Error occurred');
    } finally {
        proposeBtn.disabled = false;
    }
});

runBtn.addEventListener('click', async () => {
    if (!currentPlan) {
        updateStatus('No plan to execute');
        return;
    }
    
    // Confirmation
    if (!confirm('Execute real command? This will modify your system.')) {
        return;
    }
    
    updateStatus('Executing...');
    runBtn.disabled = true;
    
    try {
        // TODO: Call actual Tauri command
        // const result = await invoke('execute_plan', { planId: currentPlan.id });
        
        // Placeholder
        appendOutput('\n⚠️ Execution not implemented');
        updateStatus('Execution placeholder');
    } catch (error) {
        appendOutput('Error: ' + error);
        updateStatus('Execution failed');
    } finally {
        runBtn.disabled = false;
    }
});

explainBtn.addEventListener('click', async () => {
    const text = commandInput.value.trim();
    if (!text) {
        updateStatus('Please enter a command to explain');
        return;
    }
    
    clearOutput();
    updateStatus('Explaining...');
    explainBtn.disabled = true;
    
    try {
        // TODO: Call actual Tauri command
        // const result = await invoke('explain_command', { command: text });
        
        // Placeholder
        appendOutput('⚠️ Explain not implemented yet');
        appendOutput('Command: ' + text);
        appendOutput('\nWould show RAG-based explanation here');
        
        updateStatus('Ready');
    } catch (error) {
        appendOutput('Error: ' + error);
        updateStatus('Error occurred');
    } finally {
        explainBtn.disabled = false;
    }
});

historyBtn.addEventListener('click', async () => {
    clearOutput();
    updateStatus('Loading history...');
    historyBtn.disabled = true;
    
    try {
        // TODO: Call actual Tauri command
        // const result = await invoke('get_history', { limit: 20 });
        
        // Placeholder
        appendOutput('⚠️ History not implemented yet');
        appendOutput('Would show last 20 operations from SQLite');
        
        updateStatus('Ready');
    } catch (error) {
        appendOutput('Error: ' + error);
        updateStatus('Error occurred');
    } finally {
        historyBtn.disabled = false;
    }
});

// Test Tauri connection
invoke('greet', { name: 'User' })
    .then((message) => {
        console.log('Tauri connection:', message);
    })
    .catch((error) => {
        console.error('Tauri error:', error);
    });
