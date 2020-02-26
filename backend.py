import networkx as nx
import operator
import random
import math 

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
    sum_path = dict()
    
    path = []
    for key in keywords:
        activate_list.append([key])
        node_distance.append({key : 0})
        path.append({key:[key]})
        
    while len(disease) <= 10:
        
        for circle in range(len(activate_list)):
            activate_node = activate_list[circle][current_hop]
            
            for neighbor in nx.neighbors(G, activate_node):
                if neighbor in keywords:
                    continue

                # distance from initial point.
                if neighbor not in node_distance[circle]:
                    
                    node_distance[circle][neighbor] = node_distance[circle][activate_node] + G[activate_node][neighbor]['cost']
                    
                    prev_path = path[circle][activate_node]
                    current_path = prev_path + [neighbor]
                    path[circle][neighbor] = current_path
                    
                    # sum distance to all keywords.
                    if neighbor in sum_distance:
                        sum_distance[neighbor] += node_distance[circle][neighbor]
                        sum_path[neighbor] += 1
                    else:
                        sum_distance[neighbor] = node_distance[circle][neighbor]
                        sum_path[neighbor] = 1

                
                # check intersect
                if neighbor in node_count:

                    if neighbor not in activate_list[circle]:
                        activate_list[circle].append(neighbor)
                        node_count[neighbor] += 1
                    
                    # if found node intersect, calculate average distance.
                    if node_count[neighbor] == len(keywords):
                        candidate[neighbor] = sum_distance[neighbor] / len(keywords)
                        if G.node[neighbor]['tag'] == 'DS' or G.node[neighbor]['tag'] == 'DT':
                            disease[neighbor] = float(format(sum_distance[neighbor] / len(keywords) , '.4f'))
            
                else:
                    activate_list[circle].append(neighbor)
                    node_count[neighbor] = 1
                     

        current_hop += 1
    
    return dict(sorted(disease.items(), key=operator.itemgetter(1))), dict(sorted(candidate.items(), key=operator.itemgetter(1))), path, sum_path

def get2node_path(source, target):
    activate_node = [source]
    node_path = {source:[source]}
    node_distance = {source:0}
    found_target = False

  
    for an in activate_node:
        
        for nb in nx.neighbors(G, an):
            if nb not in node_path:
                activate_node.append(nb)
                # path
                prev_path = node_path[an]
                current_path = prev_path + [nb]
                node_path[nb] = current_path

                #distance
                node_distance[nb] = node_distance[an] + G[an][nb]['cost']
            
                if nb == target:
                    found_target = True

        if found_target:
            break

    return node_path[target], node_distance[target]
   
def create_graph(disease, path, centroid):
    node = [] # [{name: node}]
    edge = [] # [{source: node1, target: node2}]
    node_index = dict()
    temp_path = [] # [[path1], [n]]
    index_id = 0
 
    # Store node info
    # iterate disease list
    for d in disease:
        # path of each keyword to disease --> [{from symptom1}, {n}]
        for index in range(len(path)):
            # check if disease have path to current symptom list.
            if d in path[index]:
                # keep path list for edge info.
                temp_path.append(path[index][d])
                # iterate node from source to target and store to node list.
                for p in path[index][d]:
                    if p not in node_index:
                        color= None
                                             
                        # color
                        if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                            color = 'red'
                        elif G.node[p]['tag'] == 'ST':
                            color = 'yellow'
                        else :
                            color = 'blue'
                                                 
                        node_index[p] = index_id
                        node.append({'name': p , 'color':color})
                        index_id += 1

    d_list = list(disease)
    # Link between disease
    for d1 in range(len(d_list)):
        for d2 in range(d1+1, len(d_list)):
            getpath, distance = get2node_path(d_list[d1], d_list[d2])
            temp_path.append(getpath)
            # add node
            for n in getpath:
                if n not in node_index:
                    color= None
                    if G.node[n]['tag'] == 'DS' or G.node[n]['tag'] == 'DT':
                        color = 'red'
                    elif G.node[n]['tag'] == 'ST':
                        color = 'yellow'
                    else :
                        color = 'blue'
                        
                    node_index[n] = index_id
                    node.append({'name': n , 'color':color})
                    index_id += 1

    # Set postition (x, y)
    node = node_position(node, centroid)
 
    # Store edge info
    check_edge = [] # for check if edge already exist
    # iterate path
    for p in temp_path:
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
                if pair not in check_edge:
                    edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]]})
                    check_edge.append(pair)
    
    return node, edge

