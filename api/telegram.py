# api/telegram.py
import requests

class TelegramMessenger:
    """
    Gerencia o envio de mensagens para a API do Telegram.
    """
    def __init__(self, bot_token: str):
        self.telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def enviar_mensagem(self, chat_id: str, texto: str, parse_mode: str = "HTML") -> bool:
        """
        Envia uma mensagem de texto para um chat específico do Telegram.
        Retorna True em caso de sucesso, False em caso de erro.
        """
        params = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(self.telegram_api_url, data=params)
            response.raise_for_status()
            print(f"Mensagem enviada ao Telegram para chat {chat_id} com sucesso.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mensagem para o Telegram para chat {chat_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta de erro do Telegram: {e.response.text}")
            return False