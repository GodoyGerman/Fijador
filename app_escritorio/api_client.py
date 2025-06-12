import requests

BASE_URL = "http://127.0.0.1:8000"

def listar_herramientas():
    response = requests.get(f"{BASE_URL}/herramientas/")
    response.raise_for_status()
    return response.json()

def obtener_herramienta(herramienta_id):
    response = requests.get(f"{BASE_URL}/herramientas/{herramienta_id}")
    response.raise_for_status()
    return response.json()

def crear_herramienta(data):
    response = requests.post(f"{BASE_URL}/herramientas/", json=data)
    response.raise_for_status()
    return response.json()

def actualizar_herramienta(herramienta_id, data):
    response = requests.put(f"{BASE_URL}/herramientas/{herramienta_id}", json=data)
    response.raise_for_status()
    return response.json()

def eliminar_herramienta(herramienta_id):
    response = requests.delete(f"{BASE_URL}/herramientas/{herramienta_id}")
    response.raise_for_status()
    return response.json()

def listar_categorias():
    return requests.get(f"{BASE_URL}/categorias/").json()

def listar_ubicaciones():
    return requests.get(f"{BASE_URL}/ubicaciones/").json()

def listar_responsables():
    return requests.get(f"{BASE_URL}/responsables/").json()

def registrar_movimiento(data):
    response = requests.post(f"{BASE_URL}/movimientos/", json=data)
    response.raise_for_status()
    return response.json()
