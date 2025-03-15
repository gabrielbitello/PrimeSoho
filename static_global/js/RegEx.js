document.addEventListener("DOMContentLoaded", function() {
    // 📌 Formatação e limite de telefone
    document.querySelectorAll(".phone").forEach((input) => {
        input.addEventListener("input", function (e) {
            let telefone = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número

            // Garante que sempre comece com +55
            if (!telefone.startsWith("55")) telefone = "55" + telefone;

            // Limita o tamanho máximo do número (sem contar o +)
            if (telefone.length > 13) telefone = telefone.substring(0, 13);

            // Aplica a formatação automática
            telefone = telefone.replace(/^55(\d{2})(\d{5})?(\d{4})?/, "+55 ($1) $2-$3");

            e.target.value = telefone.trim();
        });
    });

    // 📌 Formatação e limite de CPF
    document.querySelectorAll(".cpf").forEach((input) => {
        input.addEventListener("input", function (e) {
            let cpf = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número

            if (cpf.length > 3) cpf = cpf.replace(/^(\d{3})(\d)/, "$1.$2");
            if (cpf.length > 6) cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
            if (cpf.length > 9) cpf = cpf.replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");

            // Impede que ultrapasse o formato "XXX.XXX.XXX-XX"
            if (cpf.length > 14) cpf = cpf.substring(0, 14);

            e.target.value = cpf;
        });

        input.addEventListener("blur", function (e) {
            if (!validarCPF(e.target.value)) {
                alert("CPF inválido!");
                e.target.value = "";
            }
        });
    });

    // 📌 Validação de CPF
    function validarCPF(cpf) {
        cpf = cpf.replace(/\D/g, "");

        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false; // Evita CPFs repetidos (ex: 111.111.111-11)

        let soma = 0, resto;
        for (let i = 1; i <= 9; i++) soma += parseInt(cpf[i - 1]) * (11 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(cpf[9])) return false;

        soma = 0;
        for (let i = 1; i <= 10; i++) soma += parseInt(cpf[i - 1]) * (12 - i);
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(cpf[10])) return false;

        return true;
    }

    // 📌 Validação e formatação do e-mail
    document.querySelectorAll(".email").forEach((input) => {
        input.addEventListener("input", function (e) {
            let email = e.target.value.trim();

            // Remove espaços e caracteres inválidos
            email = email.replace(/\s/g, "").replace(/[^a-zA-Z0-9@._-]/g, "");

            // Impede múltiplos "@"
            let parts = email.split("@");
            if (parts.length > 2) {
                email = parts[0] + "@" + parts.slice(1).join("");
            }

            e.target.value = email;

            // Validação em tempo real
            if (validarEmail(email)) {
                input.setCustomValidity(""); // E-mail válido (removendo erro)
            } else {
                input.setCustomValidity("E-mail inválido!"); // Define como inválido no HTML
            }
        });

        // 📌 Evento para alertar quando o campo perde o foco
        input.addEventListener("blur", function (e) {
            let email = e.target.value.trim();
            if (!validarEmail(email)) {
                alert("E-mail inválido!");
            }
        });
    });

    // 📌 Função de validação de e-mail
    function validarEmail(email) {
        let regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
    }
});
