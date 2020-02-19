import backend as backend
from flask import Flask, render_template, url_for, request, jsonify

app = Flask(__name__)

node = []
edge = []
n_disease = dict()
symptoms = []
@app.route('/', methods=['GET','POST'])
def index():
    global node
    global edge
    global n_disease
    global symptoms

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
        sp_path = backend.centroid_shotest_path(n_disease, symptoms, centroid)
        node, edge = backend.create_graph_sp(n_disease, sp_path, centroid)
        print("Create graph success!")
        return render_template('index.html', symptoms = symptoms, diseases = n_disease, node = node, edge=edge)
    else:
        return render_template('index.html')
"""
@app.route('/re_centroid', methods=['GET','POST'])
def re_centroid():
    global node
    centroid = request.form['centroid']
    node = backend.node_position(node, centroid)
   
    return jsonify({'node':node})
"""
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
    return jsonify({'nodes':graph_node, 'edges':graph_edge})

# send first centroid graph --> click on centroid btn
@app.route('/centroid_graph', methods=['GET','POST'])
def centroid_graph():

    return jsonify({'nodes':node, 'edges':edge})

# re-calculate centroid when recieve addition symptom.
@app.route('/re_centroid', methods=['GET','POST'])
def re_centroid():
    global node
    global edge
    global n_disease
    global symptoms

    data = request.get_json()
    input_keyword = data['symptoms']
    symptoms = backend.check_keyword_exist(input_keyword)
    disease, centroid, path, sum_path = backend.disease_hop_activate(symptoms)
    n_disease = dict()
    for k in list(disease.keys())[:10]:
        n_disease[k] = [disease[k], sum_path[k]]

    centroid = list(n_disease)[0]
    print("Calculate centroid success!")
    sp_path = backend.centroid_shotest_path(n_disease, symptoms, centroid)
    node, edge = backend.create_graph_sp(n_disease, sp_path, centroid)
    print("Create graph success!")
    return jsonify({'node':node, 'edge':edge, 'diseases':n_disease})



if __name__ == "__main__":
    app.run(debug=True)
    