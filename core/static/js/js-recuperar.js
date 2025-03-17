// Instância do HttpClient para facilitar as requisições
const api = new HttpClient('/');

// Função para inicializar o formulário de redefinir senha
function initPasswordResetConfirmForm() {
    document.getElementById('passwordResetConfirmForm')?.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries()); // Converte para um objeto JS

        await handlePasswordResetConfirm(data);
    });
}

// Função para obter o token da URL
function getTokenFromUrl() {
    const url = window.location.href;
    const regex = /\/recuperar_senha\/([a-zA-Z0-9]+)/;  // Expressão regular para capturar o token
    const match = url.match(regex);
    return match ? match[1] : null;  // Retorna o token ou null se não encontrado
}

// Função para enviar a requisição de confirmação de redefinição de senha
async function handlePasswordResetConfirm(data) {
    try {
        // Valida se as senhas são iguais
        if (data.new_password !== data.confirm_password) {
            showResponseMessage('As senhas não coincidem. Tente novamente.', 'error');
            return;
        }

        const token = getTokenFromUrl();  // Obtém o token da URL
        if (!token) {
            showResponseMessage('Token inválido ou não encontrado.', 'error');
            return;
        }

        const url = `recuperar_senha/${token}/`;  // URL completa
        
        // Enviando a requisição para o Django
        const response = await api.post(url, data);

        if (response.success) {
            showResponseMessage('Sua senha foi redefinida com sucesso!', 'success');
            setTimeout(() => {
                window.location.href = '/login/'; // Redireciona para a página de login
            }, 3000);
        } else {
            showResponseMessage(response.message || 'Erro desconhecido.', 'error');
        }
    } catch (error) {
        showResponseMessage(`Ocorreu um erro: ${error.message}`, 'error');
    }
}

// Função para exibir mensagens de sucesso ou erro
function showResponseMessage(message, type) {
    const responseMessageDiv = document.getElementById('responseMessage');
    responseMessageDiv.classList.remove('hidden');
    responseMessageDiv.textContent = message;
    responseMessageDiv.classList.add(type); // 'error' ou 'success'
}

// Inicializa o formulário de redefinir senha quando a página for carregada
document.addEventListener('DOMContentLoaded', initPasswordResetConfirmForm);
