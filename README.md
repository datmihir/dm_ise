# 📊 Data Mining Tool (PE-IV 6CS412)

Built with **Angular (Frontend), Django (Backend), and MySQL (Database)**.
This project was developed as part of the coursework for **PE-IV 6CS412: Data Mining**.

---

## 🚀 Tech Stack

* **Frontend:** Angular + Angular Material
* **Backend:** Django (Python) + Django 
* **Database:** MySQL
* **Version Control:** Git

---

## ✨ Features

### 📂 Dataset Management

* Upload CSV datasets
* Preview first 10 rows instantly
* Dataset Library to manage all uploaded files
* Save complete **analysis history** for reproducibility

### ⚙️ Data Preprocessing

* **Statistical Description**

  * Mean, Median, Mode
* **Dispersion Measures**

  * Variance, Standard Deviation
* **Data Cleaning**

  * Handle missing values (row removal / mean imputation)
* **Statistical Tests**

  * Chi-Square Test (categorical data)
* **Correlation & Covariance**

  * Pearson Correlation Coefficient
  * Covariance
* **Normalization**

  * Min-Max
  * Z-Score
  * Decimal Scaling
* **Discretization**

  * Equal-Width Binning
* **Visualization Data Generation**

  * Histograms
  * Scatter Plots

### 🤖 Classification & Regression

* **Decision Tree**

  * Entropy (Information Gain)
  * Gain Ratio
  * Gini Index
* **k-Nearest Neighbors (k-NN)**
* **Rule-Based Classifier (1R)**
* **Naïve Bayesian Classifier**
* **Simple Linear Regression**
* **Artificial Neural Network (Perceptron for binary classification)**

---

## 🛠️ Prerequisites

Make sure you have the following installed:

* [Python 3.8+](https://www.python.org/downloads/)
* [Node.js (LTS) + npm](https://nodejs.org/)
* [MySQL Server](https://dev.mysql.com/downloads/)
* [Git](https://git-scm.com/)

---

## ⚡ Installation & Setup

### 🔹 1. Clone Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

### 🔹 2. Backend Setup (Django)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install Django django-cors-headers mysqlclient
```

#### Configure Database

Login to MySQL and create a database:

```sql
CREATE DATABASE dm_tool_db;
```

Update `backend/dm_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dm_tool_db',
        'USER': 'root',
        'PASSWORD': 'YOUR_MYSQL_PASSWORD',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Run migrations:

```bash
python manage.py makemigrations api
python manage.py migrate
```

Start backend server:

```bash
python manage.py runserver
```

Runs on: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### 🔹 3. Frontend Setup (Angular)

```bash
cd frontend

# Install dependencies
npm install

# Add Angular Material
ng add @angular/material
```

Start frontend server:

```bash
ng serve
```

Runs on: **[http://localhost:4200](http://localhost:4200)**

---

## 📖 Usage Guide

1. **Upload Dataset** → via "Upload New Dataset" button.
2. **Select Dataset** → appears in Dataset Library.
3. **Perform Actions**

   * Preprocess data
   * Classify data
   * View history