def node_position(node, centroid):
    xc = 275
    yc = 275
    node_size = 10
    circle_coordinates = {
        'circle1':{'x1':225,'x2':325,'y1':225,'y2':325,'r':50},
        'circle2':{'x1':125,'x2':425,'y1':125,'y2':425,'r':150},
        'circle3':{'x1':75,'x2':475,'y1':75,'y2':475,'r':200},
        'circle4':{'x1':0,'x2':550,'y1':0,'y2':550,'r':275},
    }
    color = {
        'red':'rgba(247, 32, 32, 1)',
        'yellow':'rgba(172, 247, 32)',
        'blue':'rgba(2, 69, 255)'
    }
    node_pos = []

    for n in node:
        x = None
        y = None
      
        # circle 1 (inside) centroid fixed
        if n['name'] == centroid:
            if n['color'] == 'red':
                n['rgba'] = color['red']
            elif n['color'] == 'yellow':
                n['rgba'] = color['yellow']
            else:
                n['rgba'] = color['blue']

            x = xc
            y = yc

        # circle 2
        elif n['color'] == 'red':
            n['rgba'] = color['red']
            x1 = circle_coordinates['circle2']['x1']
            x2 = circle_coordinates['circle2']['x2']
            y1 = circle_coordinates['circle2']['y1']
            y2 = circle_coordinates['circle2']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle1']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle2']['r']:
                    # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break
        # circle 3
        elif n['color'] == 'yellow':
            n['rgba'] = color['yellow']
            x1 = circle_coordinates['circle3']['x1']
            x2 = circle_coordinates['circle3']['x2']
            y1 = circle_coordinates['circle3']['y1']
            y2 = circle_coordinates['circle3']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle2']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle3']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break

         # circle 4 (outside)
        elif n['color'] == 'blue':
            n['rgba'] = color['blue']
            x1 = circle_coordinates['circle4']['x1']
            x2 = circle_coordinates['circle4']['x2']
            y1 = circle_coordinates['circle4']['y1']
            y2 = circle_coordinates['circle4']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle3']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size*2 < circle_coordinates['circle4']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break
        n['x'] = x
        n['y'] = y
        n['fixed'] = True

    return node
      
def centroid_shotest_path(diseases, symptoms, centroid):
    sp_path = dict()
    lenght, path = nx.single_source_dijkstra(G, centroid, weight='cost')
  
    for s in symptoms:
        if s in path:
            sp_path[s] = path[s]
    for d in diseases:
        if d in path:
            sp_path[d] = path[d]
   
    return sp_path, path, lenght

def create_graph_sp(disease, path, centroid):
    node = [] # [{name: node}]
    edge = [] # [{source: node1, target: node2}]
    node_index = dict()
    temp_path = [] # [[path1], [n]]
    index_id = 0

    # Store node info
    # iterate disease list
    for d in path:
        # check if disease have path to current symptom list.
        temp_path.append(path[d])
        # iterate node from source to target and store to node list.
        for p in path[d]:
            if p not in node_index:
                color= None
                                        
                # color
                if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                    color = 'red'
                elif G.node[p]['tag'] == 'ST':
                    color = 'yellow'
                else :
                    color = 'blue'
                                            
                node_index[p] = index_id
                node.append({'name': p , 'color':color})
                index_id += 1

    d_list = list(disease)

    # Link between disease
    for d1 in range(len(d_list)):
        for d2 in range(d1+1, len(d_list)):
            getpath, distance = get2node_path(d_list[d1], d_list[d2])
            temp_path.append(getpath)
            # add node
            for n in getpath:
                if n not in node_index:
                    color= None
                    if G.node[n]['tag'] == 'DS' or G.node[n]['tag'] == 'DT':
                        color = 'red'
                    elif G.node[n]['tag'] == 'ST':
                        color = 'yellow'
                    else :
                        color = 'blue'
                        
                    node_index[n] = index_id
                    node.append({'name': n , 'color':color})
                    index_id += 1

    # Set postition (x, y)
    node = node_position(node, centroid)
 
    # Store edge info
    check_edge = [] # for check if edge already exist.
    # iterate path
    for p in temp_path:
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
                if pair not in check_edge:
                    line_color = None
                    # line from red node to yellow node.
                    if node[node_index[p[source]]]['color'] == 'red' and node[node_index[p[target]]]['color'] == 'yellow' \
                        or node[node_index[p[source]]]['color'] == 'yellow' and node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'red'
                    # line from red node to blue node.
                    elif node[node_index[p[source]]]['color'] == 'red' and node[node_index[p[target]]]['color'] == 'blue' \
                        or node[node_index[p[source]]]['color'] == 'blue' and node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'deepSkyBlue'
                    # line from yellow node to blue node.
                    elif node[node_index[p[source]]]['color'] == 'yellow' and node[node_index[p[target]]]['color'] == 'blue' \
                        or node[node_index[p[source]]]['color'] == 'blue' and node[node_index[p[target]]]['color'] == 'yellow':
                        line_color = 'yellow'
                    else:
                        line_color = 'white'
                    edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]], 'color':line_color})
                    check_edge.append(pair)
    
    return node, edge

