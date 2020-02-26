import backend as backend
from flask import Flask, render_template, url_for, request, jsonify

app = Flask(__name__)

# main nodes and edges
node = []
edge = []
n_disease = dict()
symptoms = []
centroid = None

# nodes and edges correspond to slider cost
nodes_radius = []
edges_radius = []
center_node = None

# symptoms graph
symp_nodes = []
symp_edges = []
symptoms_graph= None

@app.route('/', methods=['GET','POST'])
def index():
    global node
    global edge
    global n_disease
    global symptoms
    global centroid
    global nodes_radius
    global edges_radius
    global center_node
    global symptoms_graph
    symptoms_graph= False
    if request.method == 'POST':
        input_keyword = None
        if request.get_json():
            data = request.get_json()
            input_keyword = data['symptoms']
           
        else:
            input_keyword = request.form['symptoms'].split()
            
        symptoms = backend.check_keyword_exist(input_keyword)
       
        disease, centroid, path, sum_path = backend.disease_hop_activate(symptoms)
        n_disease = dict()
        for k in list(disease.keys())[:10]:
            n_disease[k] = [disease[k], sum_path[k]]
    
        centroid = list(n_disease)[0]
        print("Calculate centroid success!")
        sp_path, allpath, pathcost = backend.centroid_shotest_path(n_disease, symptoms, centroid)
        node, edge = backend.create_graph_sp(n_disease, sp_path, centroid, pathcost)
        nodes_radius = node
        edges_radius = edge
        center_node = centroid
        print("Create graph success!")
        return render_template('index.html', symptoms = symptoms, diseases = n_disease, node = node, edge=edge)
    else:
        return render_template('index.html')

# send disease pdf
@app.route('/send_document', methods=['GET','POST'])
def send_document():
    over_node = request.form['over_node']
    document = backend.document_content(over_node)
    
    return jsonify({'read':document})

# disease graph with symptoms node
@app.route('/node_symptoms', methods=['GET','POST'])
def node_symptoms():
    global nodes_radius
    global edges_radius
    global center_node
    global symp_nodes
    global symp_edges
    global symptoms_graph
    get_node = request.form['node']
    graph_node, graph_edge =  backend.node_symptoms_graph(get_node)
    nodes_radius = graph_node
    edges_radius = graph_edge
    center_node = get_node

    #symptoms graph dataset
    symp_nodes = graph_node
    symp_edges = graph_edge
    symptoms_graph = True

    return jsonify({'nodes':graph_node, 'edges':graph_edge})

# send first centroid graph --> click on centroid btn
@app.route('/centroid_graph', methods=['GET','POST'])
def centroid_graph():
    global nodes_radius
    global edges_radius
    global center_node
    global symptoms_graph
    symptoms_graph= False
    nodes_radius = node
    edges_radius = edge
    center_node = centroid
    
    return jsonify({'nodes':node, 'edges':edge})

# re-calculate centroid when recieve addition symptom.
@app.route('/re_centroid', methods=['GET','POST'])
def re_centroid():
    global node
    global edge
    global n_disease
    global symptoms
    global centroid
    global nodes_radius
    global edges_radius
    global center_node
    global symptoms_graph
    symptoms_graph= False

    data = request.get_json()
    input_keyword = data['symptoms']
    symptoms = backend.check_keyword_exist(input_keyword)
    disease, centroid, path, sum_path = backend.disease_hop_activate(symptoms)
    n_disease = dict()
    for k in list(disease.keys())[:10]:
        n_disease[k] = [disease[k], sum_path[k]]

    centroid = list(n_disease)[0]
    print("Calculate centroid success!")
    sp_path, allpath, pathcost = backend.centroid_shotest_path(n_disease, symptoms, centroid)
    node, edge = backend.create_graph_sp(n_disease, sp_path, centroid)
    print("Create graph success!")
    nodes_radius = node
    edges_radius = edge
    center_node = centroid
    return jsonify({'node':node, 'edge':edge, 'diseases':n_disease})

# adjust slider to display nodes within distance.
@app.route('/nodes_radius', methods=['GET','POST'])
def nodes_radius():
    global nodes_radius
    global edges_radius
    slider_cost = int(request.form['cost'])
    expression = request.form['expression'] # plus or minus
    
    # adjust nodes of main graph
    if not symptoms_graph:
        if expression == 'plus':
            nodes_radius, edges_radius = backend.nodes_in_distance(center_node, node, nodes_radius, edges_radius, slider_cost)
            return jsonify({'nodes':nodes_radius, 'edges':edges_radius})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius = backend.nodes_out_distance(center_node, node, nodes_radius, edges_radius, slider_cost)
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius})

    # adjust nodes of symptoms graph // after move some node to center instead centroid
    else:
        if expression == 'plus':
            nodes_radius, edges_radius = backend.symptoms_in_distance(center_node, symp_nodes, nodes_radius, edges_radius, slider_cost)
            return jsonify({'nodes':nodes_radius, 'edges':edges_radius})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius = backend.symptoms_out_distance(center_node, symp_nodes, nodes_radius, edges_radius, slider_cost)
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius})
    
# display direct connected nodes in graph
@app.route('/direct_connected_nodes', methods=['GET','POST'])
def direct_connected_nodes():
    global nodes_radius
    global edges_radius
    global symptoms_graph
    symptoms_graph= False
    selectednode = request.form['selectednode']
    nodes_radius, edges_radius = backend.get_direct_connected_nodes(selectednode, nodes_radius, edges_radius)
    
    return jsonify({'nodes':nodes_radius, 'edges':edges_radius})

if __name__ == "__main__":
    app.run(debug=True)
    