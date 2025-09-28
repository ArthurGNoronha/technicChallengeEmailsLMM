document.addEventListener('DOMContentLoaded', fetchHistory);

const emailForm = document.getElementById('email-form');
const resultsSection = document.getElementById('resultsSection');
const analysisOutput = document.getElementById('analysisOutput');
const replyOutput = document.getElementById('replyOutput');
const spinner = '<div class="spinner-container"><div class="spinner"></div></div>';
const historyList = document.getElementById('historyList');

emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(emailForm);
    const text = formData.get('text');
    const file = formData.get('file');
    const tone = formData.get('tone');

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
                type: analyzeData.type,
                tone: tone
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
        
        await fetchHistory();

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

async function fetchHistory() {
    try {
        const response = await fetch('/api/history');
        if(!response.ok) throw new Error('Falha ao buscar o histórico');

        const data = await response.json();

        historyList.innerHTML = ''
        if(data.length === 0) {
            historyList.innerHTML = '<li>Sem emails recentes.</li>';
            return;
        }

        data.forEach(item => {
            const li = document.createElement('li');
            li.dataset.historyId = item.id;

            const keyPoints = JSON.parse(item.keyPoints);
            const keyPointsHTML = keyPoints.map(point => `<li>${point}</li>`).join('');
            
            li.innerHTML = `
                <div class="history-summary">
                    <strong>${item.classification}</strong>
                    <span class="urgency-${item.urgency} urgency-badge">${item.urgency}</span>
                    <span>${item.content.substring(0, 50)}...</span>
                    <span class="expand-icon">+</span>
                </div>
                <div class="history-details hidden">
                    <p><strong>Resumo:</strong> ${item.summary}</p>
                    <p><strong>Pontos-chave:</strong></p>
                    <ul>${keyPointsHTML}</ul>
                    <p><strong>Urgência:</strong> ${item.urgency}</p>
                </div>
            `;
            historyList.appendChild(li);
        });
    } catch(error) {
        console.error('Erro ao buscar o histórico:', error);
        historyList.innerHTML = '<li>Erro ao carregar o histórico.</li>';
    }
}

historyList.addEventListener('click', (e) => {
    const clickedLi = e.target.closest('li');
    if(!clickedLi) return;

    const detailsView = clickedLi.querySelector('.history-details');
    if(!detailsView) return;

    detailsView.classList.toggle('hidden');
    clickedLi.classList.toggle('expanded');
});