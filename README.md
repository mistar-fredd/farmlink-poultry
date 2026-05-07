# FARMLINK POULTRY

**AI-Enhanced Flock Management and Bird Identification System**

FARMLINK POULTRY is a web-based MVP for managing poultry flocks, tracking individual birds by Leg Band Number, recording health data, and using a simple AI/ML model to predict bird health status.

---

## Features

- **Bird Identification** — Register and track individual birds using a unique Leg Band Number. Track breed, age, assigned flock, and status (alive, dead, sold).
- **Flock Management** — Group birds into flocks/batches. Track total populations with automatic count updates based on bird status.
- **Health Tracking** — Record health observations, diseases, and treatments per bird.
- **AI Health Prediction** — A trained Random Forest classifier predicts whether a bird is **"Healthy"** or **"At Risk"** based on age, previous health issues, and flock mortality rate.
- **Dashboard** — View summary statistics and flock overviews at a glance.

---

## Technology Stack

| Layer        | Technology                              |
| ------------ | --------------------------------------- |
| Backend      | Python, Flask                           |
| Database     | MySQL (via XAMPP)                       |
| Frontend     | HTML, CSS, Bootstrap 5 (CDN)           |
| ML           | scikit-learn, pandas, NumPy             |
| Environment  | Visual Studio Code, Localhost           |

---

## Project Structure

```
farmlink-poultry/
├── app.py                  # Flask application (backend)
├── schema.sql              # MySQL database schema
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── model/
│   ├── __init__.py
│   ├── ml_model.py         # ML training script
│   ├── bird_health_model.pkl   # Trained model (generated)
│   └── feature_columns.pkl     # Feature column names (generated)
├── templates/
│   ├── base.html           # Master layout with navbar
│   ├── index.html          # Dashboard
│   ├── add_flock.html      # Create new flock form
│   ├── add_bird.html       # Register new bird form
│   ├── bird_profile.html   # Bird details + health history + AI prediction
│   ├── bird_list.html      # List of all birds
│   └── add_health_record.html  # Add health record form
└── static/
    └── css/
        └── style.css       # Custom styles
```

---

## Deployment Instructions

Follow these steps to get FARMLINK POULTRY running on your local machine.

### Prerequisites

- **XAMPP** installed ([Download XAMPP](https://www.apachefriends.org/))
- **Python 3.9+** installed ([Download Python](https://www.python.org/downloads/))
- **Visual Studio Code** installed ([Download VS Code](https://code.visualstudio.com/))

### Step 1: Start MySQL via XAMPP

1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **Apache**.
3. Click **Start** next to **MySQL**.
4. Verify both services show a green "Running" status.

### Step 2: Import the Database Schema

1. Open your web browser and go to **http://localhost/phpmyadmin**.
2. Click the **Import** tab at the top.
3. Click **Choose File** and select the `schema.sql` file from this project.
4. Click **Go** at the bottom to execute the script.
5. You should see `farmlink_db` appear in the left sidebar with three tables: `flocks`, `birds`, and `health_records`.

### Step 3: Open the Project in VS Code

1. Open **Visual Studio Code**.
2. Go to **File → Open Folder** and select the `farmlink-poultry` folder.
3. Open a **Terminal** in VS Code (**Terminal → New Terminal** or press `` Ctrl+` ``).

### Step 4: Set Up Python Virtual Environment

Run these commands in the VS Code terminal:

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Train the ML Model

Run the ML training script once to generate the model file:

```bash
python model/ml_model.py
```

You should see output showing the training progress and a classification report. The trained model will be saved to `model/bird_health_model.pkl`.

### Step 6: Run the Application

```bash
python app.py
```

The Flask development server will start. Open your browser and navigate to:

**http://localhost:5000**

### Step 7: Using the System

1. **Create a Flock** — Click "New Flock" in the navbar and fill in the batch details.
2. **Register Birds** — Click "Register Bird" and assign each bird a unique Leg Band Number.
3. **View Bird Profile** — Click on any bird to see its details and health history.
4. **Add Health Records** — From a bird's profile, click "Add Health Record" to log diseases and treatments.
5. **AI Health Prediction** — From a bird's profile, click the "Run AI Health Prediction" button. The system will analyze the bird's data and predict if it is "Healthy" or "At Risk."

---

## Database Configuration

By default, the app connects to MySQL with:

| Setting  | Value         |
| -------- | ------------- |
| Host     | `localhost`   |
| User     | `root`        |
| Password | *(empty)*     |
| Database | `farmlink_db` |

If your XAMPP MySQL has a different password, update the `DB_CONFIG` dictionary in `app.py`.

---

## License

This project is for educational purposes.
