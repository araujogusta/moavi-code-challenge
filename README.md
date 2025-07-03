# Moavi — Aplicação Web de Visualização de Escalas Realizadas

## Descrição

Este projeto tem como objetivo construir uma aplicação web que permite a **visualização e análise das escalas realizadas por colaboradores de uma farmácia**, a partir das marcações de ponto registradas ao longo do dia.

Cada colaborador realiza **4 marcações de ponto por dia**:

1. **Entrada** – Ex: 06:55
2. **Início do Almoço** – Ex: 10:40
3. **Retorno do Almoço** – Ex: 11:50
4. **Saída** – Ex: 15:25

A aplicação possibilita o **upload de arquivos CSV** contendo essas marcações, processa os dados e os exibe de forma tabular e gráfica para facilitar a visualização da escala diária dos colaboradores.

---

## Funcionalidades

### A. Histórico de Consumos

* Visualização de uma tabela com os uploads realizados.
* Informações exibidas:

  * Nome do arquivo CSV
  * Data e hora do consumo
  * Quantidade de marcações processadas

### B. Tabela de Marcações de Ponto

* Lista consolidada com todas as marcações importadas.
* Colunas exibidas:

  * Nome do arquivo de origem
  * Matrícula do colaborador
  * Data e hora da marcação

### C. Visualização Gráfica da Escala

* Gráfico de barras que mostra, em intervalos de 10 minutos, a quantidade de colaboradores presentes na farmácia ao longo do dia.
* O gráfico é baseado no dia selecionado pelo usuário.

---

## Tecnologias Utilizadas

* **Backend**: Python & Django
* **Frontend**: DTL & Vue.js
* **Banco de dados**: MySQL
* **Visualização de dados**: Chart.js
* **Containerização**: Docker, Docker Compose

---

## Como Rodar Localmente

1. Clone o repositório:

   ```bash
   git clone https://github.com/araujogusta/moavi-code-challenge.git
   cd moavi-code-challenge
   ```


2. Instale as dependências:

   ```bash
   poetry install
   ```

3. Configure as variáveis de ambiente, crie um arquivo `.env` usando o arquivo `.env.template` para se basear.

4. Execute a aplicação:

   ```bash
   poetry run python manage.py runserver
   ```

5. Acesse em:

   ```
   http://localhost:8000
   ```

---

## Executando com Docker

1. Certifique-se de ter Docker e Docker Compose instalados.
2. Crie um arquivo `.env` usando o arquivo `.env.template` para se basear.
3. Execute os containers com o comando:

   ```bash
   docker-compose up --build
   ```
4. A aplicação estará disponível em:

   ```
   http://localhost:8000
   ```

---

## Executando os Testes

A aplicação possui uma suíte de testes automatizados. Para executá-los:

```bash
poetry run python manage.py test
```
---

## Exemplo de Arquivo CSV

O arquivo CSV deve seguir o seguinte formato:

```
matricula;data;hora
1234;2025-06-01;06:55
1234;2025-06-01;10:40
1234;2025-06-01;11:50
1234;2025-06-01;15:25
```