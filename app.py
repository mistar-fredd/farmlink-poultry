"""
FARMLINK POULTRY - Flask Application
AI-Enhanced Flock Management and Bird Identification System
"""

import os
from datetime import date, datetime

import joblib
import numpy as np
from flask import Flask, flash, redirect, render_template, request, url_for
import mysql.connector
from mysql.connector import Error

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "farmlink-poultry-secret-key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "farmlink_db",
}

# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------


def get_db():
    """Return a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None


# ---------------------------------------------------------------------------
# ML Model Helper
# ---------------------------------------------------------------------------

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")


def load_model():
    """Load the trained ML model and feature columns from disk."""
    model_path = os.path.join(MODEL_DIR, "bird_health_model.pkl")
    columns_path = os.path.join(MODEL_DIR, "feature_columns.pkl")
    if not os.path.exists(model_path):
        return None, None
    model = joblib.load(model_path)
    feature_columns = joblib.load(columns_path)
    return model, feature_columns


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Dashboard showing summary statistics."""
    conn = get_db()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template("index.html", flocks=[], total_birds=0, active_birds=0)

    cursor = conn.cursor(dictionary=True)

    # Total flocks
    cursor.execute("SELECT COUNT(*) AS count FROM flocks")
    total_flocks = cursor.fetchone()["count"]

    # Total birds and active birds
    cursor.execute("SELECT COUNT(*) AS count FROM birds")
    total_birds = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM birds WHERE status = 'alive'")
    active_birds = cursor.fetchone()["count"]

    # Recent flocks with live bird counts
    cursor.execute(
        """
        SELECT f.id, f.batch_name, f.start_date, f.total_initial_birds,
               COUNT(CASE WHEN b.status = 'alive' THEN 1 END) AS alive_count,
               COUNT(b.leg_band_number) AS registered_count
        FROM flocks f
        LEFT JOIN birds b ON f.id = b.flock_id
        GROUP BY f.id
        ORDER BY f.start_date DESC
        """
    )
    flocks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        flocks=flocks,
        total_flocks=total_flocks,
        total_birds=total_birds,
        active_birds=active_birds,
    )


# ---- Flock Routes --------------------------------------------------------


@app.route("/add_flock", methods=["GET", "POST"])
def add_flock():
    """Add a new flock/batch."""
    if request.method == "POST":
        batch_name = request.form.get("batch_name", "").strip()
        start_date = request.form.get("start_date", "")
        total_initial_birds = request.form.get("total_initial_birds", 0, type=int)

        if not batch_name or not start_date:
            flash("Batch name and start date are required.", "warning")
            return redirect(url_for("add_flock"))

        conn = get_db()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("add_flock"))

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO flocks (batch_name, start_date, total_initial_birds) "
            "VALUES (%s, %s, %s)",
            (batch_name, start_date, total_initial_birds),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Flock '{batch_name}' created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_flock.html")


# ---- Bird Routes ---------------------------------------------------------


@app.route("/add_bird", methods=["GET", "POST"])
def add_bird():
    """Register a new bird."""
    conn = get_db()
    flocks = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, batch_name FROM flocks ORDER BY batch_name")
        flocks = cursor.fetchall()
        cursor.close()

    if request.method == "POST":
        leg_band_number = request.form.get("leg_band_number", "").strip()
        flock_id = request.form.get("flock_id", 0, type=int)
        breed = request.form.get("breed", "").strip()
        category = request.form.get("category", "Layer").strip()
        hatch_date = request.form.get("hatch_date", "")

        if not leg_band_number or not flock_id or not breed or not hatch_date:
            flash("All fields are required.", "warning")
            if conn:
                conn.close()
            return render_template("add_bird.html", flocks=flocks)

        if conn is None:
            flash("Database connection failed.", "danger")
            return render_template("add_bird.html", flocks=flocks)

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO birds (leg_band_number, flock_id, breed, category, hatch_date, status) "
                "VALUES (%s, %s, %s, %s, %s, 'alive')",
                (leg_band_number, flock_id, breed, category, hatch_date),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash(
                f"Bird '{leg_band_number}' registered successfully!", "success"
            )
            return redirect(url_for("bird_profile", leg_band_number=leg_band_number))
        except Error as e:
            if conn:
                conn.close()
            flash(f"Error: {e}", "danger")
            return render_template("add_bird.html", flocks=flocks)

    if conn:
        conn.close()
    return render_template("add_bird.html", flocks=flocks)


@app.route("/bird/<leg_band_number>")
def bird_profile(leg_band_number):
    """View a bird's profile with health history."""
    conn = get_db()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("index"))

    cursor = conn.cursor(dictionary=True)

    # Get bird details
    cursor.execute(
        """
        SELECT b.*, f.batch_name
        FROM birds b
        JOIN flocks f ON b.flock_id = f.id
        WHERE b.leg_band_number = %s
        """,
        (leg_band_number,),
    )
    bird = cursor.fetchone()

    if not bird:
        cursor.close()
        conn.close()
        flash("Bird not found.", "warning")
        return redirect(url_for("index"))

    # Get health records
    cursor.execute(
        "SELECT * FROM health_records WHERE leg_band_number = %s ORDER BY record_date DESC",
        (leg_band_number,),
    )
    health_records = cursor.fetchall()

    # Count health issues for this bird
    cursor.execute(
        "SELECT COUNT(*) AS count FROM health_records WHERE leg_band_number = %s AND disease IS NOT NULL AND disease != ''",
        (leg_band_number,),
    )
    health_issue_count = cursor.fetchone()["count"]

    cursor.close()
    conn.close()

    return render_template(
        "bird_profile.html",
        bird=bird,
        health_records=health_records,
        health_issue_count=health_issue_count,
    )


