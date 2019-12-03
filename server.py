import backend as backend
from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        input_keyword = request.form['symptoms'].split()
        symptoms = backend.check_keyword_exist(input_keyword)
        disease, centroid = backend.disease_hop_activate(symptoms)
        n_disease = {k: disease[k] for k in list(disease.keys())[:10]}
      
        return render_template('index.html', symptoms = symptoms, diseases = n_disease)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
    