document.addEventListener('DOMContentLoaded', () => {
    fetchHistory();
    toggleResults();
});

const emailForm = document.getElementById('email-form');
const resultsSection = document.getElementById('resultsSection');
const analysisOutput = document.getElementById('analysisOutput');
const replyOutput = document.getElementById('replyOutput');
const spinner = '<div class="spinner-container"><div class="spinner"></div></div>';
const historyList = document.getElementById('historyList');

const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');

let isAnalyzing = false;
let isGeneratingResponses = false;

function formatDate(date) {
    try {
        const isoDateString = date.replace(' ', 'T');
        const originalDate = new Date(isoDateString);
        
        const utcMinus3Date = new Date(originalDate);
        utcMinus3Date.setHours(originalDate.getHours() - 3);
        
        return utcMinus3Date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (error) {
        console.error('Erro ao formatar data:', error);
        return date;
    }
}

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        removeFileBtn.classList.remove('hidden');
    } else {
        fileName.textContent = 'Nenhum arquivo selecionado';
        removeFileBtn.classList.add('hidden');
    }
    toggleResults();
});

removeFileBtn.addEventListener('click', () => {
    fileInput.value = '';
    fileName.textContent = 'Nenhum arquivo selecionado';
    removeFileBtn.classList.add('hidden');
    toastAlert('Arquivo removido', 'success');
    toggleResults();
});

emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitButton = emailForm.querySelector('button[type="submit"]');
    if (isAnalyzing) return;
    
    isAnalyzing = true;
    submitButton.disabled = true;
    submitButton.innerHTML = 'Analisando...';

    const formData = new FormData(emailForm);
    const text = formData.get('text');
    const file = formData.get('file');
    const tone = formData.get('tone');

    if(!text.trim() && file.size===0) {
        toastAlert('Por favor, insira um texto ou um arquivo.', 'warn');
        resultsSection.classList.add('hidden');
        isAnalyzing = false;
        submitButton.disabled = false;
        submitButton.innerHTML = 'Analisar Email';
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

        await generateAnswers(
            analyzeData.originalContent,
            analyzeData.type,
            tone,
            replyOutput,
            analyzeData.sender_email || ''
        );
        
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
    } finally {
        isAnalyzing = false;
        submitButton.disabled = false;
        submitButton.innerHTML = 'Analisar Email';
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
                    <strong class="edit-classification">${item.classification}</strong>
                    <span class="urgency-${item.urgency} urgency-badge edit-urgency">${item.urgency}</span>
                    <span>${item.content.substring(0, 50)}...</span>
                    <span class="expand-icon">+</span>
                </div>
                <div class="history-details hidden">
                    <p><strong>Resumo:</strong> ${item.summary}</p>
                    <p><strong>Pontos-chave:</strong></p>
                    <ul>${keyPointsHTML}</ul>
                    <p><strong>Urgência:</strong> ${item.urgency}</p>
                    ${item.sender_email ? `<p><strong>Remetente:</strong> ${item.sender_email}</p>` : ''}
                    <p><strong>Data:</strong> ${formatDate(item.timestamp)}</p>
                    <div class="history-actions">
                        <button class="generate-responses" data-id="${item.id}" data-content="${encodeURIComponent(item.content)}" data-type="${item.classification}" data-email="${item.sender_email || ''}">
                            Gerar respostas
                        </button>
                        <button class="delete-history" data-id="${item.id}">Remover do Histórico</button>
                    </div>
                    <div class="history-responses"></div>
                </div>
            `;
            historyList.appendChild(li);
        });
    } catch(error) {
        console.error('Erro ao buscar o histórico:', error);
        historyList.innerHTML = '<li>Erro ao carregar o histórico.</li>';
    }
}

function toggleResults() {
    const textValue = document.getElementById('email-input').value.trim();
    const hasFile = fileInput.files && fileInput.files.length > 0;

    if (!textValue && !hasFile) {
        resultsSection.classList.add('hidden');
    }
}

async function generateAnswers(emailContent, emailType, tone, container, senderEmail = '', isHistory = false, buttonToDisable = null) {
    if (buttonToDisable) {
        buttonToDisable.disabled = true;
        buttonToDisable.innerHTML = 'Gerando...';
    }
    
    if (isHistory) {
        isGeneratingResponses = true;
    }
    
    container.innerHTML = spinner;
    
    try {
        const requestData = {
            email: emailContent,
            type: emailType,
            tone: tone
        };
        
        const replyResponse = await fetch('/api/reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (!replyResponse.ok) {
            let errorMsg = 'Falha ao gerar respostas';
            try {
                const errorData = await replyResponse.json();
                errorMsg = errorData.error || errorMsg;
            } catch (e) {
                console.error('[generateAnswers] Não foi possível obter detalhes do erro');
            }
            throw new Error(errorMsg);
        }

        const replyData = await replyResponse.json();
        
        const title = isHistory ? '<h4>Respostas Sugeridas:</h4>' : '';
        
        if (!replyData || replyData === undefined) {
            console.error('[generateAnswers] replyData é undefined ou null');
            throw new Error('Dados de resposta inválidos');
        }
        
        if (!('reply' in replyData)) {
            console.error('[generateAnswers] replyData não contém o campo reply');
            throw new Error('Formato de resposta inválido');
        }
        
        let responseHTML = '';
        
        let suggestionsArray = [];
        
        if (Array.isArray(replyData.reply)) {
            suggestionsArray = replyData.reply;
        } else {
            suggestionsArray = [String(replyData.reply)];
        }
        
        if (suggestionsArray.length === 0) {
            responseHTML = `${title}<p>Nenhuma sugestão de resposta disponível.</p>`;
        } else {
            const suggestionsHTML = suggestionsArray.map(suggestion => {
                if (typeof suggestion !== 'string') {
                    console.warn('[generateAnswers] Item não é uma string:', suggestion);
                    suggestion = String(suggestion);
                }
                
                const mailtoBody = encodeURIComponent(suggestion);
                
                const emailOptions = senderEmail 
                    ? `<div class="email-options">
                        <a href="mailto:${senderEmail}?body=${mailtoBody}" class="email-btn">Cliente de Email</a>
                        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=${senderEmail}&body=${mailtoBody}" 
                           target="_blank" class="email-btn gmail-btn">Gmail</a>
                        <a href="https://outlook.live.com/mail/0/deeplink/compose?to=${senderEmail}&body=${mailtoBody}" 
                           target="_blank" class="email-btn outlook-btn">Outlook</a>
                       </div>`
                    : `<button type="button" class="email-btn email-disabled">Responder por E-mail</button>`;
                
                return `
                    <li>
                        <p>${suggestion}</p>
                        <div class="reply-actions">
                            <button class="copy-btn" data-text="${encodeURIComponent(suggestion)}">Copiar</button>
                            ${emailOptions}
                        </div>
                    </li>
                `;
            }).join('');
            
            responseHTML = `${title}<ul class="reply-suggestions">${suggestionsHTML}</ul>`;
        }
        
        container.innerHTML = responseHTML;
        
        container.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', function() {
                try {
                    const text = decodeURIComponent(this.dataset.text);
                    
                    navigator.clipboard.writeText(text).then(() => {
                        toastAlert('Resposta copiada!', 'success');
                    }).catch(err => {
                        console.error('[generateAnswers] Erro ao copiar:', err);
                        toastAlert('Falha ao copiar texto.', 'error');
                    });
                } catch (e) {
                    console.error('[generateAnswers] Erro ao processar texto para copiar:', e);
                    toastAlert('Erro ao processar texto', 'error');
                }
            });
        });
        
        container.querySelectorAll('.email-disabled').forEach(button => {
            button.addEventListener('click', function() {
                toastAlert('Nenhum e-mail do remetente fornecido. Adicione um e-mail para responder.', 'warn');
            });
        });
        
        return replyData;
    } catch (error) {
        console.error('[generateAnswers] Erro completo:', error);
        container.innerHTML = '<p class="error">Erro ao gerar respostas. Tente novamente.</p>';
        toastAlert(`Erro ao gerar respostas: ${error.message}`, 'error');
        return null;
    } finally {
        if (buttonToDisable) {
            buttonToDisable.disabled = false;
            buttonToDisable.innerHTML = 'Gerar respostas';
        }
        
        if (isHistory) {
            isGeneratingResponses = false;
        }
    }
}

document.getElementById('email-input').addEventListener('input', toggleResults);

historyList.addEventListener('click', async (e) => {
    const target = e.target;
    const clickedLi = target.closest('li');
    if (!clickedLi) return;

    const entryId = clickedLi.dataset.historyId;

    if (target.classList.contains('delete-history')) {
        e.stopPropagation();
        const entryId = e.target.dataset.id;

        try {
            const response = await fetch(`/api/history/${entryId}`, {
                method: 'DELETE'
            });

            if(!response.ok) throw new Error('Falha ao deletar a entrada do histórico');
            toastAlert('Email deletado com sucesso!', 'success');
            clickedLi.style.transition = 'opacity 0.9s ease';
            clickedLi.style.opacity = '0';
            setTimeout(() => clickedLi.remove(), 500);
            fetchHistory();

        } catch(error) {
            console.error('Erro ao deletar a entrada do histórico:', error);
            toastAlert('Erro ao deletar a entrada do histórico. Tente novamente.', 'error');
        }
        return;
    }

    if (target.classList.contains('generate-responses')) {
        e.stopPropagation();
        
        if (isGeneratingResponses) return;
        
        const content = decodeURIComponent(target.dataset.content);
        const type = target.dataset.type;
        const senderEmail = target.dataset.email;
        const tone = document.getElementById('tone-selector')?.value || 'professional';
        
        const responsesContainer = clickedLi.querySelector('.history-responses');
        
        await generateAnswers(content, type, tone, responsesContainer, senderEmail, true, target);
        
        return;
    }

    if (clickedLi.querySelector('select')) {
        return;
    }

    let originalElement = null;
    let selectElement = null;
    let fieldToUpdate = '';

    if (target.classList.contains('edit-classification')) {
        originalElement = target;
        fieldToUpdate = 'classification';
        selectElement = document.createElement('select');
        selectElement.innerHTML = `
            <option value="Produtivo" ${target.textContent === 'Produtivo' ? 'selected' : ''}>Produtivo</option>
            <option value="Improdutivo" ${target.textContent === 'Improdutivo' ? 'selected' : ''}>Improdutivo</option>
        `;
    } else if (target.classList.contains('edit-urgency')) {
        originalElement = target;
        fieldToUpdate = 'urgency';
        selectElement = document.createElement('select');
        let options = '';
        for (let i = 1; i <= 5; i++) {
            options += `<option value="${i}" ${target.textContent == i ? 'selected' : ''}>${i}</option>`;
        }
        selectElement.innerHTML = options;
    }

    if (originalElement && selectElement) {
        e.stopPropagation();

        originalElement.replaceWith(selectElement);
        selectElement.focus();

        const revertUI = () => selectElement.replaceWith(originalElement);

        selectElement.addEventListener('change', async () => {
            const newValue = selectElement.value;
            try {
                const response = await fetch(`/api/history/${entryId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ [fieldToUpdate]: newValue })
                });
                if (!response.ok) throw new Error('Falha ao salvar');
                
                toastAlert('Atualizado com sucesso!', 'success');
                await fetchHistory();
            } catch (error) {
                console.error('Erro ao atualizar:', error);
                toastAlert('Erro ao salvar. Tente novamente.', 'error');
                revertUI();
            }
        });

        selectElement.addEventListener('blur', () => {
            setTimeout(() => {
                if (document.body.contains(selectElement)) {
                    revertUI();
                }
            }, 200);
        });
    } else {
        const detailsView = clickedLi.querySelector('.history-details');
        if (!detailsView) return;
        detailsView.classList.toggle('hidden');
        clickedLi.classList.toggle('expanded');
    }
});