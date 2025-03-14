class Popup {
    constructor() {
        this.container = document.getElementById("popup");
        this.overlay = document.getElementById("popupOverlay");
        this.closeButton = document.getElementById("closePopup");
        
        this.closeButton.addEventListener("click", () => this.Close_PopUp());
    }

    Open_PopUp({ type = "neutral", message = "", inputs = [], buttons = [], autoClose = 0, redirectUrl = "" }) {
        console.log("Chamando popup.open()");
        console.log("Parâmetros recebidos:", { type, message, inputs, buttons, autoClose, redirectUrl });
    
        // Torna visível o popup e o overlay alterando o estilo
        this.container.style.display = "block";
        this.overlay.style.display = "block";
    
        // Alterando a classe do popup conforme o tipo
        this.container.className = `popup ${type}`;
    
        // Definindo a mensagem no popup
        const messageElement = document.getElementById("popup-message");
        messageElement.textContent = message;
    
        // Limpando o corpo e rodapé
        this.container.querySelector(".input-container").innerHTML = "";
    
        // Adicionando inputs
        inputs.forEach(input => {
            let wrapper = document.createElement("div");
            let label = document.createElement("label");
            let field = document.createElement("input");
            label.textContent = input.label;
            field.type = input.type || "text";
            field.name = input.name || "";
            wrapper.appendChild(label);
            wrapper.appendChild(field);
            this.container.querySelector(".input-container").appendChild(wrapper);
        });
    
        // Adicionando botões
        buttons.forEach(btn => {
            let button = document.createElement("button");
            button.textContent = btn.label;
            button.classList.add("submit-btn");
            button.onclick = () => {
                if (btn.action) btn.action();
                if (btn.close) this.Close_PopUp();
            };
            this.container.querySelector(".input-container").appendChild(button);
        });
    
        // Se o popup deve fechar automaticamente
        if (autoClose > 0) {
            setTimeout(() => {
                this.Close_PopUp();
                // Verifica se existe uma URL de redirecionamento e redireciona após o fechamento
                if (redirectUrl) {
                    window.location.href = redirectUrl;
                }
            }, autoClose * 1000);
        }
    
        // Verificar se a URL de redirecionamento foi fornecida
        if (redirectUrl) {
            // Adiciona o redirecionamento caso o popup seja fechado manualmente
            this.container.querySelector(".close-btn").addEventListener("click", () => {
                window.location.href = redirectUrl;
            });
        }
    }
    
    Close_PopUp() {
        // Torna invisível o popup e o overlay alterando o estilo
        this.container.style.display = "none";
        this.overlay.style.display = "none";
    }
}

const popup = new Popup();


