class HttpClient {
    constructor(baseURL = '', defaultHeaders = {}) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...defaultHeaders
        };

        // Pega o CSRF Token do HTML
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        // Adiciona o token CSRF aos cabeçalhos padrões, se existir
        if (csrfToken) {
            this.defaultHeaders['X-CSRFToken'] = csrfToken;
        }
    }

    // Método que faz a requisição
    async request(endpoint, method = 'GET', data = null, headers = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method,
            headers: { ...this.defaultHeaders, ...headers } // Adiciona os cabeçalhos personalizados aos padrões
        };

        if (data) {
            options.body = JSON.stringify(data); // Envia os dados como JSON no corpo da requisição
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            throw error; // Permite que o erro seja tratado onde a função for chamada
        }
    }

    // Métodos específicos para cada tipo de requisição
    get(endpoint, headers = {}) {
        return this.request(endpoint, 'GET', null, headers);
    }

    post(endpoint, data, headers = {}) {
        return this.request(endpoint, 'POST', data, headers);
    }

    put(endpoint, data, headers = {}) {
        return this.request(endpoint, 'PUT', data, headers);
    }

    delete(endpoint, headers = {}) {
        return this.request(endpoint, 'DELETE', null, headers);
    }
}
