
import os
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import subprocess
import mysql.connector

from config import DB_CONFIG


# =========================================================
# Flask Configuration
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is not set")
# =========================================================
# Project Configuration
# =========================================================

RESTIC_REPO = "rclone:gdrive:CloudBackup/restic-repo"

BACKUP_SOURCE = "/home/hano/cloud-backup/client_files"

RESTORE_PATH = "/home/hano/cloud-backup/restore_web"


# =========================================================
# MySQL Connection
# =========================================================

def get_db_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# =========================================================
# Login Protection
# =========================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# =========================================================
# Dashboard HTML - Dark Teal Design
# =========================================================

DASHBOARD_HTML = """
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <meta name="color-scheme" content="dark">

    <title>Cloud Backup Dashboard</title>


    <!-- Icons -->

    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">


    <!-- Chart.js -->

    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>


    <style>

        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --inner: #0f172a;
            --border: #334155;
            --text: #e2e8f0;
            --text-strong: #f1f5f9;
            --muted: #94a3b8;
            --teal: #14b8a6;
            --teal-light: #2dd4bf;
            --teal-dark: #0d9488;
            --teal-bg: #134e4a;
            --green: #4ade80;
            --red: #f87171;
            --violet: #a78bfa;
            --amber: #fbbf24;
        }


        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }


        body {
            font-family:
                -apple-system, BlinkMacSystemFont,
                "Segoe UI", Roboto, Arial, sans-serif;

            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }


        a {
            text-decoration: none;
            color: inherit;
        }


        a:focus-visible {
            outline: 2px solid var(--teal-light);
            outline-offset: 2px;
        }


        /* ---------- Header ---------- */

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 16px 24px;

            border-bottom: 1px solid var(--surface);
        }


        .brand {
            display: flex;
            align-items: center;
            gap: 10px;

            font-size: 18px;
            font-weight: 600;
            color: var(--text-strong);
        }


        .brand i {
            font-size: 26px;
            color: var(--teal-light);
        }


        .user-area {
            display: flex;
            align-items: center;
            gap: 12px;
        }


        .user-email {
            font-size: 14px;
            color: var(--muted);
        }


        .avatar {
            width: 34px;
            height: 34px;

            border-radius: 50%;

            background: var(--teal-bg);
            color: #5eead4;

            display: flex;
            align-items: center;
            justify-content: center;

            font-size: 13px;
            font-weight: 600;
        }


        .logout {
            display: flex;
            align-items: center;
            gap: 6px;

            font-size: 14px;
            color: var(--muted);

            padding: 7px 12px;

            border: 1px solid var(--border);
            border-radius: 8px;
        }


        .logout:hover {
            color: var(--text-strong);
            border-color: var(--muted);
        }


        /* ---------- Layout ---------- */

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 24px 20px 40px;
        }


        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-strong);
            margin-bottom: 14px;
        }


        .block {
            margin-bottom: 24px;
        }


        /* ---------- Messages ---------- */

        .message {
            padding: 14px 16px;
            margin-bottom: 20px;

            background: #052e16;
            color: #86efac;

            border: 1px solid #166534;
            border-radius: 10px;

            font-size: 14px;
        }


        .error {
            padding: 14px 16px;
            margin-bottom: 20px;

            background: #450a0a;
            color: #fca5a5;

            border: 1px solid #991b1b;
            border-radius: 10px;

            font-size: 14px;
        }


        /* ---------- Quick Actions ---------- */

        .actions {
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(150px, 1fr));

            gap: 12px;
        }


        .action {
            display: block;

            padding: 16px;

            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;

            transition: border-color 0.15s;
        }


        .action:hover {
            border-color: var(--muted);
        }


        .action i {
            display: block;
            font-size: 26px;
            margin-bottom: 10px;
        }


        .action span {
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
        }


        .action-primary {
            background: var(--teal);
            border-color: var(--teal);
        }


        .action-primary:hover {
            background: var(--teal-light);
            border-color: var(--teal-light);
        }


        .action-primary i,
        .action-primary span {
            color: #042f2e;
        }


        .ic-violet {
            color: var(--violet);
        }


        .ic-green {
            color: var(--green);
        }


        .ic-amber {
            color: var(--amber);
        }


        /* ---------- Panels ---------- */

        .panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;

            padding: 20px;
        }


        .latest-head {
            display: flex;
            align-items: center;
            gap: 14px;

            margin-bottom: 16px;
        }


        .status-icon {
            width: 44px;
            height: 44px;

            border-radius: 50%;

            display: flex;
            align-items: center;
            justify-content: center;

            font-size: 24px;

            flex-shrink: 0;
        }


        .status-ok {
            background: var(--teal-bg);
            color: var(--teal-light);
        }


        .status-fail {
            background: #450a0a;
            color: var(--red);
        }


        .latest-label {
            font-size: 12px;
            color: var(--muted);
        }


        .latest-title {
            font-size: 17px;
            font-weight: 600;
            color: var(--text-strong);
        }


        .latest-grid {
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(150px, 1fr));

            gap: 12px;
        }


        .latest-item {
            background: var(--inner);

            padding: 12px 14px;

            border-radius: 8px;
        }


        .latest-item small {
            display: block;

            font-size: 12px;
            color: var(--muted);

            margin-bottom: 3px;
        }


        .latest-item div {
            font-size: 15px;
            color: var(--text);

            word-break: break-all;
        }


        .mono {
            font-family:
                ui-monospace, SFMono-Regular,
                Menlo, Consolas, monospace;

            color: #5eead4 !important;
        }


        /* ---------- Stats ---------- */

        .stats {
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(150px, 1fr));

            gap: 12px;
        }


        .stat {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;

            padding: 18px;
        }


        .stat .label {
            font-size: 13px;
            color: var(--muted);
        }


        .stat .number {
            font-size: 30px;
            font-weight: 600;

            margin-top: 4px;

            color: var(--text-strong);
        }


        .stat .number.ok {
            color: var(--green);
        }


        .stat .number.bad {
            color: var(--red);
        }


        .online {
            display: flex;
            align-items: center;
            gap: 9px;

            margin-top: 14px;

            font-size: 18px;
            font-weight: 600;

            color: var(--text-strong);
        }


        .dot {
            width: 10px;
            height: 10px;

            border-radius: 50%;

            background: var(--green);
        }


        /* ---------- Chart ---------- */

        .chart-container {
            position: relative;

            width: 100%;
            height: 320px;
        }


        .empty {
            color: var(--muted);
            font-size: 14px;
        }


        /* ---------- Mobile ---------- */

        @media (max-width: 600px) {

            .header {
                padding: 14px 16px;
            }

            .user-email {
                display: none;
            }

            .container {
                padding: 18px 14px 32px;
            }

        }

    </style>

</head>


<body>


<div class="header">

    <div class="brand">

        <i class="ti ti-shield-check"></i>

        Cloud Backup

    </div>


    <div class="user-area">

        <span class="user-email">{{ email }}</span>

        <div class="avatar">
            {{ (email or "?")[0] | upper }}
        </div>

        <a class="logout"
           href="{{ url_for('logout') }}">

            <i class="ti ti-logout"></i>

            Logout

        </a>

    </div>

</div>



<div class="container">


    {% if message %}

        <div class="message">
            {{ message }}
        </div>

    {% endif %}


    {% if error %}

        <div class="error">
            {{ error }}
        </div>

    {% endif %}



    <!-- Quick Actions -->

    <div class="block">

        <h2 class="section-title">Quick actions</h2>

        <div class="actions">


            <a href="{{ url_for('backup') }}"
               class="action action-primary">

                <i class="ti ti-cloud-upload"></i>

                <span>Backup now</span>

            </a>


            <a href="{{ url_for('history') }}"
               class="action">

                <i class="ti ti-history ic-violet"></i>

                <span>History</span>

            </a>


            <a href="{{ url_for('restore') }}"
               class="action">

                <i class="ti ti-download ic-green"></i>

                <span>Restore latest</span>

            </a>


            <a href="{{ url_for('statistics') }}"
               class="action">

                <i class="ti ti-chart-bar ic-amber"></i>

                <span>Statistics</span>

            </a>


        </div>

    </div>



    <!-- Latest Backup -->

    <div class="block">

        <div class="panel">

            {% if latest %}

                <div class="latest-head">

                    {% if latest.status == "SUCCESS" %}

                        <div class="status-icon status-ok">
                            <i class="ti ti-check"></i>
                        </div>

                        <div>
                            <div class="latest-label">Latest backup</div>
                            <div class="latest-title">Completed successfully</div>
                        </div>

                    {% else %}

                        <div class="status-icon status-fail">
                            <i class="ti ti-alert-triangle"></i>
                        </div>

                        <div>
                            <div class="latest-label">Latest backup</div>
                            <div class="latest-title">Backup failed</div>
                        </div>

                    {% endif %}

                </div>


                <div class="latest-grid">

                    <div class="latest-item">

                        <small>Date</small>

                        <div>
                            {{ latest.started_at.strftime("%Y-%m-%d %H:%M")
                               if latest.started_at else "N/A" }}
                        </div>

                    </div>


                    <div class="latest-item">

                        <small>Files</small>

                        <div>
                            {{ latest.files_count }}
                        </div>

                    </div>


                    <div class="latest-item">

                        <small>Snapshot ID</small>

                        <div class="mono">

                            {{ latest.snapshot_id or "N/A" }}

                        </div>

                    </div>

                </div>

            {% else %}

                <div class="latest-label">
                    Latest backup
                </div>

                <p class="empty">

                    No backup yet. Select Backup now to create your first one.

                </p>

            {% endif %}

        </div>

    </div>



    <!-- Summary Cards -->

    <div class="block">

        <div class="stats">


            <div class="stat">

                <div class="label">
                    Total backups
                </div>

                <div class="number">
                    {{ total_backups }}
                </div>

            </div>


            <div class="stat">

                <div class="label">
                    Successful
                </div>

                <div class="number ok">
                    {{ successful }}
                </div>

            </div>


            <div class="stat">

                <div class="label">
                    Failed
                </div>

                <div class="number bad">
                    {{ failed }}
                </div>

            </div>


            <div class="stat">

                <div class="label">
                    System status
                </div>

                <div class="online">

                    <span class="dot"></span>

                    Online

                </div>

            </div>


        </div>

    </div>



    <!-- Backup Activity -->
    <div class="block">

        <div class="panel">

            <h2 class="section-title">
                Backup activity
            </h2>


<div class="chart-container">

    <canvas id="backupChart"></canvas>

    {% if not chart_data %}
        <p class="empty" style="text-align:center; margin-top:10px;">
            No backup activity yet.
        </p>
    {% endif %}

</div>

        </div>



</div>



<script>

const chartElement =
    document.getElementById("backupChart");


const chartLabels =
    {{ chart_labels | tojson }};


const chartData =
    {{ chart_data | tojson }};


if (chartElement && typeof Chart !== "undefined") {

    Chart.defaults.color = "#94a3b8";

    new Chart(chartElement, {

        type: "bar",

        data: {

            labels: chartLabels,

            datasets: [

                {

                    label: "Backup operations",

                    data: chartData,

                    backgroundColor: "#0d9488",

                    hoverBackgroundColor: "#2dd4bf",

                    borderRadius: 6,

                    maxBarThickness: 40

                }

            ]

        },


        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: false

                }

            },

            scales: {

                x: {

                    grid: {

                        display: false

                    },

                    border: {

                        color: "#334155"

                    }

                },

                y: {

                    beginAtZero: true,

                    ticks: {

                        precision: 0

                    },

                    grid: {

                        color: "#334155"

                    },

                    border: {

                        display: false

                    }

                }

            }

        }

    });

}

</script>


</body>

</html>
"""


