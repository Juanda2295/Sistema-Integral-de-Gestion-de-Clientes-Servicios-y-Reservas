# Juan David Mejia Vides
# Fase 4 - Componente práctico
# Programación
# 2026-07-06

import logging
from abc import ABC, abstractmethod
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS (Manejo de archivos para eventos)
# ==============================================================================
logging.basicConfig(
    filename='software_fj_sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==============================================================================
# 2. ARQUITECTURA DE EXCEPCIONES PERSONALIZADAS
# ==============================================================================
class SoftwareFJException(Exception):
    """Clase base para excepciones del sistema."""
    pass

class ClienteInvalidoError(SoftwareFJException):
    """Se lanza cuando los datos del cliente no cumplen las validaciones."""
    pass

class ServicioNoDisponibleError(SoftwareFJException):
    """Se lanza cuando un servicio no cuenta con los parámetros o disponibilidad."""
    pass

class ReservaInvalidaError(SoftwareFJException):
    """Se lanza cuando la reserva viola reglas de negocio."""
    pass

# ==============================================================================
# 3. MODELADO DE CLASES (Abstracción, Encapsulación y Herencia)
# ==============================================================================
class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self):
        return self._id_entidad


class Cliente(EntidadSistema):
    """Clase Cliente con encapsulación estricta y validaciones."""
    def __init__(self, id_cliente, nombre, correo):
        super().__init__(id_cliente)
        self.nombre = nombre   
        self.correo = correo   

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise ClienteInvalidoError(f"El correo '{valor}' no tiene un formato válido.")
        self._correo = valor

    def __str__(self):
        return f"Cliente ID: {self.id_entidad} | Nombre: {self.nombre}"


# ==============================================================================
# 4. JERARQUÍA DE SERVICIOS (Polimorfismo y Métodos Sobrescritos)
# ==============================================================================
class Servicio(ABC):
    """Clase abstracta base para los servicios de Software FJ."""
    def __init__(self, codigo, nombre_servicio, costo_base):
        self.codigo = codigo
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base

    @abstractmethod
    def calcular_costo(self, unidades, **kwargs):
        pass

    @abstractmethod
    def obtener_descripcion(self):
        pass


class ReservaSala(Servicio):
    """Servicio 1: Reserva de salas físicas de reuniones por horas."""
    def __init__(self, codigo, nombre_servicio, costo_base, capacidad_maxima):
        super().__init__(codigo, nombre_servicio, costo_base)
        self.capacidad_maxima = capacidad_maxima

    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19):
        if horas <= 0:
            raise ServicioNoDisponibleError("Las horas de reserva deben ser mayores a cero.")
        subtotal = self.costo_base * horas
        total = subtotal - (subtotal * descuento)
        total += total * impuesto
        return total

    def obtener_descripcion(self):
        return f"Sala: {self.nombre_servicio} (Capacidad máx: {self.capacidad_maxima} personas)"


class AlquilerEquipos(Servicio):
    """Servicio 2: Alquiler de hardware/computadores por días."""
    def __init__(self, codigo, nombre_servicio, costo_base, stock_disponible):
        super().__init__(codigo, nombre_servicio, costo_base)
        self.stock_disponible = stock_disponible

    def calcular_costo(self, dias, cantidad_equipos=1):
        if cantidad_equipos > self.stock_disponible:
            raise ServicioNoDisponibleError(f"No hay suficientes equipos. Stock: {self.stock_disponible}")
        if dias <= 0:
            raise ServicioNoDisponibleError("La duración del alquiler debe ser de al menos 1 día.")
        return self.costo_base * dias * cantidad_equipos

    def obtener_descripcion(self):
        return f"Equipo: {self.nombre_servicio} (Disponibles: {self.stock_disponible})"


class AsesoriaEspecializada(Servicio):
    """Servicio 3: Mentorías de desarrollo o arquitectura de software."""
    def __init__(self, codigo, nombre_servicio, costo_base, consultor_asignado):
        super().__init__(codigo, nombre_servicio, costo_base)
        self.consultor_asignado = consultor_asignado

    def calcular_costo(self, sesiones, es_cliente_vip=False):
        if sesiones <= 0:
            raise ServicioNoDisponibleError("Debe agendar al menos 1 sesión de asesoría.")
        descuento = 0.15 if es_cliente_vip else 0.0
        costo = self.costo_base * sesiones
        return costo * (1 - descuento)

    def obtener_descripcion(self):
        return f"Asesoría de TI con el consultor: {self.consultor_asignado}"


# ==============================================================================
# 5. GESTIÓN DE RESERVAS CON MANEJO AVANZADO DE EXCEPCIONES
# ==============================================================================
class Reserva:
    """Clase que integra Cliente, Servicio, duración y estado con flujos de control."""
    def __init__(self, id_reserva, cliente, servicio, duracion, **kwargs):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.kwargs = kwargs
        self.estado = "Pendiente"
        self.costo_total = 0.0

    def procesar_reserva(self):
        print(f"-> Procesando Reserva #{self.id_reserva}...")
        try:
            if not isinstance(self.cliente, Cliente):
                raise ReservaInvalidaError("La reserva no contiene un objeto Cliente válido.")
            if not isinstance(self.servicio, Servicio):
                raise ReservaInvalidaError("La reserva no contiene un objeto Servicio válido.")
            
            self.costo_total = self.servicio.calcular_costo(self.duracion, **self.kwargs)
            
        except (ClienteInvalidoError, ServicioNoDisponibleError, ReservaInvalidaError) as ex:
            self.estado = "Fallida"
            mensaje_error = f"Error controlado en Reserva #{self.id_reserva}: {str(ex)}"
            logging.error(mensaje_error)
            raise ReservaInvalidaError(mensaje_error) from ex
            
        except Exception as e:
            self.estado = "Error Interno"
            logging.critical(f"Error inesperado en Reserva #{self.id_reserva}: {str(e)}")
            raise SoftwareFJException("Error imprevisto de la infraestructura interna.") from e
            
        else:
            self.estado = "Confirmada"
            mensaje_exito = f"   Reserva #{self.id_reserva} EXITOSA. Total: ${self.costo_total:.2f}"
            print(mensaje_exito)
            logging.info(mensaje_exito)
            
        finally:
            print(f"   Chequeo de Reserva #{self.id_reserva} finalizado. Estado final: [ {self.estado} ]")


