from multiprocessing import Process, Semaphore, Array
import time, random

# ---------------------------
# CONSTANTES DEL PROBLEMA
# ---------------------------
BUFFER_SIZE = 5      # Capacidad del buffer (almacén compartido)
N_ITEMS = 10         # Número de elementos a producir

# ---------------------------
# BUFFER COMPARTIDO
# ---------------------------
# Usamos un Array compartido de enteros con tamaño fijo
# Inicializamos con -1 para indicar posiciones vacías
buffer = Array('i', BUFFER_SIZE)
for i in range(BUFFER_SIZE):
    buffer[i] = -1

# ---------------------------
# SEMÁFOROS
# ---------------------------
# sem_empty = cuenta cuántos huecos libres hay en el buffer
sem_empty = Semaphore(BUFFER_SIZE)

# sem_full = cuenta cuántos ítems hay disponibles en el buffer
sem_full = Semaphore(0)

# sem_mutex = asegura EXCLUSIÓN MUTUA (solo un proceso accede al buffer a la vez)
sem_mutex = Semaphore(1)

# ---------------------------
# FUNCIÓN PRODUCTOR
# ---------------------------
def productor():
    in_index = 0  # posición donde se escribirá el próximo dato
    for i in range(N_ITEMS):
        item = random.randint(1, 100)  # producir un número aleatorio

        sem_empty.acquire()  # esperar hueco libre
        sem_mutex.acquire()  # entrar en sección crítica

        # Insertar el ítem en el buffer
        buffer[in_index] = item
        print(f"Productor produjo {item} en posición {in_index}")

        in_index = (in_index + 1) % BUFFER_SIZE  # avanzar índice circular

        sem_mutex.release()  # salir de sección crítica
        sem_full.release()   # avisar que hay un ítem disponible

        time.sleep(random.uniform(0.2, 1))  # simular tiempo de producción

    # Al final, meter un valor especial (-1) para indicar fin
    sem_empty.acquire()
    sem_mutex.acquire()
    buffer[in_index] = -1
    print("Productor terminó.")
    sem_mutex.release()
    sem_full.release()

# ---------------------------
# FUNCIÓN CONSUMIDOR
# ---------------------------
def consumidor():
    out_index = 0  # posición de lectura
    while True:
        sem_full.acquire()   # esperar hasta que haya un ítem
        sem_mutex.acquire()  # entrar en sección crítica

        item = buffer[out_index]
        buffer[out_index] = -1  # dejar el hueco vacío
        print(f"Consumidor consumió {item} de posición {out_index}")

        out_index = (out_index + 1) % BUFFER_SIZE  # avanzar índice circular

        sem_mutex.release()  # salir de sección crítica
        sem_empty.release()  # avisar que hay un hueco libre

        if item == -1:  # si recibe la señal de fin
            break

        time.sleep(random.uniform(0.2, 1))  # simular tiempo de consumo

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    # Crear procesos
    p = Process(target=productor)
    c = Process(target=consumidor)

    # Iniciar procesos
    p.start()
    c.start()

    # Esperar a que terminen
    p.join()
    c.join()

    print("Ejecución completada.")
