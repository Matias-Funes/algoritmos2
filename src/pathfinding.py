#este archivo contiene la implementación del algoritmo A* para la búsqueda de caminos
import heapq #este modulo proporciona una cola de prioridad eficiente

#estimación heurística (distancia Manhattan que es como una estimacion de que tan lejos esta un punto de otro)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#esto implementa el algoritmo A*Complejidad de A*:
#Tiempo: O(|E| + |V| log |V|)
#|V| = número de celdas
#|E| = número de conexiones entre celdas
#Espacio: O(|V|) para almacenar los caminos y costos
def a_star(start, goal, world):
    # start, goal = (gx, gy)
    openq = [] # Cola de prioridad de celdas a explorar
    heapq.heappush(openq, (0, start))  # Añade punto inicial. Un heap es un árbol binario especial donde cada nodo padre es menor que sus hijos.Complejidad: O(log n) para inserción y extracción
    came_from = {start: None}    # Hash table para rastrear el camino
    cost_so_far = {start: 0}  # Hash table para costos. Permite acceso O(1) a los datos. Usa hash tables para almacenar información de caminos y costos

#esto es el núcleo del algoritmo A*
    while openq:
        _, current = heapq.heappop(openq)  # Toma la celda más prometedora
        if current == goal:  # ¿Llegamos al destino?
            # Reconstruye el camino
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
#esta parte evalúa los vecinos
        for neighbor in world.get_neighbors(*current):
            new_cost = cost_so_far[current] + 1  # Costo real hasta el vecino
            # Si encontramos un mejor camino
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                # Prioridad = costo real + estimación hasta meta
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(openq, (priority, neighbor))
                came_from[neighbor] = current
    return None

