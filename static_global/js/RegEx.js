document.addEventListener("DOMContentLoaded", function() {
    // Funções de formatação e validação
    const formatarTelefone = (e) => {
        let telefone = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número

        // Garante que sempre comece com +55
        if (!telefone.startsWith("55")) telefone = "55" + telefone;

        // Limita o tamanho máximo do número (sem contar o +)
        if (telefone.length > 13) telefone = telefone.substring(0, 13);

        // Aplica a formatação automática
        telefone = telefone.replace(/^55(\d{2})(\d{5})?(\d{4})?/, "+55 ($1) $2-$3");

        e.target.value = telefone.trim();
    };

    const formatarNumero = (e) => {
        let numero = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número
        numero = numero.replace(/\B(?=(\d{3})+(?!\d))/g, "."); // Adiciona ponto a cada 3 dígitos
        e.target.value = numero;
    };

    const formatarCPF = (e) => {
        let cpf = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número

        if (cpf.length > 3) cpf = cpf.replace(/^(\d{3})(\d)/, "$1.$2");
        if (cpf.length > 6) cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
        if (cpf.length > 9) cpf = cpf.replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");

        if (cpf.length > 14) cpf = cpf.substring(0, 14); // Impede que ultrapasse o formato "XXX.XXX.XXX-XX"
        e.target.value = cpf;
    };

    const validarCPFOnBlur = (e) => {
        if (e.target.value && !validarCPF(e.target.value)) {
            alert("CPF inválido!");
            e.target.value = ""; // Limpa o campo
        }
    };

    const formatarEmail = (e) => {
        let email = e.target.value.trim();

        email = email.replace(/\s/g, "").replace(/[^a-zA-Z0-9@._-]/g, ""); // Remove espaços e caracteres inválidos

        let parts = email.split("@");
        if (parts.length > 2) {
            email = parts[0] + "@" + parts.slice(1).join(""); // Impede múltiplos "@"
        }

        e.target.value = email;
    };

    const validarEmailOnBlur = (e) => {
        let email = e.target.value.trim();
        if (email && !validarEmail(email)) {
            alert("E-mail inválido!");
            e.target.value = ""; // Limpa o campo
        }
    };

    // Validação de CPF
    const validarCPF = (cpf) => {
        cpf = cpf.replace(/\D/g, "");
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;

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
    };

    // Validação de e-mail
    const validarEmail = (email) => {
        const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
    };

    // Aplicar eventos aos campos existentes
    const aplicarEventos = () => {
        document.querySelectorAll(".phone").forEach((input) => {
            // Remove evento anterior e adiciona novamente
            input.removeEventListener("input", formatarTelefone);
            input.addEventListener("input", formatarTelefone);
        });

        document.querySelectorAll(".number").forEach((input) => {
            input.removeEventListener("input", formatarNumero);
            input.addEventListener("input", formatarNumero);
        });

        document.querySelectorAll(".cpf").forEach((input) => {
            input.removeEventListener("input", formatarCPF);
            input.removeEventListener("blur", validarCPFOnBlur);
            input.addEventListener("input", formatarCPF);
            input.addEventListener("blur", validarCPFOnBlur);
        });

        document.querySelectorAll(".email").forEach((input) => {
            input.removeEventListener("input", formatarEmail);
            input.removeEventListener("blur", validarEmailOnBlur);
            input.addEventListener("input", formatarEmail);
            input.addEventListener("blur", validarEmailOnBlur);
        });
    };

    // Aplicar eventos na carga inicial
    aplicarEventos();

    // Observar mudanças no DOM
    const observador = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                aplicarEventos(); // Se novos nós foram adicionados, aplicar eventos
            }
        });
    });

    observador.observe(document.body, {
        childList: true,
        subtree: true
    });
});