# =========================================================
# Login Page
# =========================================================

LOGIN_HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Cloud Backup - Login</title>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.box {
    width: 360px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 30px;
}

h1 {
    text-align: center;
    color: #2dd4bf;
    margin-bottom: 25px;
}

label {
    display: block;
    margin-bottom: 7px;
    color: #94a3b8;
}

input {
    width: 100%;
    padding: 12px;
    margin-bottom: 18px;
    box-sizing: border-box;
    border: 1px solid #334155;
    border-radius: 8px;
    background: #0f172a;
    color: white;
}

button {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: #14b8a6;
    color: #042f2e;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #2dd4bf;
}

.message {
    background: #052e16;
    color: #86efac;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.error {
    background: #450a0a;
    color: #fca5a5;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.link {
    text-align: center;
    margin-top: 20px;
}

a {
    color: #2dd4bf;
    text-decoration: none;
}

</style>

</head>

<body>

<div class="box">

<h1>Cloud Backup</h1>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="POST">

<label>Email</label>

<input
    type="email"
    name="email"
    required
>

<label>Password</label>

<input
    type="password"
    name="password"
    required
>

<button type="submit">
    Login
</button>

</form>

<div class="link">

Don't have an account?

<a href="{{ url_for('register') }}">
    Register
</a>

