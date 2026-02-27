# Projeto Backend de Compras - Supermercado BOX MAYORISTA

Este é o repositório do projeto backend de compras para o supermercado BOX MAYORISTA. O projeto é desenvolvido em Python e utiliza o banco de dados PostgreSQL.

## Rotas

A seguir estão as principais rotas disponíveis no projeto:

### User

- `GET /users`: Retorna a lista de usuários.
- `GET /users/{id}`: Retorna os detalhes de um usuário específico.
- `POST /users`: Cria um novo usuário.
- `PUT /users/{id}`: Atualiza os dados de um usuário existente.
- `DELETE /users/{id}`: Remove um usuário.

### Fornecedor

- `GET /fornecedores`: Retorna a lista de fornecedores.
- `GET /fornecedores/{id}`: Retorna os detalhes de um fornecedor específico.
- `POST /fornecedores`: Cria um novo fornecedor.
- `PUT /fornecedores/{id}`: Atualiza os dados de um fornecedor existente.
- `DELETE /fornecedores/{id}`: Remove um fornecedor.

### Sucursal

- `GET /sucursais`: Retorna a lista de sucursais.
- `GET /sucursais/{id}`: Retorna os detalhes de uma sucursal específica.
- `POST /sucursais`: Cria uma nova sucursal.
- `PUT /sucursais/{id}`: Atualiza os dados de uma sucursal existente.
- `DELETE /sucursais/{id}`: Remove uma sucursal.

### Compras

- `GET /compras`: Retorna a lista de compras.
- `GET /compras/{id}`: Retorna os detalhes de uma compra específica.
- `POST /compras`: Cria uma nova compra.
- `PUT /compras/{id}`: Atualiza os dados de uma compra existente.
- `DELETE /compras/{id}`: Remove uma compra.

### Produtos

- `GET /produtos`: Retorna a lista de produtos.
- `GET /produtos/{id}`: Retorna os detalhes de um produto específico.
- `POST /produtos`: Cria um novo produto.
- `PUT /produtos/{id}`: Atualiza os dados de um produto existente.
- `DELETE /produtos/{id}`: Remove um produto.

## Configuração do Banco de Dados

Certifique-se de ter o PostgreSQL instalado e configurado corretamente. Você pode encontrar as instruções de configuração no site oficial do PostgreSQL.

## Instalação

1. Clone este repositório.
2. Crie um ambiente virtual e ative-o.
3. Instale as dependências do projeto usando o comando `pip install -r requirements.txt`.
4. Configure as variáveis de ambiente necessárias, como as credenciais do banco de dados.
5. Execute o comando `python manage.py migrate` para aplicar as migrações do banco de dados.
6. Inicie o servidor de desenvolvimento usando o comando `python manage.py runserver`.

## Testes

Para executar o teste:
````
daphne app.asgi:application -b 0.0.0.0 -p 8000          
````

## Contribuição

Se você deseja contribuir para este projeto, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).