@app.route("/update_bird_status/<leg_band_number>", methods=["POST"])
def update_bird_status(leg_band_number):
    """Update a bird's status (alive, dead, sold)."""
    new_status = request.form.get("status", "alive")

    conn = get_db()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("bird_profile", leg_band_number=leg_band_number))

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE birds SET status = %s WHERE leg_band_number = %s",
        (new_status, leg_band_number),
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Bird status updated to '{new_status}'.", "success")
    return redirect(url_for("bird_profile", leg_band_number=leg_band_number))


# ---- Health Record Routes ------------------------------------------------


@app.route("/add_health_record/<leg_band_number>", methods=["GET", "POST"])
def add_health_record(leg_band_number):
    """Add a health record for a bird."""
    if request.method == "POST":
        record_date = request.form.get("record_date", str(date.today()))
        disease = request.form.get("disease", "").strip()
        treatment = request.form.get("treatment", "").strip()
        notes = request.form.get("notes", "").strip()

        conn = get_db()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(
                url_for("add_health_record", leg_band_number=leg_band_number)
            )

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO health_records (leg_band_number, record_date, disease, treatment, notes) "
            "VALUES (%s, %s, %s, %s, %s)",
            (leg_band_number, record_date, disease or None, treatment or None, notes or None),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Health record added successfully!", "success")
        return redirect(url_for("bird_profile", leg_band_number=leg_band_number))

    return render_template("add_health_record.html", leg_band_number=leg_band_number)


# ---- AI / ML Prediction Route -------------------------------------------


@app.route("/predict_health/<leg_band_number>")
def predict_health(leg_band_number):
    """Run the AI health prediction for a specific bird."""
    conn = get_db()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("bird_profile", leg_band_number=leg_band_number))

    cursor = conn.cursor(dictionary=True)

    # Get bird data
    cursor.execute(
        "SELECT * FROM birds WHERE leg_band_number = %s", (leg_band_number,)
    )
    bird = cursor.fetchone()

    if not bird:
        cursor.close()
        conn.close()
        flash("Bird not found.", "warning")
        return redirect(url_for("index"))

    # Calculate age in weeks
    hatch_date = bird["hatch_date"]
    if isinstance(hatch_date, str):
        hatch_date = datetime.strptime(hatch_date, "%Y-%m-%d").date()
    age_weeks = max(1, (date.today() - hatch_date).days // 7)

    # Count previous health issues
    cursor.execute(
        "SELECT COUNT(*) AS count FROM health_records "
        "WHERE leg_band_number = %s AND disease IS NOT NULL AND disease != ''",
        (leg_band_number,),
    )
    previous_health_issues = cursor.fetchone()["count"]

    # Calculate flock mortality rate
    cursor.execute(
        "SELECT COUNT(*) AS total, "
        "COUNT(CASE WHEN status = 'dead' THEN 1 END) AS dead "
        "FROM birds WHERE flock_id = %s",
        (bird["flock_id"],),
    )
    flock_stats = cursor.fetchone()
    total_in_flock = flock_stats["total"] if flock_stats["total"] > 0 else 1
    flock_mortality_rate = round(flock_stats["dead"] / total_in_flock, 3)

    cursor.close()
    conn.close()

    # Load model and predict
    model, feature_columns = load_model()
    if model is None:
        flash(
            "ML model not found. Please run model/ml_model.py first to train the model.",
            "danger",
        )
        return redirect(url_for("bird_profile", leg_band_number=leg_band_number))

    # Prepare feature vector (match training feature order)
    weight_kg = round(np.random.uniform(1.0, 4.5), 2)  # Simulated weight
    vaccination_status = 1  # Default vaccinated

    features = np.array(
        [[age_weeks, weight_kg, previous_health_issues, flock_mortality_rate, vaccination_status]]
    )
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    # Determine confidence
    confidence = round(max(probability) * 100, 1)

    flash(
        f"AI Prediction for {leg_band_number}: {prediction} "
        f"(Confidence: {confidence}%)",
        "info",
    )

    return redirect(url_for("bird_profile", leg_band_number=leg_band_number))


# ---- Bird List Route -----------------------------------------------------


@app.route("/birds")
def bird_list():
    """List all registered birds."""
    conn = get_db()
    if conn is None:
        flash("Database connection failed.", "danger")
        return render_template("bird_list.html", birds=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT b.*, f.batch_name
        FROM birds b
        JOIN flocks f ON b.flock_id = f.id
        ORDER BY b.leg_band_number
        """
    )
    birds = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("bird_list.html", birds=birds)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
