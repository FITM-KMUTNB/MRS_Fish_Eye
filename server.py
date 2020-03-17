import backend as backend
from flask import Flask, render_template, url_for, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'd8ca72807d23a1ee51e2016cbb57f36c7e8e51555a25711a'

# session config
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session()
sess.init_app(app)

# session vairable
"""
*** main graph ***
node : main nodes
edge : main edges
allpath : shortest path list from centroid
pathcost : nodes distance to centroid

"""
@app.route('/', methods=['GET','POST'])
def index():
    
    if request.method == 'POST':

        input_keyword = request.form['symptoms'].split()
            
        symptoms = backend.check_keyword_exist(input_keyword)
       
        disease, centroid, path, sum_path = backend.disease_hop_activate(symptoms)
        print("calculate centroid --> done")
        n_disease = dict()
        for k in list(disease.keys())[:10]:
            n_disease[k] = [disease[k], sum_path[k]]
        centroid = list(n_disease)[0]

        
        sp_path, allpath, pathcost = backend.centroid_shotest_path(n_disease, symptoms, centroid)
        node,  edge= backend.create_graph_sp(n_disease, sp_path, centroid, pathcost)
        print("create graph success --> done")

        # session variable
        session['allpath'] = allpath
        session['pathcost'] = pathcost
        session['node'] = node
        session['edge'] = edge
        session['nodes_radius'] = node
        session['edges_radius'] = edge
        session['centroid'] = centroid
        session['center_node'] = centroid
        session['symptoms_graph'] = False
        return render_template('index.html', symptoms = symptoms, diseases = n_disease, node = session['node'], edge=session['edge'])
    else:
        session.clear()
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
   
    get_node = request.form['node']
    graph_node, graph_edge =  backend.node_symptoms_graph(get_node)

    # session variable
    session['nodes_radius'] = graph_node
    session['edges_radius'] = graph_edge
    session['center_node'] = get_node
        # symptoms graph dataset
    session['symp_nodes'] = graph_node
    session['symp_edges'] = graph_edge
    session['symptoms_graph'] = True

    return jsonify({'nodes':graph_node, 'edges':graph_edge})

# send first centroid graph --> click on centroid btn
@app.route('/centroid_graph', methods=['GET','POST'])
def centroid_graph():
    
    session['symptoms_graph'] = False
    session['nodes_radius'] = session['node']
    session['edges_radius'] = session['edge']
    session['center_node'] = session['centroid']
    
    return jsonify({'nodes':session['node'], 'edges':session['edge']})


# adjust slider to display nodes within distance.
@app.route('/nodes_radius', methods=['GET','POST'])
def nodes_radius():
    slider_cost = int(request.form['cost'])
    expression = request.form['expression'] # plus or minus
    session['node_r'] = 6
    # adjust nodes of main graph
    if not session['symptoms_graph']:
        if expression == 'plus':
            nodes_radius, edges_radius, node_r = backend.nodes_in_distance(session['center_node'], session['node'], session['nodes_radius'], session['edges_radius'], slider_cost)
            session['nodes_radius'] = nodes_radius
            session['edges_radius'] = edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':session['nodes_radius'], 'edges':session['edges_radius'], 'node_r':session['node_r']})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius, node_r = backend.nodes_out_distance(session['center_node'], session['node'], session['nodes_radius'],  session['edges_radius'], slider_cost, session['node_r'])
            session['node_r'] = node_r
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius, 'node_r':session['node_r']})

    # adjust nodes of symptoms graph // after move some node to center instead centroid
    else:
        if expression == 'plus':
            nodes_radius, edges_radius, node_r = backend.symptoms_in_distance(session['center_node'], session['symp_nodes'], session['nodes_radius'], session['edges_radius'], slider_cost)
            session['nodes_radius'] = nodes_radius
            session['edges_radius'] = edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':session['nodes_radius'], 'edges':session['edges_radius'], 'node_r':session['node_r']})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius, node_r = backend.symptoms_out_distance(session['center_node'], session['symp_nodes'], session['nodes_radius'], session['edges_radius'], slider_cost, session['node_r'])
            session['node_r'] = node_r
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius, 'node_r':session['node_r']})
    
# display direct connected nodes in graph
@app.route('/direct_connected_nodes', methods=['GET','POST'])
def direct_connected_nodes():
   
    selectednode = request.form['selectednode']
    nodes_radius, edges_radius = backend.get_direct_connected_nodes(selectednode, session['nodes_radius'], session['edges_radius'])

    # session variable
    session['symptoms_graph'] = False
    session['nodes_radius'] = nodes_radius
    session['edges_radius'] =  edges_radius
    return jsonify({'nodes':nodes_radius, 'edges':edges_radius})

# get closest to select node for find more condition.    
@app.route('/more_relevant', methods=['GET','POST'])
def more_relevant():
    selectednode = request.form['selectednode']
    relevantnodes = backend.get_closest_nodes(selectednode, session['nodes_radius'])

    return jsonify({'relevantnodes':relevantnodes})
if __name__ == "__main__":
    app.run(debug=True)
    