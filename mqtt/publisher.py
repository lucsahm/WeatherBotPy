# mqtt/publisher.py
import paho.mqtt.client as mqtt
import json

class MQTTPublisher:
    """
    Gerencia a publicação de mensagens em um broker MQTT.
    """
    def __init__(self, broker: str, port: int, topic: str):
        self.broker = broker
        self.port = port
        self.topic = topic

    def publicar_mensagem(self, payload: dict) -> bool:
        """
        Publica um payload (dicionário) no tópico MQTT configurado.
        Retorna True em caso de sucesso, False em caso de erro.
        """
        try:
            client = mqtt.Client()
            client.connect(self.broker, self.port, 60)
            client.loop_start()
            mensagem_json = json.dumps(payload, ensure_ascii=False)
            client.publish(self.topic, mensagem_json, qos=1)
            print(f'Publicado em {self.topic}: {mensagem_json}')
            client.loop_stop()
            client.disconnect()
            return True
        except Exception as e:
            print(f"Erro ao publicar no MQTT: {e}")
            return False