def document_content(node):
    try:
        doc = G.node[node]['document']
        if "'s" in doc:
            doc = doc.replace("'s", "")
        text_file = 'static/Wiki/'+doc
        return text_file
    except:
        return None

def node_symptoms_graph(node):

    path = nx.single_source_dijkstra_path(G, node, weight='cost')
    closest_symptoms = dict()
    limit = 10

    # store first closest 10 symptoms
    for p in path:
        if G.node[p]['tag'] == 'ST':
            closest_symptoms[p] = path[p]
        if len(closest_symptoms) >= limit:
            break

    #D3 Graph variable
    # Node variable
    graph_node = []
    node_index=dict()
    index_id = 0
    #  closest_symptoms = {'s':['n1','n2']}
    for c in closest_symptoms:

        #  closest_symptoms[c] = ['n1','n2']
        for cvalue in closest_symptoms[c]:

            if cvalue not in node_index:
                color= None
                if G.node[cvalue]['tag'] == 'DS' or G.node[cvalue]['tag'] == 'DT':
                    color = 'red'
                elif G.node[cvalue]['tag'] == 'ST':
                    color = 'yellow'
                else :
                    color = 'blue'
                node_index[cvalue] = index_id
                graph_node.append({'name': cvalue , 'color':color})
                index_id += 1

    #   set node postition (x, y)
    centroid = node
    graph_node = node_position(graph_node, centroid)

    # Edge variable
    graph_edge = []
    check_edge = [] # for check if edge already exist.
    # iterate path
    for c in closest_symptoms:
        p = closest_symptoms[c]
   
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
                if pair not in check_edge:
                    line_color = None
                    # line from red node to yellow node.
                    if graph_node[node_index[p[source]]]['color'] == 'red' and graph_node[node_index[p[target]]]['color'] == 'yellow' \
                        or graph_node[node_index[p[source]]]['color'] == 'yellow' and graph_node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'red'
                    # line from red node to blue node.
                    elif graph_node[node_index[p[source]]]['color'] == 'red' and graph_node[node_index[p[target]]]['color'] == 'blue' \
                        or graph_node[node_index[p[source]]]['color'] == 'blue' and graph_node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'deepSkyBlue'
                    # line from yellow node to blue node.
                    elif graph_node[node_index[p[source]]]['color'] == 'yellow' and graph_node[node_index[p[target]]]['color'] == 'blue' \
                        or graph_node[node_index[p[source]]]['color'] == 'blue' and graph_node[node_index[p[target]]]['color'] == 'yellow':
                        line_color = 'yellow'
                    else:
                        line_color = 'white'
                    graph_edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]], 'color':line_color})
                    check_edge.append(pair)
                    
    return graph_node, graph_edge

