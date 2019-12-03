import networkx as nx
import operator


G = nx.read_gpickle("graph/221disease.gpickle")
print(nx.info(G))

def check_keyword_exist(keywords):
    node = []
    for word in keywords:
        if G.has_node(word):
            node.append(word)
    return node

def disease_hop_activate(keywords):
    activate_list = []
    candidate = dict()
    disease = dict()
    current_hop = 0
    node_count = dict()
    node_distance = []
    sum_distance = dict()

    path = []

    for key in keywords:
        activate_list.append([key])
        path.append([])
        node_distance.append({key : 0})
               
    while len(disease) <= 10:
        for circle in range(len(activate_list)):
            activate_node = activate_list[circle][current_hop]
            
            for neighbors in nx.neighbors(G, activate_node):
                if neighbors in keywords:
                    continue

                # distance from initial point.
                if neighbors not in node_distance[circle]:
                    
                    node_distance[circle][neighbors] = node_distance[circle][activate_node] + G[activate_node][neighbors]['cost']
                    path[circle].append([activate_node, neighbors])
                    # sum distance to all keywords.
                    if neighbors in sum_distance:
                        sum_distance[neighbors] += node_distance[circle][neighbors]
                    else:
                        sum_distance[neighbors] = node_distance[circle][neighbors]
                
                # check intersect
                if neighbors in node_count:

                    if neighbors not in activate_list[circle]:
                        activate_list[circle].append(neighbors)
                        node_count[neighbors] += 1
                    
                    # if found node intersect, calculate average distance.
                    if node_count[neighbors] == len(keywords):
                        candidate[neighbors] = sum_distance[neighbors] / len(keywords)
                        if G.node[neighbors]['tag'] == 'DS':
                            disease[neighbors] = float(format(sum_distance[neighbors] / len(keywords) , '.4f'))
            
                else:
                    activate_list[circle].append(neighbors)
                    node_count[neighbors] = 1
                     

        current_hop += 1
    print(path[0])
    return dict(sorted(disease.items(), key=operator.itemgetter(1))), dict(sorted(candidate.items(), key=operator.itemgetter(1)))
