const emailForm = document.getElementById('email-form');
const resultsSection = document.getElementById('resultsSection');
const analysisOutput = document.getElementById('analysisOutput');
const replyOutput = document.getElementById('replyOutput');
const spinner = '<div class="spinner-container"><div class="spinner"></div></div>';

emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(emailForm);
    const text = formData.get('text');
    const file = formData.get('file');

    if(!text.trim() && file.size===0) {
        toastAlert('Por favor, insira um texto ou um arquivo.', 'warn');
        return;
    }

    resultsSection.classList.remove('hidden');
    analysisOutput.innerHTML = spinner;
    replyOutput.innerHTML = '';

    try {
        const analyzeResponse = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        const analyzeData = await analyzeResponse.json();
        if(!analyzeResponse.ok) throw new Error(analyzeData.error || 'A análise falhou');

        analysisOutput.innerHTML = `
            <p><strong>Classificação:</strong> ${analyzeData.type}</p>
            <p><strong>Resumo:</strong> ${analyzeData.summary}</p>
            <p><strong>Pontos-chave:</strong></p>
            <ul>${analyzeData.keyPoints.map(point => `<li>${point}</li>`).join('')}</ul>
            <p><strong>Urgência:</strong> ${analyzeData.urgency}</p>
        `;

        replyOutput.innerHTML = spinner;

        const replyResponse = await fetch('/api/reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: analyzeData.originalContent, 
                type: analyzeData.type 
            })
        });

        const replyData = await replyResponse.json();
        if(!replyResponse.ok) throw new Error(replyData.error || 'A geração da resposta falhou');

        if (Array.isArray(replyData.reply)) {
            const suggestionsHTML = replyData.reply.map(suggestion => 
                `<li>${suggestion}</li>`
            ).join('');
            replyOutput.innerHTML = `<ul>${suggestionsHTML}</ul>`;
        } else {
            replyOutput.innerHTML = `<p>${replyData.reply}</p>`;
        }
        
    } catch (error) {
        toastAlert('Um erro ocorreu! Tente novamente mais tarde.', 'error');
        console.error('Ocorreu um erro:', error);
        if (analysisOutput.innerHTML.includes('spinner')) {
            analysisOutput.innerHTML = `<p style="color: red;">Ocorreu um erro! Tente novamente mais tarde.</p>`;
            replyOutput.innerHTML = '';
        } else {
            replyOutput.innerHTML = `<p style="color: red;">Ocorreu um erro! Tente novamente mais tarde.</p>`;
        }
    }
});