# not use
def all_path_graph(path, pathcost, centroid):
    node = [] # [{name: node}]
    edge = [] # [{source: node1, target: node2}]
    node_index = dict()
    index_id = 0

    # Graph Nodes
    for p in path:
        if p not in node_index:
            color= None
                                    
            # color
            if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                color = 'red'
            elif G.node[p]['tag'] == 'ST':
                color = 'yellow'
            else:
                color = 'blue'
                                        
            node_index[p] = index_id
            node.append({'name': p , 'color':color, 'cost':pathcost[p]})
            index_id += 1

    # Set postition (x, y)
    node = node_position(node, centroid)

    # Graph Edges
    check_edge = [] # for check if edge already exist.
    # iterate path
    for p in path:
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
            
                if pair not in check_edge:
                    edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]]})
                    check_edge.append(pair)
 
    return node, edge

def nodes_in_distance(centroid, org_nodes, org_edges, cost):
    lenght, path = nx.single_source_dijkstra(G, centroid, weight='cost', cutoff=cost)
    neigbors_amount = len(lenght)
    print("distance :", cost, " neighbors : ", neigbors_amount)

    node = [] # [ {name: node, 'color': 'blue', 'rgba': 'rgba(2, 69, 255)', 'x': 423, 'y': 437, 'fixed': True} ]
    edge = [] # [ {source: node1, target: node2} ]
    node_index = dict()
    index_id = 0

    # Graph Nodes
    for p in path:
        if p not in node_index:
            color= None
                                    
            # color
            if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                color = 'red'
            elif G.node[p]['tag'] == 'ST':
                color = 'yellow'
            else:
                color = 'blue'
                                        
            node_index[p] = index_id
            node.append({'name': p , 'color':color})
            index_id += 1
            
    # Set postition (x, y)
    node = node_position_intersect(node, centroid)

    # add initial nodes
    for orn in org_nodes:
        # if node from neighbors calculation duplicate with orignal node, set original pos(x, y) to that node.
        if orn['name'] in node_index:
            i = node_index[orn['name']]
            node[i]['x'] = orn['x']
            node[i]['y'] = orn['y']

        # add original node with original position
        else:
            node_index[orn['name']] = index_id
            node.append(orn)
            index_id += 1
    # Graph Edges
    check_edge = [] # for check if edge already exist.
    # iterate path
    for p in path:
        for source in range(len(path[p])):
            for target in range(source + 1, len(path[p])):
                pair = sorted([path[p][source], path[p][target]])
                if pair not in check_edge:
                    line_color = None
                    # line from red node to yellow node.
                    if node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'yellow' \
                        or node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'red':
                        line_color = 'red'
                    # line from red node to blue node.
                    elif node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'blue' \
                        or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'red':
                        line_color = 'deepSkyBlue'
                    # line from yellow node to blue node.
                    elif node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'blue' \
                        or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'yellow':
                        line_color = 'yellow'
                    else:
                        line_color = 'white'
                    edge.append({'source' : node_index[path[p][source]], 'target' :  node_index[path[p][target]], 'color':line_color})
                    check_edge.append(pair)

    # add original edges if not aready added
    for ore in org_edges:
        pair = sorted([org_nodes[ore['source']]['name'], org_nodes[ore['target']]['name']])
        if pair not in check_edge:
            # node_index['name'] = id
            # org_nodes['name'] = 'dengue_fever'
            # ore['source'] = node index
            # --> node_index[org_nodes[id]['name']]
            source_id = node_index[org_nodes[ore['source']]['name']]
            target_id = node_index[org_nodes[ore['target']]['name']]
            line_color = None
            # line from red node to yellow node.
            if node[source_id]['color'] == 'red' and node[target_id]['color'] == 'yellow' \
                or node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'red':
                line_color = 'red'
            # line from red node to blue node.
            elif node[source_id]['color'] == 'red' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'red':
                line_color = 'deepSkyBlue'
            # line from yellow node to blue node.
            elif node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'yellow':
                line_color = 'yellow'
            else:
                line_color = 'white'
                       
            edge.append({'source' : source_id, 'target' :  target_id, 'color': line_color})
            check_edge.append(pair)
    print("done")
    return node, edge

