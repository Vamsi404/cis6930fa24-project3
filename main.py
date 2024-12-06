import requests
from flask import Flask, render_template, request, redirect, jsonify
from utils.pdf_handler import extract_incidents
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import seaborn as sns
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="PyPDF2")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="jupyter_client.connect")


app = Flask(__name__)
UPLOAD_FOLDER = './utils'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to hold the DataFramene 
incidents_df = pd.DataFrame()

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global incidents_df  # Use global variable to store DataFrame
    
    # Check if the URL is provided
    url = request.form.get('url')
    
    # Handle file upload
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        
        if not file.filename.lower().endswith('.pdf'):
            return "Invalid file type. Please upload a PDF file.", 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            incidents_df = extract_incidents(file_path)
        except Exception as e:
            return f"Error processing the PDF: {str(e)}", 500

    # Handle URL input
    elif url:
        try:
            # Download the PDF from the URL
            response = requests.get(url)
            if response.status_code != 200:
                return f"Failed to download PDF from the URL. Status code: {response.status_code}", 400
            
            # Save the file locally
            pdf_filename = url.split("/")[-1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Process the downloaded PDF
            incidents_df = extract_incidents(file_path)
        
        except Exception as e:
            return f"Error downloading or processing the PDF: {str(e)}", 500
    else:
        return "No file or URL provided", 400
    
    # After processing the PDF, redirect to the dashboard
    return redirect('/dashboard')



from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import io
import base64

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

def perform_clustering(incidents_df):
    # Ensure 'Date / Time' is in datetime format
    incidents_df['Date / Time'] = pd.to_datetime(incidents_df['Date / Time'], errors='coerce')
    
    # Extract hour from 'Date / Time'
    incidents_df['hour'] = incidents_df['Date / Time'].dt.hour

    # Encode 'incident_location' and 'incident_nature' using LabelEncoder
    label_encoder_location = LabelEncoder()
    label_encoder_nature = LabelEncoder()
    incidents_df['location_encoded'] = label_encoder_location.fit_transform(incidents_df['incident_location'])
    incidents_df['nature_encoded'] = label_encoder_nature.fit_transform(incidents_df['incident_nature'])

    # Prepare features for clustering
    clustering_features = incidents_df[['hour', 'location_encoded', 'nature_encoded']].dropna()

    # Standardize features for clustering
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(clustering_features)

    # Apply K-Means clustering with a fixed number of clusters
    kmeans = KMeans(n_clusters=5, random_state=42)  # Adjust n_clusters as needed
    cluster_labels = kmeans.fit_predict(scaled_features)

    # Apply PCA for dimensionality reduction
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(scaled_features)

    # Add cluster labels to the reduced features for visualization
    clustering_features['PCA1'] = reduced_features[:, 0]
    clustering_features['PCA2'] = reduced_features[:, 1]
    clustering_features['cluster'] = cluster_labels

    # Visualization with PCA components
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        clustering_features['PCA1'],  # PCA Component 1
        clustering_features['PCA2'],  # PCA Component 2
        c=cluster_labels, cmap='viridis', alpha=0.8
    )
    ax.set_title("K-Means Clustering of Incidents (PCA Reduced)")
    ax.set_xlabel("PCA Component 1")
    ax.set_ylabel("PCA Component 2")
    legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
    ax.add_artist(legend1)

    # Save plot as base64 string for rendering in HTML
    clustering_img = io.BytesIO()
    fig.tight_layout()
    fig.savefig(clustering_img, format='png')
    clustering_img.seek(0)
    clustering_url = base64.b64encode(clustering_img.getvalue()).decode('utf8')

    return clustering_url

@app.route('/dashboard')
def dashboard():
    global incidents_df  # Access the global DataFrame

    try:
        if incidents_df.empty:  # Check if the DataFrame is empty
            return "No data available for dashboard", 400
        # Summarize incident data and sort by count, then take the top 10
        summary = incidents_df.groupby('incident_nature').size().reset_index(name='count')
        top_summary = summary.nlargest(10, 'count')

        # Adjust figure size based on the number of labels
        fig_height = max(6, len(top_summary) * 0.8)  # Dynamically adjust height for spacing
        fig1, ax1 = plt.subplots(figsize=(10, fig_height))  # Horizontal chart needs more height

        # Create a horizontal bar chart
        ax1.barh(top_summary['incident_nature'], top_summary['count'], color='skyblue')
        ax1.set_title('Top 10 Incident Types')
        ax1.set_xlabel('Count')
        ax1.set_ylabel('Type')

        # Invert the y-axis to display the highest count on top
        ax1.invert_yaxis()

        # Convert the bar chart to base64 string
        img1 = io.BytesIO()
        fig1.tight_layout()  # Prevent label clipping
        fig1.savefig(img1, format='png')
        img1.seek(0)
        bar_chart_url = base64.b64encode(img1.getvalue()).decode('utf8')

        # Generate a pie chart for the top 10 fields
        fig2, ax2 = plt.subplots()
        ax2.pie(top_summary['count'], labels=top_summary['incident_nature'], autopct='%1.1f%%', startangle=90)
        ax2.set_title('Top 10 Incident Distribution')

        # Convert the pie chart to base64 string
        img2 = io.BytesIO()
        fig2.tight_layout()  # Prevent label clipping
        fig2.savefig(img2, format='png')
        img2.seek(0)
        pie_chart_url = base64.b64encode(img2.getvalue()).decode('utf8')

        # Generate a heatmap grouped by location
        location_counts = incidents_df.groupby('incident_location').size().reset_index(name='incident_count')

        # Sort by incident count and get the top 5 locations
        top_locations = location_counts.nlargest(10, 'incident_count')['incident_location']

        # Filter the original dataframe to include only the top 5 locations
        filtered_df = incidents_df[incidents_df['incident_location'].isin(top_locations)]

        # Group by location and incident nature
        heatmap_data = filtered_df.groupby(['incident_location', 'incident_nature']).size().unstack(fill_value=0)

        # Create heatmap
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        sns.heatmap(heatmap_data, cmap="Blues", linewidths=0.5, annot=False, ax=ax3)
        ax3.set_title("Heatmap of Incidents by Location (Top 10 Locations)")
        ax3.set_xlabel("Incident Nature")
        ax3.set_ylabel("Location")

        # Convert the heatmap to a base64 string
        img3 = io.BytesIO()
        fig3.tight_layout()
        fig3.savefig(img3, format='png')
        img3.seek(0)
        heatmap_url = base64.b64encode(img3.getvalue()).decode('utf8')

        clustering_url = perform_clustering(incidents_df)
        # Pass clustering_url to the template


        return render_template('dashboard.html', 
                            summary=top_summary.to_dict(orient='records'), 
                            bar_chart_url=bar_chart_url, 
                            pie_chart_url=pie_chart_url,
                            heatmap_url=heatmap_url,
                            clustering_url=clustering_url)




    except Exception as e:
        return f"Error generating the dashboard: {str(e)}", 500

@app.route('/data', methods=['GET'])
def get_data():
    global incidents_df  # Access the global DataFrame
    
    try:
        # Return incident summary in JSON format for any API-based consumption
        summary = incidents_df.groupby('incident_nature').size().reset_index(name='count')
        return jsonify(summary.to_dict(orient='records'))
    
    except Exception as e:
        return jsonify({"error": f"Error fetching incident summary: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
