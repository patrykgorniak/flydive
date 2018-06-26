import sys
from collections import deque

def BFS(graph, depth, start, end):
    paths = []
    if start and end not in graph:
        return paths
    
    q = deque()
    temp_path = [start]
    q.append(temp_path)

    while len(q) != 0:
        tmp_path = q.popleft()
        last_node = tmp_path[len(tmp_path)-1]
        if end != "":
            if last_node == end:
                if len(tmp_path) <= depth:
                    # file.write("VALID_PATH : {}\n".format(tmp_path))
                    paths.append(tmp_path)
        else:
            if len(tmp_path) > 1 and len(tmp_path) <= depth:
                # file.write("VALID_PATH : {}\n".format(tmp_path))
                paths.append(tmp_path)

        for link_node in graph[last_node]:
            if link_node not in tmp_path:
                new_path = []
                new_path = tmp_path + [link_node]
                q.append(new_path)
                if len(new_path) > (depth + 1):
                    return paths
    # file.close()
    return paths


def findFlights(self, paths):
    pass

if __name__ == "__main__":
    depth = 4 if len(sys.argv) == 1 else int(sys.argv[-1])
    if depth > 4:
        print("WARNING! It may take a lot of time.")

    if depth < 2:
        depth = 2

    file = open("paths.txt", "w")
    paths = BFS(G.graph, depth, "WRO", "")
    paths.extend(BFS(G.graph, depth, "WAW", ""))
    paths.extend(BFS(G.graph, depth, "POZ", ""))
    for path in paths:
        file.write("{}\n".format(path))
    file.close()

