# api/clima.py
import requests
from datetime import datetime, timedelta


class ClimaAPI:
    """
    Gerencia a obtenção de dados de clima atual e previsão do OpenWeatherMap.
    """

    def __init__(self, api_key: str, city: str):
        self.api_key = api_key
        self.city = city
        self.base_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.base_forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

    def obter_dados_clima_atual(self) -> dict | None:
        """
        Obtém os dados do clima atual para a cidade configurada.
        Retorna um dicionário com os dados ou None em caso de erro.
        """
        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "pt_br"
        }
        try:
            response = requests.get(self.base_weather_url, params=params)
            response.raise_for_status()
            data = response.json()

            velocidade_vento_ms = data['wind']['speed']
            velocidade_vento_kmh = round(velocidade_vento_ms * 3.6, 2)

            clima = {
                'cidade': data.get('name'),
                'temperatura': data['main']['temp'],
                'sensacao': data['main']['feels_like'],
                'umidade': data['main']['humidity'],
                'vento': f"{velocidade_vento_kmh} km/h",
                'descricao': data['weather'][0]['description']
            }
            return clima
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ao obter clima atual do OpenWeatherMap: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao processar dados do clima atual: {e}")
            return None

    def obter_previsao_detalhada(self, horas: int) -> str:
        """
        Obtém e formata a previsão para as próximas X horas.
        Retorna uma string formatada com a previsão ou uma mensagem de erro.
        """
        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "pt_br"
        }
        try:
            response = requests.get(self.base_forecast_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "list" not in data:
                return "Erro: dados de previsão não encontrados na resposta da API."

            texto_previsao_linhas = []
            blocos = min(horas // 3, len(data["list"]))

            for i in range(blocos):
                bloco = data["list"][i]

                utc_dt = datetime.strptime(bloco["dt_txt"], '%Y-%m-%d %H:%M:%S')
                local_dt = utc_dt - timedelta(hours=3)  # Ajuste manual para GMT-3
                hora = local_dt.strftime('%H:%M')

                temp = bloco["main"]["temp"]
                sensacao = bloco["main"]["feels_like"]
                descricao = bloco["weather"][0]["description"]
                umidade = bloco["main"]["humidity"]
                vento_ms = bloco["wind"]["speed"]
                vento_kmh = vento_ms * 3.6

                texto_previsao_linhas.append(
                    f"<b>Horário:</b> {hora}\n"
                    f"🌡️ Temperatura: {temp:.1f}°C (sensação {sensacao:.1f}°C)\n"
                    f"☁️ Condição: {descricao.capitalize()}\n"
                    f"💧 Umidade: {umidade}%\n"
                    f"💨 Vento: {vento_kmh:.1f} km/h\n"
                    "--------------------"
                )
            return "\n".join(texto_previsao_linhas).strip()

        except requests.exceptions.RequestException as e:
            return f"Erro de conexão ao obter previsão do OpenWeatherMap: {e}"
        except Exception as e:
            return f"Erro inesperado ao processar dados da previsão: {e}"