# ==============================================================================
# 6. BANCO DE PRUEBAS (Simulación de 10 Operaciones en Memoria)
# ==============================================================================
def ejecutar_simulacion():
    print("=== INICIANDO SIMULACIÓN DE 10 OPERACIONES EN SOFTWARE FJ ===")
    logging.info("--- Iniciando lote de simulación universitaria ---")

    # Instanciación de servicios bases para usar en las operaciones
    sala_reunion = ReservaSala("SR01", "Sala de Juntas Premium", 50000, capacidad_maxima=12)
    computadores = AlquilerEquipos("AE01", "Laptops Dev i7", 35000, stock_disponible=5)
    asesoria_ai = AsesoriaEspecializada("AS01", "Consultoría Arquitectura AI", 120000, "Ing. Carlos Mendoza")

    # Creación de un cliente base válido para usar en reservas de prueba
    cliente_base_valido = Cliente("C100", "Carlos Restrepo", "carlos@email.com")

    # -------------------------------------------------------------------------
    print("\n[Op 1] Intentando crear cliente válido...")
    try:
        c1 = Cliente("C001", "Juan Pérez", "juan.perez@email.com")
        print(f"   Éxito: {c1}")
    except ClienteInvalidoError as e:
        print(f"   Error: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 2] Intentando crear cliente con nombre inválido...")
    try:
        c2 = Cliente("C002", "Al", "al@email.com")
        print(f"   Éxito: {c2}")
    except ClienteInvalidoError as e:
        print(f"   Excepción controlada con éxito: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 3] Intentando crear cliente con correo sin estructura...")
    try:
        c3 = Cliente("C003", "Andrés Gómez", "andresgomez_email.com")
        print(f"   Éxito: {c3}")
    except ClienteInvalidoError as e:
        print(f"   Excepción controlada con éxito: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 4] Reserva Exitosa - Uso de Sala con descuento del 10%")
    try:
        r1 = Reserva(4, cliente_base_valido, sala_reunion, duracion=4, descuento=0.10)
        r1.procesar_reserva()
    except ReservaInvalidaError as e:
        print(f"   La reserva falló de manera controlada: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 5] Reserva Fallida - Horas negativas en sala (Datos inválidos)")
    try:
        r2 = Reserva(5, cliente_base_valido, sala_reunion, duracion=-2)
        r2.procesar_reserva()
    except ReservaInvalidaError as e:
        print(f"   Aviso capturado en simulación: {e.args[0]}")

    # -------------------------------------------------------------------------
    print("\n[Op 6] Reserva Exitosa - Alquiler de Equipos Estándar")
    try:
        r3 = Reserva(6, cliente_base_valido, computadores, duracion=3, cantidad_equipos=2)
        r3.procesar_reserva()
    except Exception as e:
        print(f"   Error en simulación: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 7] Reserva Fallida - Alquiler supera Stock disponible (Operación no permitida)")
    try:
        r4 = Reserva(7, cliente_base_valido, computadores, duracion=5, cantidad_equipos=10) 
        r4.procesar_reserva()
    except ReservaInvalidaError as e:
        print(f"   Aviso capturado en simulación: {e.args[0]}")

    # -------------------------------------------------------------------------
    print("\n[Op 8] Reserva Exitosa - Asesoría Especializada aplicando tarifa VIP")
    try:
        r5 = Reserva(8, cliente_base_valido, asesoria_ai, duracion=2, es_cliente_vip=True)
        r5.procesar_reserva()
    except Exception as e:
        print(f"   Error en simulación: {e}")

    # -------------------------------------------------------------------------
    print("\n[Op 9] Reserva Fallida - Inyección de un String en lugar de un objeto Cliente")
    try:
        r6 = Reserva(9, "Texto corrupto no objeto", asesoria_ai, duracion=1)
        r6.procesar_reserva()
    except ReservaInvalidaError as e:
        print(f"   Aviso capturado en simulación: {e.args[0]}")

    # -------------------------------------------------------------------------
    print("\n[Op 10] Reserva Fallida - Sesiones de Asesoría en cero (Cálculo inconsistente)")
    try:
        r7 = Reserva(10, cliente_base_valido, asesoria_ai, duracion=0)
        r7.procesar_reserva()
    except ReservaInvalidaError as e:
        print(f"   Aviso capturado en simulación: {e.args[0]}")

    print("\n=== SIMULACIÓN FINALIZADA SIN CAÍDAS DEL SISTEMA ===")
    print("El archivo 'software_fj_sistema.log' ha registrado todas las auditorías en la carpeta del proyecto.")

# Lanzador del script principal
if __name__ == "__main__":
    ejecutar_simulacion()