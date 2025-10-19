import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, world):
    # start, goal = (gx, gy)
    openq = []
    heapq.heappush(openq, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while openq:
        _, current = heapq.heappop(openq)
        if current == goal:
            # reconstruct path
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in world.get_neighbors(*current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(openq, (priority, neighbor))
                came_from[neighbor] = current
    return None