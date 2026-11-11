const API_URL = "http://127.0.0.1:5000";

// Função para carregar os produtos da API na tabela.
async function getList() {
    const response = await fetch(`${API_URL}/produtos`);
    const data = await response.json();

    // Função para inserir cada produto retornado pela API.
    data.produtos.forEach((produto) => {
        insertList(produto.nome, produto.quantidade, produto.valor);
    });
}

// Função para enviar um produto novo para a API.
async function postItem(nome, quantidade, valor) {
    const response = await fetch(`${API_URL}/produto`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            nome,
            quantidade: Number(quantidade),
            valor: Number(valor),
        }),
    });
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message);
    }

    return data;
}

// Função para excluir um produto na API.
async function deleteItem(nome) {
    const response = await fetch(
        `${API_URL}/produto?nome=${encodeURIComponent(nome)}`,
        { method: "DELETE" },
    );
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message);
    }
}

// Função para validar os campos e adicionar um produto.
async function newItem() {
    const nomeInput = document.getElementById("newInput");
    const quantidadeInput = document.getElementById("newQuantity");
    const valorInput = document.getElementById("newPrice");
    const nome = nomeInput.value;
    const quantidade = quantidadeInput.value;
    const valor = valorInput.value;

    if (!nome.trim()) {
        alert("Escreva o nome de um item!");
        return;
    }

    if (
        !quantidade.trim()
        || !valor.trim()
        || !Number.isFinite(Number(quantidade))
        || !Number.isFinite(Number(valor))
    ) {
        alert("Quantidade e valor precisam ser números!");
        return;
    }

    try {
        const produto = await postItem(nome, quantidade, valor);
        insertList(produto.nome, produto.quantidade, produto.valor);
        nomeInput.value = "";
        quantidadeInput.value = "";
        valorInput.value = "";
        alert("Item adicionado!");
    } catch (erro) {
        alert(erro.message);
    }
}

// Função para inserir um produto e seu botão de remoção na tabela.
function insertList(nome, quantidade, valor) {
    const tabela = document.getElementById("myTable");
    const linha = tabela.insertRow(-1);
    linha.insertCell(0).textContent = nome;
    linha.insertCell(1).textContent = quantidade;
    linha.insertCell(2).textContent = valor;

    const celulaRemocao = linha.insertCell(3);
    const botaoRemover = document.createElement("span");
    botaoRemover.className = "close";
    botaoRemover.textContent = "×";

    // Função para remover o produto após confirmação e sucesso na API.
    botaoRemover.addEventListener("click", async () => {
        if (!confirm("Você tem certeza?")) {
            return;
        }

        try {
            await deleteItem(nome);
            linha.remove();
            alert("Removido!");
        } catch (erro) {
            alert(erro.message);
        }
    });

    celulaRemocao.appendChild(botaoRemover);
}

getList();
