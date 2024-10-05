from django.apps import AppConfig
import threading
from .consumer import start_payment_consumer

class PagosConfig(AppConfig):
    name = 'pagos'

    def ready(self):
        # Inicia el consumidor en un hilo separado
        threading.Thread(target=start_payment_consumer, daemon=True).start()
