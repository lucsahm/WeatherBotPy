# 🌦️ Blumenau Clima Bot

---

## 💡 Sobre o Projeto

O **Blumenau Clima Bot** é um bot para Telegram desenvolvido em Python com **Flask**. Ele fornece informações sobre o clima atual e a previsão do tempo para a cidade de Blumenau, Santa Catarina, utilizando a API do **OpenWeatherMap**.

Além de interagir com o Telegram, o bot também publica dados de clima via **MQTT**, permitindo a integração com sistemas de automação, dashboards ou outros dispositivos.

---

## ✨ Funcionalidades

* **Clima Atual:** Obtém e exibe dados meteorológicos em tempo real para Blumenau (temperatura, sensação térmica, umidade, vento, descrição do tempo).
* **Previsão Detalhada:** Fornece a previsão do tempo para as próximas horas (6h, 12h ou 24h) em blocos de 3 horas.
* **Integração Telegram:** Responde a comandos específicos (`/clima`, `/previsao_6h`, `/previsao_12h`, etc.) enviados em chats privados ou grupos.
* **Publicação MQTT:** Publica dados climáticos em um tópico MQTT configurado, permitindo que outros sistemas consumam essas informações.

---

## 🚀 Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **Flask:** Microframework web para criar o webhook do Telegram.
* **python-dotenv:** Para gerenciar variáveis de ambiente (tokens, chaves de API).
* **requests:** Para fazer requisições HTTP para as APIs do OpenWeatherMap e Telegram.
* **paho-mqtt:** Cliente MQTT para publicação de dados.
* **OpenWeatherMap API:** Fonte dos dados climáticos.
* **Telegram Bot API:** Plataforma para comunicação com o bot.

---

## 🛠️ Instalação e Configuração

Siga os passos abaixo para configurar e rodar o bot em sua máquina local.

### Pré-requisitos

* Python 3.9+ instalado.
* Uma conta no OpenWeatherMap para obter sua **API Key**.
* Um bot criado no [BotFather](https://t.me/BotFather) do Telegram para obter seu **Bot Token** e **Bot Username**.
* Um broker MQTT (pode ser local como Mosquitto ou um serviço online).
* [ngrok](https://ngrok.com/) (ou similar) para expor seu webhook localmente para o Telegram (necessário para desenvolvimento).

### 1. Clonar o Repositório

```bash
git clone [https://github.com/lucsahm/WeatherBotPy.git](https://github.com/lucsahm/WeatherBotPy.git)
cd WeatherBotPy
```
### 2. Configurar o Ambiente Virtual (Recomendado)

```bash
# No Windows
python -m venv venv
.\venv\Scripts\activate

# No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```
### 4. Configurar Variáveis de Ambiente (.env)
Crie um arquivo chamado .env na raiz do projeto (na mesma pasta de bot_app.py) e preencha com suas credenciais:

```# .env
OWM_API_KEY="SUA_CHAVE_API_OPENWEATHERMAP"
TELEGRAM_BOT_TOKEN="SEU_TOKEN_DO_BOT_TELEGRAM"
BOT_USERNAME="seu_nome_de_usuario_do_bot" # Ex: meu_clima_bot
CITY="Blumenau" # Cidade para buscar o clima
MQTT_BROKER="broker.hivemq.com" # Ex: broker.hivemq.com ou localhost
MQTT_PORT=1883
MQTT_TOPIC="blumenau/clima" # Tópico MQTT para publicação
Importante: O arquivo .env é ignorado pelo Git (verifique o .gitignore) e não deve ser enviado para o seu repositório público.
```

### 5. Executar o Bot
```bash
python main.py
```
O bot iniciará e você verá uma mensagem indicando que ele está ouvindo na porta 5001.

---

## 🌐 Configuração do Webhook do Telegram (para desenvolvimento)
Para que o Telegram possa enviar atualizações para seu bot rodando localmente, você precisa expor sua porta 5001 para a internet. O ngrok é a ferramenta ideal para isso:

1. Instale o ngrok
`https://dashboard.ngrok.com`

2. Configure o ngrok com seu token
```bash
ngrok config add-authtoken <SEU_TOKEN>
```

3. Inicie o ngrok em um novo terminal, apontando para a porta 5001:

```bash
./ngrok http 5001
```
O ngrok irá fornecer uma URL pública (ex: `https://abcdef123456.ngrok-free.app`).

4. Configure o Webhook no Telegram usando a URL do ngrok. Substitua `SEU_BOT_TOKEN` e `SUA_URL_NGROK`:

```bash
https://api.telegram.org/bot<SEU_BOT_TOKEN>/setWebhook?url=https://<SUA_URL_NGROK>/webhook
```

Você deve ver uma resposta JSON do Telegram com `"ok":true,"result":true,"description":"Webhook was set"`.

5. Remover o Webhook do Telegram
```bash
https://api.telegram.org/bot<SEU_TOKEN>/deleteWebhook
```

---

## ⚡ Como Usar o Bot
Após a configuração, você pode interagir com o bot no Telegram:

* Envie /clima para obter o clima atual de Blumenau.

* Envie /previsao_6h para obter a previsão para as próximas 6 horas.

* Envie /previsao_12h para obter a previsão para as próximas 12 horas.

* Envie /previsao_24h para obter a previsão para as próximas 24 horas.

---
### Consultar informações da como ID do chat
`https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`

---
## 🧪 Teste Local (sem ngrok)
Para testar o webhook diretamente contra seu Flask rodando localmente, você pode usar o PowerShell no Windows para simular uma requisição do Telegram.

```PowerShell
# Exemplo de comando /clima
$jsonBody = @{
    update_id = 123456789
    message = @{
        message_id = 1
        from = @{id = 987654321; is_bot = $false; first_name = "Test"; last_name = "User"; username = "testuser"; language_code = "en"}
        chat = @{id = "SEU_CHAT_ID"; first_name = "Test"; last_name = "User"; username = "testuser"; type = "private"}
        date = 1678886400
        text = "/clima@seu_nome_de_usuario_do_bot"
        entities = @(@{offset = 0; length = 6; type = "bot_command"})
    }
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri 'http://localhost:5001/webhook' -Method POST -Headers @{"Content-Type"="application/json"} -Body $jsonBody
```
Substitua `SEU_CHAT_ID` pelo ID numérico do seu chat com o bot e `seu_nome_de_usuario_do_bot` pelo username real do seu bot.