</div>

</div>

</body>

</html>

"""


# =========================================================
# Register Page
# =========================================================

REGISTER_HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Cloud Backup - Register</title>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.box {
    width: 360px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 30px;
}

h1 {
    text-align: center;
    color: #2dd4bf;
    margin-bottom: 25px;
}

label {
    display: block;
    margin-bottom: 7px;
    color: #94a3b8;
}

input {
    width: 100%;
    padding: 12px;
    margin-bottom: 18px;
    box-sizing: border-box;
    border: 1px solid #334155;
    border-radius: 8px;
    background: #0f172a;
    color: white;
}

button {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background: #14b8a6;
    color: #042f2e;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #2dd4bf;
}

.error {
    background: #450a0a;
    color: #fca5a5;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
}

.link {
    text-align: center;
    margin-top: 20px;
}

a {
    color: #2dd4bf;
    text-decoration: none;
}

</style>

</head>

<body>

<div class="box">

<h1>Create Account</h1>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="POST">

<label>Email</label>

<input
    type="email"
    name="email"
    required
>

<label>Password</label>

<input
    type="password"
    name="password"
    required
>

<label>Confirm Password</label>

<input
    type="password"
    name="confirm_password"
    required
>

<button type="submit">
    Register
</button>

</form>

<div class="link">

Already have an account?

<a href="{{ url_for('login') }}">
    Login
</a>

</div>

</div>

</body>

</html>

"""


