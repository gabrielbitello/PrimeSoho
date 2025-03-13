$(document).ready(function () {
    // Inicializa o formulário de login e o clique do link "Esqueci minha senha"
    initLoginForm();
    initForgotPasswordLink();
});

// Função para inicializar o formulário de login
function initLoginForm() {
    $('#loginForm').on('submit', function (event) {
        event.preventDefault(); // Impede o envio padrão do formulário

        const formData = $(this).serialize(); // Coleta os dados do formulário
        console.log("Formulário de login enviado com os dados:", formData);
        handleLogin(formData);
    });
}

// Função para enviar a requisição de login
function handleLogin(formData) {
    $.ajax({
        url: '/login/', // A URL do Django para o login
        type: 'POST',
        data: formData,
        success: function (response) {
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
        },
        error: function (xhr, status, error) {
            popup.Open_PopUp({
                type: 'error',
                message: `Ocorreu um erro: ${error}`
            });
        }
    });
}

// Função para inicializar o clique no "Esqueci minha senha"
function initForgotPasswordLink() {
    $('#forgotPasswordLink').on('click', function (event) {
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
            action: () => {
                const username = document.querySelector('input[name="username"]').value;
                recoverPassword(username);
            }
        }]
    });
}

// Função para recuperar a senha
function recoverPassword(username) {
    $.ajax({
        url: '/recover-password/', // A URL para recuperação de senha
        type: 'POST',
        data: { username: username },
        success: function (response) {
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
        },
        error: function (xhr, status, error) {
            popup.Open_PopUp({
                type: 'error',
                message: `Erro ao tentar recuperar a senha: ${error}`
            });
        }
    });
}
