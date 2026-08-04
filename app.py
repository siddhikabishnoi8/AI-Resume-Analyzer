import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
from werkzeug.utils import secure_filename
from config import Config
from database import db, init_db, User, Analysis
from parser import extract_text
from analyzer import run_ats_analysis
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB
init_db(app)

# Helper to require login for APIs
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Context processor to inject user into templates
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

# ----------------- PAGE ROUTES -----------------

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard_page'))
    return render_template('landing.html')

@app.route('/login')
def login_page():
    if session.get('user_id'):
        return redirect(url_for('dashboard_page'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if session.get('user_id'):
        return redirect(url_for('dashboard_page'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard_page():
    if not session.get('user_id'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

# ----------------- AUTH APIs -----------------

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
        
    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email is already registered.'}), 400
        
    try:
        user = User(full_name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        session['user_id'] = user.id
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 400
        
    session['user_id'] = user.id
    session.permanent = True
    return jsonify({'success': True, 'message': 'Logged in successfully!', 'user': user.to_dict()})

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/api/auth/profile', methods=['GET'])
@login_required
def api_profile():
    user = g.user
    resume_count = Analysis.query.filter_by(user_id=user.id).count()
    total_score_sum = db.session.query(db.func.sum(Analysis.ats_score)).filter(Analysis.user_id == user.id).scalar() or 0
    average_score = round(total_score_sum / resume_count) if resume_count > 0 else 0
    
    return jsonify({
        'success': True,
        'profile': {
            'full_name': user.full_name,
            'email': user.email,
            'resume_count': resume_count,
            'analysis_count': resume_count,
            'average_score': average_score,
            'created_at': user.created_at.strftime('%B %Y')
        }
    })

@app.route('/api/auth/profile/password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_new = data.get('confirm_new_password', '')
    
    if not current_password or not new_password or not confirm_new:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    if new_password != confirm_new:
        return jsonify({'success': False, 'message': 'New passwords do not match.'}), 400
        
    user = g.user
    if not user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Incorrect current password.'}), 400
        
    try:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to update password: {str(e)}'}), 500

# ----------------- RESUME ANALYSIS APIs -----------------

@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    # Check if files uploaded
    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': 'Resume file is required.'}), 400
        
    file = request.files['resume']
    job_desc_text = request.form.get('job_description', '').strip()
    job_title = request.form.get('job_title', '').strip() or "General Matching"
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file.'}), 400
        
    # File validation
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.pdf', '.docx']:
        return jsonify({'success': False, 'message': 'Unsupported file format. Please upload PDF or DOCX.'}), 400
        
    if not job_desc_text:
        return jsonify({'success': False, 'message': 'Job description text is required.'}), 400
        
    try:
        # Save file to uploads folder temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{g.user.id}_{filename}")
        file.save(filepath)
        
        # Parse text from file
        resume_text = extract_text(filepath)
        if not resume_text or len(resume_text.strip()) < 50:
            os.remove(filepath)
            return jsonify({'success': False, 'message': 'Could not extract sufficient text from the resume file. Ensure the file is not scanned/image-only.'}), 400
            
        # Perform ATS analysis
        analysis_data = run_ats_analysis(resume_text, job_desc_text, filename)
        
        # Save to database
        analysis = Analysis(
            user_id=g.user.id,
            resume_name=filename,
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_desc_text,
            ats_score=analysis_data['ats_score'],
            resume_match_score=analysis_data['resume_match_score'],
            skills_score=analysis_data['skills_score'],
            keywords_score=analysis_data['keywords_score'],
            experience_score=analysis_data['experience_score'],
            education_score=analysis_data['education_score'],
            formatting_score=analysis_data['formatting_score']
        )
        # Store serialized JSON fields
        analysis.extracted_data = analysis_data['extracted_data']
        analysis.analysis_results = analysis_data['analysis_results']
        
        db.session.add(analysis)
        db.session.commit()
        
        # Delete temporary file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Resume analyzed successfully!',
            'analysis': analysis.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        # Clean file in case of error
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        return jsonify({'success': False, 'message': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    search_query = request.args.get('search', '').strip()
    
    try:
        query = Analysis.query.filter_by(user_id=g.user.id)
        if search_query:
            query = query.filter(
                (Analysis.resume_name.ilike(f"%{search_query}%")) | 
                (Analysis.job_title.ilike(f"%{search_query}%"))
            )
            
        # Newest first
        results = query.order_by(Analysis.created_at.desc()).all()
        return jsonify({
            'success': True,
            'history': [item.to_dict() for item in results]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to retrieve history: {str(e)}'}), 500

@app.route('/api/history/<int:analysis_id>', methods=['DELETE'])
@login_required
def api_delete_history(analysis_id):
    try:
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=g.user.id).first()
        if not analysis:
            return jsonify({'success': False, 'message': 'Analysis record not found.'}), 404
            
        db.session.delete(analysis)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Analysis record deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to delete record: {str(e)}'}), 500

@app.route('/api/history/<int:analysis_id>/report', methods=['GET'])
@login_required
def api_report_page(analysis_id):
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=g.user.id).first()
    if not analysis:
        return "Report not found", 404
        
    # Render static report template specifically styled for printing
    return render_template(
        'report.html',
        analysis=analysis.to_dict(),
        extracted=analysis.extracted_data,
        results=analysis.analysis_results,
        date_str=analysis.created_at.strftime('%Y-%m-%d %H:%M')
    )

if __name__ == '__main__':
    # Ensure port matches requirements, run locally
    app.run(host='0.0.0.0', port=5001, debug=True)
