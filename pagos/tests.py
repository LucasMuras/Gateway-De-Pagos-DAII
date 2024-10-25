from django.test import TestCase
from django.http import JsonResponse

class GatewayDePagosTest(TestCase):
    def setUp(self):
        self.data_payment = {
            "en_cuotas": False,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 1,
            "dni": "11111111",
            "numero": "4234567890000000",
            "fecha_vencimiento": "2025-09-11",
            "cvv": "123",
            "tipo_tarjeta": "Visa",
            "nombre_titular": "RODRIGO NUTRIALES"
        }

        self.data_payment_quotas = {
            "en_cuotas": True,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 3,
            "dni": "11111111",
            "numero": "4234567890000000",
            "fecha_vencimiento": "2025-09-11",
            "cvv": "123",
            "tipo_tarjeta": "Visa",
            "nombre_titular": "RODRIGO NUTRIALES"
        }

        self.data_payment_invalid_card_nonexistent = {
            "en_cuotas": False,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 1,
            "dni": "44444444",
            "numero": "4111111111119876",
            "fecha_vencimiento": "2025-12-31",
            "cvv": "145",
            "tipo_tarjeta": "Visa",
            "nombre_titular": "MARTINA GONZALES"
        }
        
        self.data_payment_invalid_card_expired = {
            "en_cuotas": False,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 1,
            "dni": "33333333",
            "numero": "5837492740922846",
            "fecha_vencimiento": "2022-12-10",
            "cvv": "133",
            "tipo_tarjeta": "Mastercard",
            "nombre_titular": "FERNANDA CUCHO"
        }

        self.data_payment_invalid_card_inactive = {
            "en_cuotas": False,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 1,
            "dni": "22222222",
            "numero": "4111111111111111",
            "fecha_vencimiento": "2025-12-31",
            "cvv": "120",
            "tipo_tarjeta": "Visa",
            "nombre_titular": "MARTINA GONZALES"
        }

        self.data_payment_invalid_insufficient_balance = {
            "en_cuotas": False,
            "tipo_metodo_pago": "tarjeta",
            "cantidad_cuotas": 1,
            "dni": "44444444",
            "numero": "5555555555554444",
            "fecha_vencimiento": "2027-08-08",
            "cvv": "256",
            "tipo_tarjeta": "Mastercard",
            "nombre_titular": "ROGELIO DOMINGUEZ"
        }


    # Caso de uso: pagar una reserva. Una cuota. Tarjeta válida. Camino exitoso.
    def test_endpoint_pago_exitoso(self):
        response = self.client.post('/pagos/pago/', self.data_payment, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        #print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 200)
        #self.assertEqual({'status': 'Transacción exitosa'})
        #print("Test de pago completado con éxito.\n")

    # Caso de uso: pagar una reserva. Con cuotas. Tarjeta válida. Camino exitoso.
    def test_endpoint_pago_exitoso_cuotas(self):
        response = self.client.post('/pagos/pago/', self.data_payment_quotas, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        #print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.json(), {'status': 'Transacción exitosa'})
        #print("Test de pago completado con éxito.\n")

    # Caso de uso: pagar una reserva. Una cuota. Tarjeta inválida - inexistente.
    def test_endpoint_pago_fallido_tarjeta_inexistente(self):
        response = self.client.post('/pagos/pago/', self.data_payment_invalid_card_nonexistent, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        #print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 400)
        #self.assertEqual(response.json(), {'status': 'Transacción fallida'})
        #print("Test de pago completado con éxito.\n")

    # Caso de uso: pagar una reserva. Una cuota. Tarjeta inválida - inactiva.
    def test_endpoint_pago_fallido_tarjeta_inactiva(self):
        response = self.client.post('/pagos/pago/', self.data_payment_invalid_card_inactive, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'status': 'Transacción fallida'})
        print("Test de pago completado con éxito.\n")

    # Caso de uso: pagar una reserva. Una cuota. Tarjeta inválida - expirada.
    def test_endpoint_pago_fallido_tarjeta_expirada(self):
        response = self.client.post('/pagos/pago/', self.data_payment_invalid_card_expired, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'status': 'Transacción fallida'})
        print("Test de pago completado con éxito.\n")

    # Caso de uso: pagar una reserva. Una cuota. Saldo insuficiente.
    def test_endpoint_pago_fallido_saldo_insuficiente(self):
        response = self.client.post('/pagos/pago/', self.data_payment_invalid_insufficient_balance, content_type='application/json')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Pago): {response.status_code}")
        print(f"Response JSON (Pago): {response.json()}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'status': 'Transacción fallida'})
        print("Test de pago completado con éxito.\n")

    # Caso de uso: cancelación de una reserva. Reembolso.
    def test_endpoint_reembolso(self):
        response = self.client.post('/pagos/reembolso/')
        # Verificar el estado de la respuesta
        print(f"\nResponse status (Reembolso): {response.status_code}")
        print(f"Response JSON (Reembolso): {response.json()}")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'status': 'Transacción exitosa'})
        print("Test de reembolso completado con éxito.\n")