# =========================================================
# Home / Dashboard
# =========================================================

@app.route("/")
@login_required
def home():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    # Total backups

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM backup_logs
    """)

    total_backups = cursor.fetchone()["total"]


    # Successful backups

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM backup_logs
        WHERE status = 'SUCCESS'
    """)

    successful = cursor.fetchone()["total"]


    # Failed backups

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM backup_logs
        WHERE status = 'FAILED'
    """)

    failed = cursor.fetchone()["total"]


    # Latest backup

    cursor.execute("""
        SELECT
            id,
            started_at,
            finished_at,
            status,
            files_count,
            snapshot_id,
            message
        FROM backup_logs
        ORDER BY started_at DESC
        LIMIT 1
    """)

    latest = cursor.fetchone()


    # Chart data

    cursor.execute("""
        SELECT
            DATE(started_at) AS backup_date,
            COUNT(*) AS count
        FROM backup_logs
        GROUP BY DATE(started_at)
        ORDER BY DATE(started_at)
    """)

    chart_rows = cursor.fetchall()


    cursor.close()

    connection.close()


    chart_labels = [
        str(row["backup_date"])
        for row in chart_rows
    ]

    chart_data = [
        row["count"]
        for row in chart_rows
    ]


    message = session.pop("message", None)

    error = session.pop("error", None)


    return render_template_string(

        DASHBOARD_HTML,

        email=session.get("email"),

        latest=latest,

        total_backups=total_backups,

        successful=successful,

        failed=failed,

        chart_labels=chart_labels,

        chart_data=chart_data,

        message=message,

        error=error

    )


# =========================================================
# Register
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    error = None


    if request.method == "POST":

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        if not email or not password:

            error = "Email and password are required."

            return render_template_string(
                REGISTER_HTML,
                error=error
            )


        if password != confirm_password:

            error = "Passwords do not match."

            return render_template_string(
                REGISTER_HTML,
                error=error
            )


        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing = cursor.fetchone()


        if existing:

            cursor.close()

            connection.close()

            error = "This email is already registered."

            return render_template_string(
                REGISTER_HTML,
                error=error
            )


        password_hash = generate_password_hash(password)


        cursor.execute(
            """
            INSERT INTO users
            (email, password_hash)
            VALUES (%s, %s)
            """,
            (email, password_hash)
        )


        connection.commit()


        cursor.close()

        connection.close()


        return redirect(url_for("login"))


    return render_template_string(
        REGISTER_HTML,
        error=error
    )


# =========================================================
# Login
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None


    if request.method == "POST":

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")


        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT
                id,
                email,
                password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )


        user = cursor.fetchone()


        cursor.close()

        connection.close()


        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["user_id"] = user["id"]

            session["email"] = user["email"]


            return redirect(url_for("home"))


        error = "Invalid email or password."


    return render_template_string(
        LOGIN_HTML,
        error=error
    )


# =========================================================
# Logout
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# Backup
# =========================================================

@app.route("/backup")
@login_required
def backup():

    started_at = datetime.now()

    connection = get_db_connection()

    cursor = connection.cursor()


    # Create initial log record

    cursor.execute(
        """
        INSERT INTO backup_logs
        (
            started_at,
            status,
            files_count,
            message
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            started_at,
            "FAILED",
            0,
            "Backup started"
        )
    )


    log_id = cursor.lastrowid

    connection.commit()


    try:

        result = subprocess.run(
            [
                "/home/hano/cloude_backup/restic_backup.sh"
            ],
            capture_output=True,
            text=True,
            timeout=3600
        )

        finished_at = datetime.now()


        if result.returncode == 0:

            output = result.stdout


            snapshot_id = None


            for line in output.splitlines():

                if line.startswith("snapshot ") and " saved" in line:

                    snapshot_id = (
                        line
                        .replace("snapshot ", "")
                        .replace(" saved", "")
                        .strip()
                    )


            files_count = 0


            for line in output.splitlines():

                if line.strip().startswith("processed"):

                    parts = line.strip().split()

                    try:

                        files_index = parts.index("files,")

                        files_count = int(
                            parts[files_index - 1]
                        )

                    except (ValueError, IndexError):

                        files_count = 0


            cursor.execute(
                """
                UPDATE backup_logs
                SET
                    finished_at = %s,
                    status = %s,
                    files_count = %s,
                    snapshot_id = %s,
                    message = %s
                WHERE id = %s
                """,
                (
                    finished_at,
                    "SUCCESS",
                    files_count,
                    snapshot_id,
                    output,
                    log_id
                )
            )


            connection.commit()


            session["message"] = (
                "Backup completed successfully."
            )


        else:

            error_message = (
                result.stderr
                or result.stdout
                or "Backup failed."
            )


            cursor.execute(
                """
                UPDATE backup_logs
                SET
                    finished_at = %s,
                    status = %s,
                    message = %s
                WHERE id = %s
                """,
                (
                    finished_at,
                    "FAILED",
                    error_message,
                    log_id
                )
            )


            connection.commit()


            session["error"] = (
                "Backup failed: " + error_message
            )


    except Exception as exc:

        finished_at = datetime.now()


        cursor.execute(
            """
            UPDATE backup_logs
            SET
                finished_at = %s,
                status = %s,
                message = %s
            WHERE id = %s
            """,
            (
                finished_at,
                "FAILED",
                str(exc),
                log_id
            )
        )


        connection.commit()


        session["error"] = (
            "Backup error: " + str(exc)
        )


    finally:

        cursor.close()

        connection.close()


    return redirect(url_for("home"))


