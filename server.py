import backend as backend
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        input_keyword = request.form['symptoms'].split()
        symptoms = backend.check_keyword_exist(input_keyword)
        disease, centroid, path = backend.disease_hop_activate(symptoms)
        n_disease = {k: disease[k] for k in list(disease.keys())[:10]}
        centroid = list(n_disease)[0]
        node, edge = backend.create_graph(n_disease, path, centroid)
        return render_template('index.html', symptoms = symptoms, diseases = n_disease, node = node, edge=edge)
    else:
        return render_template('index.html')

@app.route('/re_centroid', methods=['GET','POST'])
def re_centroid():
    data = request.form['centroid']
    print(data)
    return "hello"

if __name__ == "__main__":
    app.run(debug=True)
    