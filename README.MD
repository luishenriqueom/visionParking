# SMART PARKING
Solução técnica para a detecção de ocupação de vagas de estacionamento utilizando análise de histogramas de imagens

## Pré-requisitos

- [Python 3.x](https://www.python.org/downloads/) deve estar instalado na sua máquina.

## Configuração do Ambiente

### 1. Clonar o Repositório

Primeiro, clone o repositório para a sua máquina local usando:

```bash
git clone https://github.com/luishenriqueom/visionParking.git
cd visionParking
```

### 2. Criar um Ambiente Virtual

Para isolar as dependências do projeto, crie um ambiente virtual:

```bash
python -m venv venv
```

### 3. Ativar o Ambiente Virtual

Ative o ambiente virtual:

- **No Windows**:
  ```bash
  venv\Scripts\activate.bat
  ```
- **No macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 4. Instalar as Dependências

Com o ambiente virtual ativo, instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Executar o Projeto

Para iniciar o projeto, execute:

```bash
python ./src/main.py
```

Isso iniciará a aplicação conforme definido no `main.py`.
