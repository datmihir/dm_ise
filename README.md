Data Mining Tool (PE-IV 6CS412)
Project for PE-IV 6CS412: Data Mining Technology Stack: Angular, Django (Python), MySQL

1. Introduction
This web application is a comprehensive data mining tool developed as part of the coursework for PE-IV 6CS412: Data Mining. It provides a user-friendly interface to upload datasets, perform a wide variety of data pre-processing tasks, and apply several classification algorithms.

A key requirement of this project is that all data pre-processing and classification algorithms are implemented from scratch using pure Python, without relying on external data science libraries like scikit-learn or pandas for the core logic.

The application features a decoupled architecture with an Angular frontend and a Django backend, communicating via a REST API. All uploaded dataset information and analysis results are stored persistently in a MySQL database.

2. Features Implemented
2.1. Dataset Management
Upload & Preview: Users can upload CSV files. The system provides an immediate preview of the first 20 rows.

Dataset Library: All uploaded datasets are saved and listed in a central library.

Analysis History: The application saves every analysis run on a dataset to the database, allowing users to view a complete history of operations.

2.2. Pre-processing Tasks
The following pre-processing tasks can be performed on any selected dataset:

Statistical Description:

Measures of Central Tendency (Mean, Median, Mode)

Dispersion of Data:

Variance and Standard Deviation

Data Cleaning:

Handle Missing Values by removing rows.

Handle Missing Values by filling with the column's mean.

Statistical Tests:

Chi-Square Test for two categorical columns.

Correlation & Covariance:

Pearson Correlation Coefficient and Covariance for two numerical columns.

Normalization:

Min-Max Normalization

Z-Score Normalization

Decimal Scaling Normalization

Discretization:

Discretization by Equal-Width Binning.

Visualization:

Generate data for Histograms.

Generate data for Scatter Plots.

2.3. Classification Algorithms
The following classifiers can be trained and used for prediction:

Decision Tree: With three different split criteria:

Entropy (Information Gain)

Gain Ratio

Gini Index

k-Nearest Neighbors (k-NN): Predicts the class of a new instance based on its neighbors.

Rule-Based Classifier: A simple 1R (One Rule) classifier.

Regression: Simple Linear Regression to find the relationship between two variables.

Naïve Bayesian Classifier: A probabilistic classifier based on Bayes' theorem.

Artificial Neural Network (ANN): A single Perceptron model for binary classification.

3. Prerequisites
Before you begin, ensure you have the following software installed on your system:

Python (version 3.8 or higher)

Node.js and npm (LTS version recommended)

Git version control

MySQL Server

4. Installation and Deployment Steps
4.1. Backend Setup (Django)
Clone the Project:

git clone <your-repository-url>
cd <project-folder>/backend

Create and Activate Virtual Environment:

# Create the environment
python -m venv venv
# Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Install Python Dependencies:

pip install Django django-cors-headers mysqlclient

Configure MySQL Database:

Log in to your MySQL server and create a new database.

CREATE DATABASE dm_tool_db;

Open the backend/dm_project/settings.py file.

Locate the DATABASES section and update it with your MySQL credentials:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dm_tool_db', # The name you chose
        'USER': 'root',
        'PASSWORD': 'YOUR_MYSQL_PASSWORD', # Your MySQL root password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

Run Database Migrations:

python manage.py makemigrations api
python manage.py migrate

4.2. Frontend Setup (Angular)
Navigate to Frontend Directory:
Open a new, separate terminal and navigate to the frontend folder.

cd <project-folder>/frontend

Install Node.js Dependencies:

npm install

Install Angular Material:
This is required for the UI components to work correctly.

ng add @angular/material

Choose a prebuilt theme (e.g., "Indigo/Pink").

Answer "Yes" to setting up global typography styles.

Answer "Yes" to including animations.

4.3. Running the Application
You must have two terminals running simultaneously.

Start the Backend Server:

In your backend terminal (with venv active):

python manage.py runserver

The backend will be running at http://127.0.0.1:8000.

Start the Frontend Server:

In your frontend terminal:

ng serve --open

The application will automatically open in your browser at http://localhost:4200.

5. How to Use the Application
Upload a Dataset: Click the "Upload New Dataset" button to open a dialog and select a CSV file.

Select a Dataset: After uploading, the dataset will appear in the "Dataset Library". Click on it to select it.

Perform Actions: Once a dataset is selected, the "Actions" card will become active.

Click "Pre-process Data" to open a dialog with all pre-processing options.

Click "Classify Data" to open a dialog with all classification algorithms.

Click "View History" to see a record of all analyses previously run on that dataset.