# =========================================================
# Backup History
# =========================================================

@app.route("/history")
@login_required
def history():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    cursor.execute(
        """
        SELECT
            id,
            started_at,
            finished_at,
            status,
            files_count,
            snapshot_id,
            message
        FROM backup_logs
        ORDER BY started_at DESC
        """
    )


    backups = cursor.fetchall()


    cursor.close()

    connection.close()


    return render_template_string(
        """

        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Backup History</title>

        <style>

        body {
            margin: 0;
            padding: 30px;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
        }

        .container {
            max-width: 1100px;
            margin: auto;
        }

        h1 {
            color: #2dd4bf;
        }

        a {
            color: #2dd4bf;
            text-decoration: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
            background: #1e293b;
        }

        th, td {
            padding: 12px;
            border: 1px solid #334155;
            text-align: left;
        }

        th {
            color: #2dd4bf;
        }

        .success {
            color: #4ade80;
        }

        .failed {
            color: #f87171;
        }

        </style>

        </head>

        <body>

        <div class="container">

        <h1>Backup History</h1>

        <p>
            <a href="{{ url_for('home') }}">
                ← Back to Dashboard
            </a>
        </p>

        <table>

        <tr>

        <th>ID</th>
        <th>Started</th>
        <th>Finished</th>
        <th>Status</th>
        <th>Files</th>
        <th>Snapshot</th>

        </tr>

        {% for backup in backups %}

        <tr>

        <td>{{ backup.id }}</td>

        <td>{{ backup.started_at }}</td>

        <td>{{ backup.finished_at or "N/A" }}</td>

        <td class="{{
            'success'
            if backup.status == 'SUCCESS'
            else 'failed'
        }}">
            {{ backup.status }}
        </td>

        <td>{{ backup.files_count }}</td>

        <td>{{ backup.snapshot_id or "N/A" }}</td>

        </tr>

        {% endfor %}

        </table>

        </div>

        </body>

        </html>

        """,

        backups=backups
    )


