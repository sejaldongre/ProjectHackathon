import streamlit as st
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# ---------- FILE PATHS ----------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

PROBLEM_FILE = os.path.join(DATA_DIR, "problems.json")


# ---------- JSON Helpers ----------
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------- Password ----------
AUTHOR_PASSWORD = "author@123"

# ---------- Home ----------
def home(user_is_author=False):
    st.title("🌟 HackaAgent - Firebase Hackathon System")

    # # View Problems
    # st.header("📌 Problem Statements")
    # problems = db.collection("problems").stream()
    # for i, prob in enumerate(problems):
    #     p = prob.to_dict()
    #     st.markdown(f"**{i+1}. {p['title']}**")
    #     st.write(p["description"])

# View Problem Statements
    st.header("📌 Problem Statements")
    problems = load_json(PROBLEM_FILE)
    if not problems:
        st.info("No problems added yet.")
    else:
        for i, p in enumerate(problems):
            st.markdown(f"{i+1}. {p['title']}")
            st.write(p["description"])

    # Author-Only: Add Problem Statement
    if user_is_author:
        st.header("➕ Add Problem Statement")
        with st.form("add_problem"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            if st.form_submit_button("Add Problem"):
                problems.append({"title": title, "description": desc})
                save_json(PROBLEM_FILE, problems)
                st.success("Problem added!")

    # Author only: Add problem
    if user_is_author:
        st.header("➕ Add Problem Statement")
        with st.form("add_problem"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            if st.form_submit_button("Add"):
                db.collection("problems").add({"title": title, "description": desc})
                st.success("✅ Problem added!")

    # Register team
    st.header("🧑‍💻 Register Team")
    with st.form("register_team"):
        team_name = st.text_input("Team Name")
        members = st.text_area("Members")
        email = st.text_input("Email")
        if st.form_submit_button("Register"):
            db.collection("teams").document(team_name).set({
                "team_name": team_name,
                "members": members,
                "email": email
            })
            st.success("✅ Team registered!")

    # Submit project
    st.header("🔗 Submit Project Link")
    with st.form("submit_project"):
        team = st.text_input("Registered Team Name")
        link = st.text_input("GitHub/Drive Project Link")
        if st.form_submit_button("Submit"):
            db.collection("projects").document(team).set({
                "team": team,
                "project_link": link
            })
            st.success("✅ Link submitted!")

# ---------- Judge Panel ----------
def judge_panel():
    st.title("👩‍⚖️ Judge Panel (Author Only)")

    password = st.text_input("Enter Author Password", type="password")
    if password != AUTHOR_PASSWORD:
        st.warning("🔐 Access Denied")
        return

    st.success("✅ Access Granted")

    teams = db.collection("teams").stream()
    projects = {p.id: p.to_dict()["project_link"] for p in db.collection("projects").stream()}

    for t in teams:
        team = t.to_dict()
        st.subheader(team["team_name"])
        st.write("📧", team["email"])
        st.write("👥", team["members"])
        st.write("🔗", projects.get(team["team_name"], "Not Submitted"))

        with st.form(f"score_{team['team_name']}"):
            usefulness = st.slider("Usefulness", 1, 10)
            creativity = st.slider("Creativity", 1, 10)
            teamwork = st.slider("Teamwork", 1, 10)
            tech_stack = st.slider("Tech Stack", 1, 10)
            clarity = st.slider("Clarity", 1, 10)
            if st.form_submit_button("Submit Score"):
                db.collection("scores").add({
                    "team": team["team_name"],
                    "scores": {
                        "usefulness": usefulness,
                        "creativity": creativity,
                        "teamwork": teamwork,
                        "tech_stack": tech_stack,
                        "clarity": clarity
                    }
                })
                st.success("✅ Score submitted!")

# ---------- Main ----------
page = st.sidebar.radio("Navigate", ["🏠 Student/Author View", "👩‍⚖ Judge Panel"])

if page == "🏠 Student/Author View":
    user_type = st.selectbox("Who are you?", ["Student", "Author"])
    if user_type == "Author":
        pwd = st.text_input("Enter Author Password", type="password")
        home(user_is_author=(pwd == AUTHOR_PASSWORD))
    else:
        home()
elif page == "👩‍⚖ Judge Panel":
    judge_panel()
