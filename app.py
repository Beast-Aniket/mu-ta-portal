import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import json
import time
from datetime import date, datetime, timedelta
from io import BytesIO

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="Mumbai University TA Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DB_NAME = 'university_accounts.db'

# --- LISTS ---
EXAM_OPTIONS = [
    "BA Sem V", "BA Sem VI", "B.Com Sem V", "B.Com Sem VI", "B.Sc Sem V", "B.Sc Sem VI",
    "BACA Sem V", "BACA Sem VI", "B.Arch Sem VI", "B.Arch Sem X", "B.A.M.M.C Sem V", "B.A.M.M.C Sem VI",
    "B.Ed Sem V", "B.Ed Sem VI", "B.P.Ed Sem V", "B.P.Ed Sem VI", "B.Voc Sem V", "B.Voc Sem VI",
    "BAF Sem V", "BAF Sem VI", "BBI Sem V", "BBI Sem VI", "BFM Sem V", "BFM Sem VI",
    "BMS Sem V", "BMS Sem VI", "BTM Sem V", "BTM Sem VI", "L.L.B Sem V", "LLB Sem VI",
    "BLS/LLB Sem V", "BLS/LLB Sem VI", "BLS Sem V", "BLS Sem VI", "B.F.A. (Music)", "B.F.A. (Dance)",
    "Five yr degree course in Law", "BSW", "M.A. Sem I", "M.A. Sem II", "M.A. Sem III", "M.A. Sem IV",
    "M.Com Sem I", "M.Com Sem II", "M.Com Sem III", "M.Com Sem IV", "M.Sc Sem I", "M.Sc Sem II",
    "M.Sc Sem III", "M.Sc Sem IV", "MACJ Sem I", "MACJ Sem II", "MACJ Sem III", "MACJ Sem IV",
    "MAPR Sem I", "MAPR Sem II", "MAPR Sem III", "MAPR Sem IV", "MAEM Sem I", "MAEM Sem II",
    "MAEM Sem III", "MAEM Sem IV", "MP.Ed Sem I", "MP.Ed Sem II", "MP.Ed Sem III", "MP.Ed Sem IV",
    "M.Ed Sem I", "M.Ed Sem II", "M.Ed Sem III", "M.Ed Sem IV", "M.Voc Sem I", "M.Voc Sem II",
    "M.Voc Sem III", "M.Voc Sem IV", "MMM Sem I", "MMM Sem II", "MMM Sem III", "MMM Sem IV",
    "MMS Sem I", "MMS Sem II", "MMS Sem III", "MMS Sem IV", "MSW", "MFM", "MFSM", "MHRDM",
    "MFA (Music)", "MFA (Dance)", "MPA (Perf. Art)", "MLS (Lib. & Inf^n Sci)", "MCA Sem I",
    "MCA Sem II", "MCA Sem III", "MCA Sem IV", "MCA Sem V", "MCA Sem VI", "F.E. Sem I",
    "F.E. Sem II", "S.E. Sem III", "S.E. Sem IV", "T.E. Sem V", "T.E. Sem VI", "B.E. Sem VII",
    "B.E. Sem VIII", "M.Arch. Sem I", "M.Arch. Sem II", "B. Pharmacy Sem VII", "B. Pharmacy Sem VIII",
    "M. Pharm", "M.Tech Sem I", "M.Tech Sem II", "M.E. Sem I", "M.E. Sem II"
]

PURPOSE_OPTIONS = [
    "Paper Setting", "Moderation", "Supervision", 
    "Setting of Marklist", "Submission of Marksheet", "Proof Correction", 
    "Board of Examination", "Chairmans Instruction in Subject", 
    "Setting the Question Papers", "Exam Squad", "Conducting Practical/Viva", 
    "Revaluation Answer Book", "JCC Control Room", "PHD RRC Meeting", 
    "MPHARMA Viva", "Result Moderation", "Unfair Means", "Other"
]

