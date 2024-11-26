from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS for handling cross-origin requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Function to calculate distance between two points
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Load and preprocess the dataset
def preprocess_data():
    # Replace this with the path to your actual CSV file
    data = pd.read_csv('BTP.csv')

    data_cleaned = data[['STORAGE_UNIT_NAME', 'X', 'Y']]
    data_cleaned['X'] = pd.to_numeric(data_cleaned['X'], errors='coerce')
    data_cleaned['Y'] = pd.to_numeric(data_cleaned['Y'], errors='coerce')
    data_cleaned['Capacity'] = np.random.randint(500, 5000, size=len(data_cleaned))  # Simulated capacity
    data_cleaned.dropna(subset=['X', 'Y'], inplace=True)

    np.random.seed(42)
    data_cleaned['Permeability'] = np.random.uniform(0.01, 500, size=len(data_cleaned))
    data_cleaned['Porosity'] = np.random.uniform(0.01, 0.3, size=len(data_cleaned))
    data_cleaned['Temperature'] = np.random.uniform(50, 200, size=len(data_cleaned))
    data_cleaned['Seal_Integrity'] = np.random.uniform(0, 1, size=len(data_cleaned))
    data_cleaned['Depth'] = np.random.uniform(800, 3500, size=len(data_cleaned))

    # Normalize features
    features_to_normalize = ['Permeability', 'Porosity', 'Temperature', 'Seal_Integrity', 'Depth']
    for feature in features_to_normalize:
        data_cleaned[f'{feature}_Norm'] = (data_cleaned[feature] - data_cleaned[feature].min()) / (
            data_cleaned[feature].max() - data_cleaned[feature].min()
        )

    return data_cleaned

# API route for making predictions
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the incoming data from the frontend
        data = request.get_json()

        factory_x = float(data['factory_x'])
        factory_y = float(data['factory_y'])
        required_capacity = float(data['required_capacity'])

        # Preprocess the data
        data_cleaned = preprocess_data()

        # Calculate distance from the factory
        data_cleaned['Distance'] = data_cleaned.apply(
            lambda row: calculate_distance(factory_x, factory_y, row['X'], row['Y']), axis=1
        )
        data_cleaned['Distance_Norm'] = (data_cleaned['Distance'] - data_cleaned['Distance'].min()) / (
            data_cleaned['Distance'].max() - data_cleaned['Distance'].min()
        )

        # Filter sites by capacity
        filtered_data = data_cleaned[data_cleaned['Capacity'] >= required_capacity]

        if not filtered_data.empty:
            # Apply clustering for site grouping
            clustering_features = ['Permeability_Norm', 'Porosity_Norm', 'Temperature_Norm', 'Seal_Integrity_Norm', 'Depth_Norm', 'Distance_Norm']
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(filtered_data[clustering_features])

            kmeans = KMeans(n_clusters=3, random_state=42)
            filtered_data['Cluster'] = kmeans.fit_predict(X_scaled)

            # Evaluate clusters
            cluster_means = filtered_data.groupby('Cluster')[clustering_features].mean()
            cluster_means['Cluster_Score'] = (
                0.4 * cluster_means['Permeability_Norm'] +
                0.3 * cluster_means['Porosity_Norm'] +
                0.2 * cluster_means['Seal_Integrity_Norm'] -
                0.1 * cluster_means['Distance_Norm']
            )

            # Assign cluster scores to sites
            filtered_data['Cluster_Score'] = filtered_data['Cluster'].map(cluster_means['Cluster_Score'])

            # Rank sites by cluster score
            filtered_data.sort_values(by='Cluster_Score', ascending=False, inplace=True)

            # Select the top 5 sites
            top_5_sites = filtered_data.head(5)

            # Respond with the top 5 sites
            response = top_5_sites[['STORAGE_UNIT_NAME', 'Cluster_Score', 'Distance', 'Capacity']].to_dict(orient='records')
            return jsonify({'sites': response})

        else:
            return jsonify({'error': 'No sites meet the required capacity.'})

    except Exception as e:
        return jsonify({'error': str(e)})

# Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

