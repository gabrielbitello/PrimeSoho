document.addEventListener('DOMContentLoaded', () => {
    // Inicializa o formulário de login e o clique do link "Esqueci minha senha"
    initLoginForm();
    initForgotPasswordLink();
});

// Instância do HttpClient para facilitar as requisições
const api = new HttpClient('/');

// Função para inicializar o formulário de login
function initLoginForm() {
    document.getElementById('loginForm')?.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries()); // Converte para um objeto JS

        console.log("Formulário de login enviado com os dados:", data);
        await handleLogin(data);
    });
}

// Função para enviar a requisição de login
async function handleLogin(data) {
    try {
        // Verificando os dados antes de enviar
        console.log('Dados a serem enviados:', data); // Verifique no console se os dados estão corretos

        // Enviando a requisição para o Django
        const response = await api.post('login/', data);

        // Verificando a resposta
        console.log('Resposta do servidor:', response); // Verifique a resposta no console

        if (response.success) {
            popup.Open_PopUp({
                type: 'success',
                message: 'Login realizado com sucesso!',
                autoClose: 5,
                redirectUrl: '/home/'
            });
        } else {
            popup.Open_PopUp({
                type: 'error',
                message: response.message || 'Erro desconhecido.'
            });
        }
    } catch (error) {
        popup.Open_PopUp({
            type: 'error',
            message: `Ocorreu um erro: ${error.message}`
        });
    }
}


// Função para inicializar o clique no "Esqueci minha senha"
function initForgotPasswordLink() {
    document.getElementById('forgotPasswordLink')?.addEventListener('click', (event) => {
        event.preventDefault(); // Previne o comportamento padrão
        showRecoveryPasswordPopup();
    });
}

// Função para exibir o popup de recuperação de senha
function showRecoveryPasswordPopup() {
    popup.Open_PopUp({
        type: 'neutral',
        message: 'Digite seu nome de usuário:',
        inputs: [{
            label: 'Nome de usuário:',
            name: 'username',
            type: 'text'
        }],
        buttons: [{
            label: 'Recuperar senha',
            action: async () => {
                const username = document.querySelector('input[name="username"]').value;
                await recoverPassword(username);
            }
        }]
    });
}

// Função para recuperar a senha
async function recoverPassword(username) {
    try {
        const response = await api.post('recover-password/', { username });
        if (response.success) {
            popup.Open_PopUp({
                type: 'success',
                message: 'Email enviado para recuperação de senha!'
            });
        } else {
            popup.Open_PopUp({
                type: 'error',
                message: response.message || 'Erro ao tentar recuperar senha.'
            });
        }
    } catch (error) {
        popup.Open_PopUp({
            type: 'error',
            message: `Erro ao tentar recuperar a senha: ${error.message}`
        });
    }
}