# set nodes position without check nodes overlap
def node_position_intersect(node, centroid):
    xc = 275
    yc = 275
    node_size = 10
    circle_coordinates = {
        'circle1':{'x1':225,'x2':325,'y1':225,'y2':325,'r':50},
        'circle2':{'x1':125,'x2':425,'y1':125,'y2':425,'r':150},
        'circle3':{'x1':75,'x2':475,'y1':75,'y2':475,'r':200},
        'circle4':{'x1':0,'x2':550,'y1':0,'y2':550,'r':275},
    }
    color = {
        'red':'rgba(247, 32, 32, 1)',
        'yellow':'rgba(172, 247, 32)',
        'blue':'rgba(2, 69, 255)'
    }
    node_pos = []

    for n in node:
        x = None
        y = None
      
        # circle 1 (inside) centroid fixed
        if n['name'] == centroid:
            if n['color'] == 'red':
                n['rgba'] = color['red']
            elif n['color'] == 'yellow':
                n['rgba'] = color['yellow']
            else:
                n['rgba'] = color['blue']

            x = xc
            y = yc

        # circle 2
        elif n['color'] == 'red':
            n['rgba'] = color['red']
            x1 = circle_coordinates['circle2']['x1']
            x2 = circle_coordinates['circle2']['x2']
            y1 = circle_coordinates['circle2']['y1']
            y2 = circle_coordinates['circle2']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle1']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle2']['r']:
                    # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    #if not intersect:
                    if True:
                        node_pos.append({'x':x, 'y':y})
                        break
        # circle 3
        elif n['color'] == 'yellow':
            n['rgba'] = color['yellow']
            x1 = circle_coordinates['circle3']['x1']
            x2 = circle_coordinates['circle3']['x2']
            y1 = circle_coordinates['circle3']['y1']
            y2 = circle_coordinates['circle3']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle2']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle3']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    #if not intersect:
                    if True:
                        node_pos.append({'x':x, 'y':y})
                        break

         # circle 4 (outside)
        elif n['color'] == 'blue':
            n['rgba'] = color['blue']
            x1 = circle_coordinates['circle4']['x1']
            x2 = circle_coordinates['circle4']['x2']
            y1 = circle_coordinates['circle4']['y1']
            y2 = circle_coordinates['circle4']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle3']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size*2 < circle_coordinates['circle4']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    #if not intersect:
                    if True:
                        node_pos.append({'x':x, 'y':y})
                        break
        n['x'] = x
        n['y'] = y
        n['fixed'] = True

    return node

# display direct connected nodes
def get_direct_connected_nodes(selectednode, nodes, edges):
    direct_nodes = []
    direct_edges = []
    node_index = dict()
    node_id = 0

    for e in edges:
        if nodes[e['source']]['name'] == selectednode or nodes[e['target']]['name'] == selectednode:
            direct_nodes.append(nodes[e['source']])
            node_index[nodes[e['source']]['name']] = node_id
            node_id += 1
            direct_nodes.append(nodes[e['target']])
            node_index[nodes[e['target']]['name']] = node_id
            node_id += 1

            line_color = None
            # line from red node to yellow node.
            if nodes[e['source']]['color']  == 'red' and nodes[e['target']]['color']  == 'yellow' \
                or nodes[e['source']]['color']  == 'yellow' and nodes[e['target']]['color'] == 'red':
                line_color = 'red'
            # line from red node to blue node.
            elif nodes[e['source']]['color']  == 'red' and nodes[e['target']]['color'] == 'blue' \
                or nodes[e['source']]['color']  == 'blue' and nodes[e['target']]['color'] == 'red':
                line_color = 'deepSkyBlue'
            # line from yellow node to blue node.
            elif nodes[e['source']]['color']  == 'yellow' and nodes[e['target']]['color'] == 'blue' \
                or nodes[e['source']]['color']  == 'blue' and nodes[e['target']]['color'] == 'yellow':
                line_color = 'yellow'
            else:
                line_color = 'white'


            direct_edges.append({'source' :  node_index[nodes[e['source']]['name']], 'target' :  node_index[nodes[e['target']]['name']], 'color': line_color})

    return direct_nodes, direct_edges

    
#sp_path, allpath, pathcost = centroid_shotest_path(['allergy', 'asthma'], ['itch','headache','fever'], 'dengue_fever')
#all_path_graph(allpath, pathcost, 'dengue_fever')
#lenght, path = nx.single_source_dijkstra(G, 'dengue_fever', weight='cost', cutoff=30)
#print(len(lenght))