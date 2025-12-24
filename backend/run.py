from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)


## Step 4: Update requirements.txt

# **In `backend/requirements.txt`:**
# ```
# Flask==3.0.0
# Flask-SQLAlchemy==3.1.1
# Flask-CORS==4.0.0
# Werkzeug==3.0.1