# =========================================================
# Restore Latest
# =========================================================

@app.route("/restore")
@login_required
def restore():

    try:

        subprocess.run(
            [
                "rm",
                "-rf",
                RESTORE_PATH
            ],
            check=True
        )


        subprocess.run(
            [
                "mkdir",
                "-p",
                RESTORE_PATH
            ],
            check=True
        )


        result = subprocess.run(
            [
                "/home/hano/cloude_backup/restic_restore.sh"
            ],
            capture_output=True,
            text=True,
            timeout=3600
        )

        if result.returncode == 0:

            session["message"] = (
                "Latest backup restored successfully."
            )

        else:

            session["error"] = (
                "Restore failed: "
                + (
                    result.stderr
                    or result.stdout
                )
            )


    except Exception as exc:

        session["error"] = (
            "Restore error: " + str(exc)
        )


    return redirect(url_for("home"))


# =========================================================
# Statistics
# =========================================================

@app.route("/statistics")
@login_required
def statistics():

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)


    cursor.execute(
        """
        SELECT
            status,
            COUNT(*) AS total
        FROM backup_logs
        GROUP BY status
        """
    )


    status_rows = cursor.fetchall()


    cursor.execute(
        """
        SELECT
            DATE(started_at) AS backup_date,
            COUNT(*) AS total
        FROM backup_logs
        GROUP BY DATE(started_at)
        ORDER BY DATE(started_at)
        """
    )


    daily_rows = cursor.fetchall()


    cursor.close()

    connection.close()


    return render_template_string(

        """

        <!DOCTYPE html>

        <html>

        <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Statistics</title>

        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>

        <style>

        body {
            margin: 0;
            padding: 30px;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        h1 {
            color: #2dd4bf;
        }

        a {
            color: #2dd4bf;
            text-decoration: none;
        }

        .panel {
            margin-top: 25px;
            padding: 25px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
        }

        .chart {
            position: relative;
            height: 350px;
        }

        </style>

        </head>

        <body>

        <div class="container">

        <h1>Backup Statistics</h1>

        <p>
            <a href="{{ url_for('home') }}">
                ← Back to Dashboard
            </a>
        </p>

        <div class="panel">

        <h2>Backup Activity</h2>

        <div class="chart">

        <canvas id="statisticsChart"></canvas>

        </div>

        </div>

        </div>


        <script>

        const labels =
            {{ labels | tojson }};

        const data =
            {{ data | tojson }};


        new Chart(

            document.getElementById(
                "statisticsChart"
            ),

            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Backup operations",

                            data: data,

                            borderColor:
                                "#2dd4bf",

                            backgroundColor:
                                "rgba(20,184,166,0.2)",

                            tension: 0.3,

                            fill: true

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false

                }

            }

        );

        </script>

        </body>

        </html>

        """,

        labels=[
            str(row["backup_date"])
            for row in daily_rows
        ],

        data=[
            row["total"]
            for row in daily_rows
        ]

    )


# =========================================================
# Status API
# =========================================================

@app.route("/status")
@login_required
def status():

    return {
        "status": "online",
        "restic_repository": RESTIC_REPO,
        "backup_source": BACKUP_SOURCE
    }


# =========================================================
# Run Flask
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
