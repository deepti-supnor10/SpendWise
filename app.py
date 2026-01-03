from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load the trained model
try:
    model = pickle.load(open('spend_model.pkl', 'rb'))
except FileNotFoundError:
    print("Error: spend_model.pkl not found. Run model_trainer.py first.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            month = int(request.form['month'])
            prev_spend = float(request.form['prev_spend'])
            
            # Predict using pipeline
            features = np.array([[month, prev_spend]])
            prediction = model.predict(features)[0]
            
            return render_template('index.html', 
                                   prediction_text=f'Predicted Expense: ${prediction:.2f}',
                                   scroll='result-section')
        except Exception as e:
            return render_template('index.html', prediction_text=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