# ==========================================
# 2. DYNAMIC STYLING
# ==========================================
def apply_dynamic_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
        
        [data-testid="stSidebar"] { background-color: #0e1117; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        
        input, textarea, select {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        div[data-baseweb="input"], div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border: 1px solid #aaa !important;
            border-radius: 6px !important;
        }
        div[data-baseweb="select"] span { color: #000000 !important; }
        
        .main-header {
            background: linear-gradient(90deg, #002147 0%, #004e92 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        .main-header h1 { color: white !important; margin: 0; }
        
        .section-header {
            margin-top: 20px; margin-bottom: 10px; padding: 8px 15px;
            background: rgba(212, 175, 55, 0.2);
            border-left: 5px solid #d4af37;
            font-weight: 600; border-radius: 4px;
        }
        
        .stButton > button {
            background-color: #002147; color: white;
            font-weight: 600; border-radius: 8px;
            transition: transform 0.2s;
        }
        .stButton > button:hover {
            background-color: #d4af37; color: #000;
            transform: scale(1.02);
        }
        
        #MainMenu, footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DATABASE FUNCTIONS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, password TEXT, role TEXT, full_name TEXT, photo BLOB)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS professors (
                    mobile_number TEXT PRIMARY KEY, full_name TEXT, 
                    address_res TEXT, address_prof TEXT, basic_pay REAL,
                    bank_name TEXT, ifsc_code TEXT, account_number TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS ta_bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    aadhaar_number TEXT, candidate_name TEXT, mobile_number TEXT, 
                    examination TEXT, subject TEXT, month_year TEXT, purpose_text TEXT, 
                    receipt_no TEXT, receipt_date DATE,
                    rly_from TEXT, rly_to TEXT, rly_ticket_no TEXT, rly_amount REAL,
                    bus_from TEXT, bus_to TEXT, bus_amount REAL,
                    car_from TEXT, car_to TEXT, car_vehicle_no TEXT, car_km REAL, car_amount REAL,
                    lumpsum_allowance REAL, da_amount REAL, grand_total REAL,
                    bank_name TEXT, ifsc_code TEXT, account_number TEXT,
                    submitted_on DATETIME DEFAULT CURRENT_TIMESTAMP,
                    submitted_by TEXT,
                    status TEXT DEFAULT 'Submitted')''')

    c.execute('''CREATE TABLE IF NOT EXISTS bill_dates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, bill_id INTEGER,
                    visit_date DATE, place TEXT,
                    FOREIGN KEY (bill_id) REFERENCES ta_bills (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS edit_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER, username TEXT, reason TEXT,
                    proposed_data TEXT, 
                    request_date DATE DEFAULT CURRENT_DATE,
                    status TEXT DEFAULT 'Pending')''')

    # SuperAdmin
    admin_pw = hashlib.sha256("muadmin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, 'Admin', 'Registrar')", 
              ('superadmin', admin_pw))
    
    conn.commit()
    conn.close()

def log_activity(user, action):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (username, action) VALUES (?, ?)", (user, action))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT timestamp, username, action FROM activity_logs ORDER BY id DESC", conn)
    conn.close()
    return df

# --- USER MANAGEMENT ---
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT username FROM users", conn)
    conn.close()
    return df['username'].tolist()

def get_user_details(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, role, full_name, photo, password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'username': row[0], 'role': row[1], 'full_name': row[2], 'photo': row[3], 'password_hash': row[4]}
    return None

def create_user(username, password, name, role, photo_bytes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hashlib.sha256(str.encode(password)).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, role, full_name, photo) VALUES (?,?,?,?,?)",
                  (username, hashed_pw, role, name, photo_bytes))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user(username, password, name, role, photo_bytes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    final_pw_hash = None
    if password and password.strip() != "":
        final_pw_hash = hashlib.sha256(str.encode(password)).hexdigest()
    else:
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        final_pw_hash = c.fetchone()[0]

    final_photo = photo_bytes
    if final_photo is None:
        c.execute("SELECT photo FROM users WHERE username=?", (username,))
        final_photo = c.fetchone()[0]

    try:
        c.execute("""UPDATE users SET password=?, role=?, full_name=?, photo=? WHERE username=?""",
                  (final_pw_hash, role, name, final_photo, username))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()

def delete_user(username):
    if username == 'superadmin':
        return False
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()

def get_user_photo(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT photo FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()
    return data[0] if data else None

def get_professor(mobile):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM professors WHERE mobile_number=?", conn, params=(mobile,))
    conn.close()
    return df.iloc[0] if not df.empty else None

# --- BILL LOGIC ---
def get_bills_by_aadhaar(aadhaar):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("""
            SELECT id, candidate_name as 'Full Name', examination as Exam, 
                   grand_total as Amount, submitted_on as Date, status as 'Current Status',
                   aadhaar_number as 'Aadhaar'
            FROM ta_bills WHERE aadhaar_number=? ORDER BY id DESC""", conn, params=(aadhaar,))
    except:
        df = pd.DataFrame() 
    conn.close()
    return df

def get_bills_by_user(username):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("""
            SELECT id, candidate_name as 'Full Name', examination as Exam, 
                   grand_total as Amount, submitted_on as Date, status as 'Current Status',
                   aadhaar_number as 'Aadhaar'
            FROM ta_bills WHERE submitted_by=? ORDER BY id DESC""", conn, params=(username,))
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def get_bills_by_visit_date(aadhaar, start_date, end_date):
    """Filter bills that have at least one visit in the given range."""
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT DISTINCT t.id, t.candidate_name as 'Full Name', t.examination as Exam, 
               t.grand_total as Amount, t.submitted_on as Date, t.status as 'Current Status'
        FROM ta_bills t
        JOIN bill_dates bd ON t.id = bd.bill_id
        WHERE t.aadhaar_number = ? AND bd.visit_date BETWEEN ? AND ?
        ORDER BY t.id DESC
    """
    try:
        df = pd.read_sql_query(query, conn, params=(aadhaar, str(start_date), str(end_date)))
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def get_bill_details(bill_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM ta_bills WHERE id=?", conn, params=(bill_id,))
    visits_df = pd.read_sql_query("SELECT visit_date, place FROM bill_dates WHERE bill_id=?", conn, params=(bill_id,))
    conn.close()
    if df.empty: return None, []
    return df.iloc[0].to_dict(), visits_df.to_dict('records')

def submit_bill(data, visits, username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""INSERT OR REPLACE INTO professors 
                     (mobile_number, full_name, address_res, address_prof, basic_pay, bank_name, ifsc_code, account_number)
                     VALUES (?,?,?,?,?,?,?,?)""", 
                  (data['mobile'], data['name'], data['addr_res'], data['addr_prof'], data['basic'], 
                   data['bank_name'], data['ifsc'], data['acc_no']))
        
        c.execute('''INSERT INTO ta_bills (
                        aadhaar_number, candidate_name, mobile_number, examination, subject, month_year, 
                        purpose_text, receipt_no, receipt_date, 
                        rly_from, rly_to, rly_ticket_no, rly_amount,
                        bus_from, bus_to, bus_amount, 
                        car_from, car_to, car_vehicle_no, car_km, car_amount, 
                        lumpsum_allowance, da_amount, grand_total, 
                        bank_name, ifsc_code, account_number, submitted_by
                     ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (data['aadhaar'], data['name'], data['mobile'], data['exam'], data['subject'], data['month'], 
                   data['purpose'], data['receipt_no'], data['receipt_date'], 
                   data['rly_f'], data['rly_t'], data['rly_tkt'], data['rly_a'],
                   data['bus_f'], data['bus_t'], data['bus_a'], 
                   data['car_f'], data['car_t'], data['car_no'], data['car_k'], data['car_a'],
                   data['lumpsum'], data['da'], data['total'], 
                   data['bank_name'], data['ifsc'], data['acc_no'], username))
        
        bill_id = c.lastrowid
        for v in visits:
            c.execute("INSERT INTO bill_dates (bill_id, visit_date, place) VALUES (?,?,?)", 
                      (bill_id, str(v['date']), v['place']))
        conn.commit()
        return bill_id
    except Exception as e:
        print(e)
        return None
    finally:
        conn.close()

# --- EDIT REQUESTS ---
def request_update_existing(bill_id, username, reason, full_data_json):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO edit_requests (bill_id, username, reason, proposed_data, status) VALUES (?,?,?,?,?)", 
              (bill_id, username, reason, full_data_json, 'Pending'))
    c.execute("UPDATE ta_bills SET status = 'Pending Approval' WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()

def approve_update_existing(request_id, bill_id, proposed_json):
    try:
        data = json.loads(proposed_json)
        main_data = data['main']
        visits = data['visits']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""UPDATE ta_bills SET 
                     aadhaar_number=?, candidate_name=?, mobile_number=?, examination=?, subject=?, month_year=?, 
                     purpose_text=?, receipt_no=?, receipt_date=?, 
                     rly_from=?, rly_to=?, rly_ticket_no=?, rly_amount=?,
                     bus_from=?, bus_to=?, bus_amount=?, 
                     car_from=?, car_to=?, car_vehicle_no=?, car_km=?, car_amount=?, 
                     lumpsum_allowance=?, da_amount=?, grand_total=?, 
                     bank_name=?, ifsc_code=?, account_number=?, status='Approved'
                     WHERE id=?""", 
                  (main_data['aadhaar'], main_data['name'], main_data['mobile'], main_data['exam'], main_data['subject'], main_data['month'], 
                   main_data['purpose'], main_data['receipt_no'], main_data['receipt_date'], 
                   main_data['rly_f'], main_data['rly_t'], main_data['rly_tkt'], main_data['rly_a'],
                   main_data['bus_f'], main_data['bus_t'], main_data['bus_a'], 
                   main_data['car_f'], main_data['car_t'], main_data['car_no'], main_data['car_k'], main_data['car_a'],
                   main_data['lumpsum'], main_data['da'], main_data['total'], 
                   main_data['bank_name'], main_data['ifsc'], main_data['acc_no'], bill_id))
        
        c.execute("DELETE FROM bill_dates WHERE bill_id=?", (bill_id,))
        for v in visits:
            c.execute("INSERT INTO bill_dates (bill_id, visit_date, place) VALUES (?,?,?)", 
                      (bill_id, v['date'], v['place']))
        
        c.execute("UPDATE edit_requests SET status='Approved' WHERE id=?", (request_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def get_user_edit_status(username):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id as Request_ID, bill_id as Bill_ID, reason, status, request_date FROM edit_requests WHERE username=? ORDER BY id DESC", conn, params=(username,))
    conn.close()
    return df

# --- REPORTING (UPDATED FOR FULL COLUMNS) ---
def get_report_data(date_filter=None, username=None, aadhaar=None):
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT 
        t.id as 'Bill ID', t.submitted_on as 'Submission Date',
        t.submitted_by as 'User', t.status as 'Status',
        t.aadhaar_number as 'Aadhaar', t.candidate_name as 'Full Name', t.mobile_number as 'Mobile',
        t.examination as 'Exam', t.subject as 'Subject', t.month_year as 'Month/Year',
        t.purpose_text as 'Purpose', t.receipt_no as 'Receipt No', t.receipt_date as 'Receipt Date',
        t.bank_name as 'Bank', t.ifsc_code as 'IFSC', t.account_number as 'Account No',
        t.rly_from as 'Rly From', t.rly_to as 'Rly To', t.rly_ticket_no as 'Rly Ticket', t.rly_amount as 'Rly Amt',
        t.bus_from as 'Bus From', t.bus_to as 'Bus To', t.bus_amount as 'Bus Amt',
        t.car_from as 'Car From', t.car_to as 'Car To', t.car_vehicle_no as 'Car No', t.car_km as 'Car KM', t.car_amount as 'Car Amt',
        t.lumpsum_allowance as 'Lumpsum', t.da_amount as 'DA', t.grand_total as 'Grand Total',
        GROUP_CONCAT(bd.visit_date, ', ') as 'Visit Dates',
        GROUP_CONCAT(bd.place, ', ') as 'Visit Places'
    FROM ta_bills t
    LEFT JOIN bill_dates bd ON t.id = bd.bill_id
    WHERE 1=1
    """
    params = []
    
    if date_filter:
        query += " AND date(t.submitted_on) = ?"
        params.append(str(date_filter))
    
    if username:
        query += " AND t.submitted_by = ?"
        params.append(username)
        
    if aadhaar:
        query += " AND t.aadhaar_number = ?"
        params.append(aadhaar)
        
    query += " GROUP BY t.id ORDER BY t.id ASC" # Latest at bottom (Ascending Order)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def safe_float(val_str):
    if not val_str: return 0.0
    try: return float(str(val_str))
    except: return 0.0

# ==========================================
# 4. AUTHENTICATION
# ==========================================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def login_container():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<div class='main-header'><h1>🏛️ MUMBAI UNIVERSITY</h1><p>TA & Remuneration Portal</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("🔐 Sign In")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')
                if st.form_submit_button("Secure Login", use_container_width=True):
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute('SELECT password, role FROM users WHERE username = ?', (username,))
                    data = c.fetchone()
                    conn.close()
                    if data and check_hashes(password, data[0]):
                        st.session_state.logged_in = True
                        st.session_state.user = username
                        st.session_state.role = data[1]
                        log_activity(username, "Logged In")
                        st.rerun()
                    else:
                        st.error("Invalid Credentials")

# ==========================================
# 5. ADMIN DASHBOARD
# ==========================================
def admin_dashboard():
    st.markdown('<div class="main-header"><h1>🦅 SuperAdmin Control Panel</h1></div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Users", "🔍 Search", "🔔 Edit Requests", "📊 Logs", "📥 Reports"])
    
    with tab1: # Manage Users
        mode = st.radio("Action Mode:", ["Create New User", "Edit Existing User", "Delete User"], horizontal=True)
        st.divider()

        if mode == "Create New User":
            st.subheader("Create New User")
            with st.container(border=True):
                with st.form("create_user_form"):
                    c1, c2 = st.columns(2)
                    new_user = c1.text_input("Username (Unique ID)")
                    new_pass = c2.text_input("Password", type="password")
                    c3, c4 = st.columns(2)
                    new_name = c3.text_input("Full Name")
                    new_role = c4.selectbox("Role", ["User", "Admin"])
                    new_photo = st.file_uploader("Upload Profile Photo", type=['png', 'jpg', 'jpeg'])
                    
                    if st.form_submit_button("Create User", use_container_width=True):
                        if new_user and new_pass and new_name:
                            photo_bytes = new_photo.getvalue() if new_photo else None
                            if create_user(new_user, new_pass, new_name, new_role, photo_bytes):
                                log_activity(st.session_state.user, f"Created user {new_user}")
                                st.success("User created successfully!")
                            else:
                                st.error("Username already exists!")
                        else:
                            st.warning("Fill all required fields.")
        
        elif mode == "Edit Existing User":
            st.subheader("Edit User Details")
            all_users = get_all_users()
            selected_user = st.selectbox("Select User to Edit", all_users)
            
            if selected_user:
                current_data = get_user_details(selected_user)
                with st.container(border=True):
                    with st.form("edit_user_form"):
                        c1, c2 = st.columns(2)
                        c1.text_input("Username", value=selected_user, disabled=True)
                        edit_pass = c2.text_input("New Password", placeholder="Leave blank to keep current")
                        c3, c4 = st.columns(2)
                        edit_name = c3.text_input("Full Name", value=current_data['full_name'])
                        role_options = ["User", "Admin"]
                        def_ix = role_options.index(current_data['role']) if current_data['role'] in role_options else 0
                        edit_role = c4.selectbox("Role", role_options, index=def_ix)
                        st.markdown("<b>Update Photo (Optional)</b>", unsafe_allow_html=True)
                        edit_photo = st.file_uploader("Upload New Photo", type=['png', 'jpg', 'jpeg'])
                        
                        if st.form_submit_button("Update User Details", use_container_width=True):
                            photo_bytes = edit_photo.getvalue() if edit_photo else None
                            if update_user(selected_user, edit_pass, edit_name, edit_role, photo_bytes):
                                log_activity(st.session_state.user, f"Updated user {selected_user}")
                                st.success("Details updated successfully!")
                            else:
                                st.error("Failed to update user.")

        elif mode == "Delete User":
            st.subheader("🗑️ Delete User")
            all_users = get_all_users()
            safe_users = [u for u in all_users if u != 'superadmin']
            
            if not safe_users:
                st.info("No users available to delete.")
            else:
                del_user = st.selectbox("Select User to Permanently Delete", safe_users)
                if del_user:
                    st.warning(f"⚠️ Are you sure you want to delete **{del_user}**? This action cannot be undone.")
                    if st.button("🚨 YES, DELETE USER", type="primary"):
                        if delete_user(del_user):
                            log_activity(st.session_state.user, f"Deleted user {del_user}")
                            st.success("User deleted.")
                            st.rerun()
                        else:
                            st.error("Could not delete user.")

    # --- SEARCH ---
    with tab2:
        st.subheader("🔍 Search Bill History")
        with st.container(border=True):
            search_query = st.text_input("Enter Name, Mobile or Aadhaar", placeholder="Search...")
            if st.button("Search Records", type="primary"):
                if search_query:
                    conn = sqlite3.connect(DB_NAME)
                    sql = """SELECT id, candidate_name, mobile_number, aadhaar_number, grand_total, status, submitted_on 
                             FROM ta_bills WHERE candidate_name LIKE ? OR mobile_number LIKE ? OR aadhaar_number LIKE ?"""
                    term = f"%{search_query}%"
                    res = pd.read_sql_query(sql, conn, params=(term, term, term))
                    conn.close()
                    if not res.empty:
                        st.dataframe(res, use_container_width=True)
                    else:
                        st.warning("No records found.")

    # --- EDIT REQUESTS (UPDATED LOGIC) ---
    with tab3:
        st.subheader("Pending Edit Requests")
        conn = sqlite3.connect(DB_NAME)
        req_df = pd.read_sql_query("SELECT * FROM edit_requests WHERE status='Pending'", conn)
        conn.close()
        
        if not req_df.empty:
            for index, row in req_df.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.warning(f"**{row['username']}** requests update for **Bill #{row['bill_id']}**")
                    c1.info(f"Reason: {row['reason']}")
                    
                    if c2.button("👁️ View & Approve", key=f"view_{row['id']}"):
                        if approve_update_existing(row['id'], row['bill_id'], row['proposed_data']):
                            log_activity("SuperAdmin", f"Approved update for Bill #{row['bill_id']}")
                            st.success("Bill Updated Successfully!")
                            st.rerun()
                        else:
                            st.error("Error updating bill.")
        else:
            st.success("No pending requests.")

    # --- LOGS ---
    with tab4:
        st.subheader("System Logs")
        log_df = get_logs()
        st.dataframe(log_df, use_container_width=True)
        if not log_df.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                log_df.to_excel(writer, index=False)
            st.download_button("📥 Download Logs (Excel)", output.getvalue(), "System_Logs.xlsx")

    # --- REPORTS (UPDATED EXCEL with Multi-Sheets) ---
    with tab5:
        st.subheader("Daily Report (One Row Per Bill - Ascending)")
        report_date = st.date_input("Select Date", value=date.today())
        
        if st.button("Generate & Download Report"):
            df = get_report_data(date_filter=report_date)
            if not df.empty:
                st.success(f"Found {len(df)} records.")
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Master Summary', index=False)
                    if 'User' in df.columns:
                        unique_users = df['User'].unique()
                        for user in unique_users:
                            user_df = df[df['User'] == user]
                            safe_sheet_name = str(user)[:30].replace(":", "").replace("/", "")
                            user_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                st.download_button("📥 Download Daily Report (Multi-Sheet)", output.getvalue(), f"MU_Report_{report_date}.xlsx", type="primary")
            else:
                st.info("No bills found for this date.")

# ==========================================
# 6. USER PORTAL
# ==========================================
def user_portal():
    st.markdown('<div class="main-header"><h1>🎓 TA BILL ENTRY</h1></div>', unsafe_allow_html=True)
    
    # Session State (Robust Init moved to main, but double check here)
    if "aadhaar_verified" not in st.session_state: st.session_state.aadhaar_verified = False
    if "edit_bill_id" not in st.session_state: st.session_state.edit_bill_id = None
    if "aadhaar_exists_msg" not in st.session_state: st.session_state.aadhaar_exists_msg = False

    tab1, tab2, tab3 = st.tabs(["📝 Bill Entry Form", "📜 My History", "🕒 Track Requests"])

    # --- TAB 1: FORM & AADHAAR ---
    with tab1:
        if not st.session_state.aadhaar_verified:
            # 1. AADHAAR INPUT VIEW
            with st.container(border=True):
                st.subheader("Step 1: Enter Aadhaar")
                aadhaar_input = st.text_input("Aadhaar Number (12 Digits)", max_chars=12)
                if st.button("Proceed"):
                    if len(aadhaar_input) == 12 and aadhaar_input.isdigit():
                        check_df = get_bills_by_aadhaar(aadhaar_input)
                        if not check_df.empty:
                            st.session_state.aadhaar_exists_msg = True 
                        st.session_state.current_aadhaar = aadhaar_input
                        st.session_state.aadhaar_verified = True
                        st.rerun()
                    else:
                        st.error("Invalid Aadhaar Number")
        else:
            # 2. BILL FORM VIEW
            if st.session_state.aadhaar_exists_msg:
                st.toast("⚠️ Records found for this Aadhaar! Check 'My History' tab.", icon="📂")
                st.info(f"Records found for {st.session_state.current_aadhaar}. You can view them in the 'My History' tab.")
                st.session_state.aadhaar_exists_msg = False

            c_info, c_btn = st.columns([3, 1])
            c_info.success(f"🆔 Active Aadhaar: **{st.session_state.current_aadhaar}**")
            if c_btn.button("🔄 Change", key="change_aadhaar"):
                st.session_state.aadhaar_verified = False
                st.session_state.current_aadhaar = ""
                st.session_state.edit_bill_id = None
                st.rerun()

            # --- Check if Cloning from History ---
            if st.session_state.edit_bill_id:
                st.warning(f"⚠️ CLONING MODE: Editing data from Bill #{st.session_state.edit_bill_id}. Submitting will create a NEW Bill ID.")

            # --- PRE-FILL LOGIC ---
            pf_name, pf_mobile, pf_basic = "", "", ""
            pf_bank, pf_ifsc, pf_acc = "", "", ""
            pf_addr_res, pf_addr_prof = "", ""
            pf_exam, pf_sub, pf_my, pf_pur, pf_rec, pf_rec_d = EXAM_OPTIONS[0], "", "", PURPOSE_OPTIONS[0], "", None
            pf_rf, pf_rt, pf_rtk, pf_ra = "", "", "", "0.00"
            pf_bf, pf_bt, pf_ba = "", "", "0.00"
            pf_cf, pf_ct, pf_cn, pf_ck, pf_ca = "", "", "", "0.00", "0.00"
            pf_lump, pf_da = "200.00", "0.00"
            pf_visits = []

            # LOAD DATA
            if st.session_state.edit_bill_id:
                bd, v_data = get_bill_details(st.session_state.edit_bill_id)
                if bd:
                    pf_name, pf_mobile = bd.get('candidate_name',''), bd.get('mobile_number','')
                    pd_info = get_professor(pf_mobile)
                    if pd_info is not None:
                        pf_basic = str(pd_info['basic_pay'])
                        pf_bank, pf_ifsc, pf_acc = pd_info['bank_name'], pd_info['ifsc_code'], pd_info['account_number']
                        pf_addr_res, pf_addr_prof = pd_info['address_res'], pd_info['address_prof']
                    
                    pf_exam = bd.get('examination', EXAM_OPTIONS[0])
                    pf_sub, pf_my = bd.get('subject',''), bd.get('month_year','')
                    pf_pur = bd.get('purpose_text', PURPOSE_OPTIONS[0])
                    pf_rec = bd.get('receipt_no','')
                    if bd.get('receipt_date'): pf_rec_d = datetime.strptime(bd['receipt_date'], '%Y-%m-%d').date()
                    
                    pf_rf, pf_rt, pf_rtk, pf_ra = bd['rly_from'], bd['rly_to'], bd['rly_ticket_no'], str(bd['rly_amount'])
                    pf_bf, pf_bt, pf_ba = bd['bus_from'], bd['bus_to'], str(bd['bus_amount'])
                    pf_cf, pf_ct, pf_cn, pf_ck, pf_ca = bd['car_from'], bd['car_to'], bd['car_vehicle_no'], str(bd['car_km']), str(bd['car_amount'])
                    pf_lump, pf_da = str(bd.get('lumpsum_allowance', 0.0)), str(bd.get('da_amount', 0.0))
                    
                    for v in v_data: pf_visits.append({'date': datetime.strptime(v['visit_date'], '%Y-%m-%d').date(), 'place': v['place']})

            # --- FORM FIELDS ---
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                mobile = c1.text_input("Mobile No", value=pf_mobile)
                name = c2.text_input("Full Name", value=pf_name)
                basic_pay_str = c3.text_input("Basic Pay (Ref Only)", value=pf_basic)
                
                c4, c5, c6 = st.columns(3)
                bank_name = c4.text_input("Bank Name", value=pf_bank)
                ifsc = c5.text_input("IFSC Code", value=pf_ifsc)
                acc_no = c6.text_input("Account No", value=pf_acc)
                
                c7, c8 = st.columns(2)
                addr_res = c7.text_area("Res Address", value=pf_addr_res, height=70)
                addr_prof = c8.text_area("Prof Address", value=pf_addr_prof, height=70)
                
                st.subheader("Visit Dates")
                if "rows" not in st.session_state: st.session_state.rows = 1
                if st.session_state.edit_bill_id and len(pf_visits) > 0: st.session_state.rows = len(pf_visits)
                
                visits = []
                for i in range(st.session_state.rows):
                    vc1, vc2 = st.columns(2)
                    d_val = pf_visits[i]['date'] if i < len(pf_visits) else date.today()
                    p_val = pf_visits[i]['place'] if i < len(pf_visits) else ""
                    vd = vc1.date_input(f"Date {i+1}", value=d_val, key=f"d_{i}")
                    vp = vc2.text_input(f"Place {i+1}", value=p_val, key=f"p_{i}")
                    visits.append({'date': str(vd), 'place': vp})
                if st.button("➕ Add Date"): 
                    st.session_state.rows += 1
                    st.rerun()

                st.subheader("Exam & Purpose")
                e1, e2, e3 = st.columns(3)
                exam = e1.selectbox("Exam", EXAM_OPTIONS, index=EXAM_OPTIONS.index(pf_exam) if pf_exam in EXAM_OPTIONS else 0)
                subject = e2.text_input("Subject", value=pf_sub)
                month = e3.text_input("Month/Year", value=pf_my)
                
                p1, p2, p3 = st.columns(3)
                pur_val = pf_pur if pf_pur in PURPOSE_OPTIONS else "Other"
                purpose_sel = p1.selectbox("Purpose", PURPOSE_OPTIONS, index=PURPOSE_OPTIONS.index(pur_val))
                purpose = p1.text_input("Specify", value=pf_pur) if purpose_sel == "Other" else purpose_sel
                receipt = p2.text_input("Receipt No", value=pf_rec)
                r_date = p3.date_input("Receipt Date", value=pf_rec_d)

                st.subheader("Travel Expenses")
                st.markdown("**Railway**")
                r1, r2, r3, r4 = st.columns(4)
                rf = r1.text_input("From", value=pf_rf, key="rf")
                rt = r2.text_input("To", value=pf_rt, key="rt")
                rtk = r3.text_input("Ticket", value=pf_rtk)
                ra = r4.text_input("Amt", value=pf_ra, key="ra")
                
                st.markdown("**Bus**")
                b1, b2, b3 = st.columns([2, 2, 1])
                bf = b1.text_input("From", value=pf_bf, key="bf")
                bt = b2.text_input("To", value=pf_bt, key="bt")
                ba = b3.text_input("Amt", value=pf_ba, key="ba")
                
                st.markdown("**Car**")
                k1, k2, k3, k4, k5 = st.columns(5)
                cf = k1.text_input("From", value=pf_cf, key="cf")
                ct = k2.text_input("To", value=pf_ct, key="ct")
                cn = k3.text_input("Veh No", value=pf_cn)
                ck = k4.text_input("KM", value=pf_ck)
                ca = k5.text_input("Amt", value=pf_ca, key="ca")

                st.subheader("Final Calculation")
                f1, f2, f3 = st.columns(3)
                lump_str = f1.text_input("Lumpsum Allowance", value=pf_lump)
                da_str = f2.text_input("DA Amount", value=pf_da)
                
                total = safe_float(ra) + safe_float(ba) + safe_float(ca) + safe_float(lump_str) + safe_float(da_str)
                f3.metric("GRAND TOTAL", f"₹ {total:,.2f}")

                c_submit, c_req = st.columns(2)
                
                form_data = {
                    'aadhaar': st.session_state.current_aadhaar, 'name': name, 'mobile': mobile,
                    'addr_res': addr_res, 'addr_prof': addr_prof, 'basic': basic_pay_str,
                    'bank_name': bank_name, 'ifsc': ifsc, 'acc_no': acc_no,
                    'exam': exam, 'subject': subject, 'month': month, 'purpose': purpose,
                    'receipt_no': receipt, 'receipt_date': r_date,
                    'rly_f': rf, 'rly_t': rt, 'rly_tkt': rtk, 'rly_a': safe_float(ra),
                    'bus_f': bf, 'bus_t': bt, 'bus_a': safe_float(ba),
                    'car_f': cf, 'car_t': ct, 'car_no': cn, 'car_k': safe_float(ck), 'car_a': safe_float(ca),
                    'lumpsum': safe_float(lump_str), 'da': safe_float(da_str), 'total': total
                }

                if c_submit.button("🚀 CLONE / SUBMIT NEW BILL", type="primary", use_container_width=True):
                    if mobile and name:
                        bid = submit_bill(form_data, visits, st.session_state.user)
                        if bid:
                            log_activity(st.session_state.user, f"Created Bill #{bid}")
                            st.balloons()
                            st.success("Bill Created Successfully!")
                            # Reset Logic
                            st.session_state.aadhaar_verified = False
                            st.session_state.edit_bill_id = None
                            time.sleep(1) # Pause to let user see success message
                            st.rerun()
                    else:
                        st.error("Name & Mobile Required")

                if st.session_state.edit_bill_id:
                    if c_req.button("📨 REQUEST UPDATE (Same Bill ID)", use_container_width=True):
                        full_payload = json.dumps({'main': form_data, 'visits': visits}, default=str)
                        request_update_existing(st.session_state.edit_bill_id, st.session_state.user, "User Correction", full_payload)
                        log_activity(st.session_state.user, f"Requested update for Bill #{st.session_state.edit_bill_id}")
                        st.success("Update Request Sent to Admin!")
                        st.session_state.edit_bill_id = None
                        st.rerun()

    # --- TAB 2: HISTORY (UPGRADED) ---
    with tab2:
        st.subheader("My History & Reports")
        
        # FILTERS
        c1, c2 = st.columns(2)
        d_start = c1.date_input("Filter Submission From", value=date.today().replace(day=1))
        d_end = c2.date_input("Filter Submission To", value=date.today())
        
        c3, c4 = st.columns(2)
        v_start = c3.date_input("Visit Date From", value=None)
        v_end = c4.date_input("Visit Date To", value=None)
        
        # DOWNLOAD FULL REPORT
        if st.button("📥 Download Filtered Report (Excel)"):
            # Use get_report_data which returns FULL columns
            report_df = get_report_data(username=st.session_state.user)
            if not report_df.empty:
                try:
                    report_df['DateObj'] = pd.to_datetime(report_df['Submission Date']).dt.date
                    final_export = report_df[(report_df['DateObj'] >= d_start) & (report_df['DateObj'] <= d_end)].drop(columns=['DateObj'])
                    
                    # Sort Ascending (Oldest First -> Latest Last)
                    final_export.sort_values(by='Submission Date', ascending=True, inplace=True)
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        final_export.to_excel(writer, index=False)
                    st.download_button("Click to Download", output.getvalue(), f"My_Report_{d_start}_{d_end}.xlsx")
                except:
                    st.error("Error processing dates.")
            else:
                st.warning("No records found.")
        
        st.divider()
        
        # TABLE VIEW
        # Fetch all bills for this user
        user_bills = get_bills_by_user(st.session_state.user)
        
        if not user_bills.empty:
            # 1. Filter by Submission Date
            user_bills['DateObj'] = pd.to_datetime(user_bills['Date']).dt.date
            filtered_df = user_bills[(user_bills['DateObj'] >= d_start) & (user_bills['DateObj'] <= d_end)]
            
            # 2. Filter by Visit Date
            if v_start and v_end and st.session_state.current_aadhaar:
                visit_filtered = get_bills_by_visit_date(st.session_state.current_aadhaar, v_start, v_end)
                filtered_df = filtered_df[filtered_df['id'].isin(visit_filtered['id'])]
            
            filtered_df = filtered_df.drop(columns=['DateObj'])
            
            # PAGINATION
            page_size = 50
            total_rows = len(filtered_df)
            if total_rows > 0:
                total_pages = max(1, (total_rows - 1) // page_size + 1)
                page = st.selectbox("Page", range(1, total_pages + 1))
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, total_rows)
                
                st.dataframe(filtered_df.iloc[start_idx:end_idx], use_container_width=True)
                st.caption(f"Showing {start_idx+1}-{end_idx} of {total_rows} records")
                
                # Edit Action from Table
                st.write("---")
                col_sel, col_act = st.columns([3, 1])
                bill_to_edit_id = col_sel.selectbox("Select Bill ID to Clone/Edit", filtered_df['id'].tolist())
                if col_act.button("✏️ Edit Selected Bill"):
                    st.session_state.edit_bill_id = bill_to_edit_id
                    st.session_state.aadhaar_verified = True # Force into form view
                    st.session_state.current_aadhaar = filtered_df[filtered_df['id'] == bill_to_edit_id]['Aadhaar'].values[0] # Set aadhaar from bill
                    st.rerun()
            else:
                st.info("No records match your filters.")
        else:
            st.info("No history found.")

    # --- TAB 3: TRACK REQUESTS ---
    with tab3:
        st.subheader("🕒 My Edit Requests")
        req_status_df = get_user_edit_status(st.session_state.user)
        if not req_status_df.empty:
            st.dataframe(req_status_df, use_container_width=True)
        else:
            st.info("You have no pending or past edit requests.")

# ==========================================
# 7. MAIN RUN
# ==========================================
def main():
    # Force initialize session state for aadhaar_exists_msg BEFORE accessing it anywhere
    if "aadhaar_exists_msg" not in st.session_state:
        st.session_state.aadhaar_exists_msg = False

    init_db()
    apply_dynamic_styles()
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.edit_bill_id = None
        st.session_state.aadhaar_verified = False

    if not st.session_state.logged_in:
        login_container()
    else:
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
            st.markdown(f"### {st.session_state.user}")
            st.info(f"Role: {st.session_state.role}")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.aadhaar_verified = False
                st.rerun()
        
        if st.session_state.role == "Admin":
            admin_dashboard()
        else:
            user_portal()

if __name__ == "__main__":
    main()