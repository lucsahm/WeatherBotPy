#!/usr/bin/env python

import os
from flask import Flask, request
from dotenv import load_dotenv  # Para carregar variáveis do .env

# Importa as classes de seus respectivos módulos
from api.clima import ClimaAPI
from api.telegram import TelegramMessenger
from mqtt.publisher import MQTTPublisher

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


class TelegramBotApp:
    """
    Classe principal que gerencia o aplicativo Flask e coordena as interações
    com as APIs de clima, Telegram e MQTT.
    """

    def __init__(self):
        # Carrega as configurações das variáveis de ambiente
        self.owm_api_key = os.getenv("OWM_API_KEY")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot_username = os.getenv("BOT_USERNAME")  # Nome do seu bot (ex: sahm2_bot)
        self.city = os.getenv("CITY", "Blumenau")  # Default para Blumenau

        self.mqtt_broker = os.getenv("MQTT_BROKER")
        self.mqtt_port = int(os.getenv("MQTT_PORT"))
        self.mqtt_topic = os.getenv("MQTT_TOPIC")

        # Verifica se as chaves foram carregadas
        if not self.owm_api_key or not self.telegram_bot_token or not self.bot_username:
            raise ValueError(
                "As variáveis de ambiente OWM_API_KEY, TELEGRAM_BOT_TOKEN e BOT_USERNAME devem ser configuradas.")

        self.app = Flask(__name__)

        # Instancia os objetos das outras classes
        self.clima_api = ClimaAPI(self.owm_api_key, self.city)
        self.telegram_messenger = TelegramMessenger(self.telegram_bot_token)
        self.mqtt_publisher = MQTTPublisher(self.mqtt_broker, self.mqtt_port, self.mqtt_topic)

        # Configura a rota do webhook do Flask
        self.app.route("/webhook", methods=["POST"])(self._webhook_handler)

    def _webhook_handler(self):
        """
        Manipulador do webhook para as mensagens do Telegram.
        Este método é chamado quando o Telegram envia uma atualização.
        """
        data = request.get_json()
        message_text = data.get("message", {}).get("text", "")
        chat_id = data.get("message", {}).get("chat", {}).get("id")

        if not message_text or not chat_id:
            return "Ignored", 200

        # Normaliza a mensagem para comparação, incluindo o nome do bot
        normalized_message = message_text.strip().lower()

        # Comandos de clima
        if normalized_message == f"/clima@{self.bot_username}":
            self._handle_clima_command(chat_id)

        # Comandos de previsão
        elif normalized_message.startswith(f"/previsao_") and normalized_message.endswith(f"@{self.bot_username}"):
            self._handle_previsao_command(chat_id, normalized_message)

        else:
            print(f"Comando não reconhecido: {message_text}")
            # Opcional: enviar uma mensagem de "comando não reconhecido" para o usuário
            # self.telegram_messenger.enviar_mensagem(chat_id, "Comando não reconhecido. Tente /clima@seu_bot ou /previsao_Xh@seu_bot.")
            pass

        return "OK", 200

    def _handle_clima_command(self, chat_id: str):
        """Processa o comando /clima."""
        clima_dados = self.clima_api.obter_dados_clima_atual()
        if clima_dados:
            texto_clima = (
                f"🌤 Clima em {clima_dados['cidade']}:\n"
                f"🌡 Temperatura: {clima_dados['temperatura']}°C\n"
                f"🤒 Sensação: {clima_dados['sensacao']}°C\n"
                f"💧 Umidade: {clima_dados['umidade']}%\n"
                f"💨 Vento: {clima_dados['vento']}\n"
                f"🔎 Descrição: {clima_dados['descricao'].capitalize()}"
            )
            self.telegram_messenger.enviar_mensagem(chat_id, texto_clima, parse_mode="HTML")
            self.mqtt_publisher.publicar_mensagem(clima_dados)
        else:
            self.telegram_messenger.enviar_mensagem(chat_id, "Não foi possível obter os dados do clima atual.")

    def _handle_previsao_command(self, chat_id: str, message: str):
        """Processa os comandos /previsao_Xh."""
        try:
            horas_str = message.split('_')[1].split('h')[0]
            horas = int(horas_str)

            if horas not in [6, 12, 24]:
                self.telegram_messenger.enviar_mensagem(chat_id,
                                                        "Erro: Por favor, solicite a previsão para 6h, 12h ou 24h.")
            else:
                previsao_detalhada = self.clima_api.obter_previsao_detalhada(horas)
                mensagem_final_para_telegram = f"Previsão para as próximas {horas} horas em {self.city}:\n\n{previsao_detalhada}"
                self.telegram_messenger.enviar_mensagem(chat_id, mensagem_final_para_telegram, parse_mode="HTML")

        except (ValueError, IndexError):
            self.telegram_messenger.enviar_mensagem(chat_id,
                                                    "Comando de previsão inválido. Use /previsao_6h, /previsao_12h ou /previsao_24h.")

    def run(self, host: str = "0.0.0.0", port: int = 5001):
        """Inicia o servidor Flask."""
        print(f"Iniciando Bot de Clima para {self.city} (@{self.bot_username}) na porta {port}...")
        self.app.run(host=host, port=port)


# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    # Cria uma instância da aplicação do bot
    bot_app = TelegramBotApp()
    # Inicia a aplicação Flask
    bot_app.run()