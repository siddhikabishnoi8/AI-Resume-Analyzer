import re
import ssl
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from parser import parse_contact_info, parse_education, parse_experience

# Downloader helper
def setup_nltk_and_spacy():
    # Workaround for SSL certificate verification errors in NLTK downloads on macOS
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
        
    # Download NLTK data
    for pkg in ['punkt', 'stopwords', 'wordnet', 'omw-1.4']:
        try:
            nltk.download(pkg, quiet=True)
        except Exception as e:
            print(f"Error downloading NLTK package {pkg}: {e}")
            
    # Load or download spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model 'en_core_web_sm'...")
        from spacy.cli import download
        try:
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Failed to download spaCy model: {e}. Running parser fallback mode.")
            nlp = None
    return nlp

# Initialize NLP tools
nlp = setup_nltk_and_spacy()

# Comprehensive catalog of tech skills grouped by category
SKILL_CATALOG = {
    'Languages': [
        'python', 'javascript', 'typescript', 'java', 'c\\+\\+', 'c#', 'golang', 'go', 'ruby', 
        'php', 'swift', 'kotlin', 'rust', 'sql', 'html5', 'html', 'css3', 'css', 'sass', 'less', 
        'shell', 'bash', 'r language', 'julia', 'scala', 'perl', 'objective-c', 'dart'
    ],
    'Backend': [
        'flask', 'django', 'fastapi', 'express', 'node\\.js', 'spring boot', 'spring', 'rails', 
        'laravel', 'nestjs', 'asp\\.net', 'graphql', 'rest api', 'soap', 'microservices', 'gRPC'
    ],
    'Frontend': [
        'react', 'react\\.js', 'angular', 'angularjs', 'vue', 'vue\\.js', 'svelte', 'next\\.js', 
        'nuxt\\.js', 'tailwind css', 'tailwind', 'bootstrap', 'material ui', 'webpack', 'vite', 
        'jquery', 'redux', 'mobx'
    ],
    'Database': [
        'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis', 'oracle', 'cassandradb', 
        'cassandra', 'dynamodb', 'mariadb', 'elasticsearch', 'neo4j', 'firebase', 'firestore'
    ],
    'Cloud & DevOps': [
        'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 
        'k8s', 'jenkins', 'git', 'github', 'gitlab', 'terraform', 'ansible', 'chef', 'puppet', 
        'ci/cd', 'circleci', 'circle ci', 'travis ci', 'prometheus', 'grafana', 'nginx', 'apache'
    ],
    'AI & Data Science': [
        'scikit-learn', 'sklearn', 'pandas', 'numpy', 'spacy', 'nltk', 'tensorflow', 'pytorch', 
        'keras', 'scipy', 'opencv', 'nlp', 'natural language processing', 'deep learning', 
        'machine learning', 'computer vision', 'data analysis', 'data science', 'tableau', 
        'power bi', 'powerbi', 'matplotlib', 'seaborn', 'spark', 'hadoop', 'apache spark'
    ],
    'Methodologies & Tools': [
        'agile', 'scrum', 'jira', 'confluence', 'trello', 'unit testing', 'pytest', 'unittest', 
        'mocha', 'jest', 'cypress', 'selenium', 'postman', 'docker compose', 'restful api'
    ]
}

# Flatten list for general skill searches
ALL_SKILLS = []
for cat, skills in SKILL_CATALOG.items():
    ALL_SKILLS.extend(skills)

# Mapping to standard names
SKILL_MAP = {
    'js': 'JavaScript',
    'javascript': 'JavaScript',
    'ts': 'TypeScript',
    'typescript': 'TypeScript',
    'py': 'Python',
    'python': 'Python',
    'c++': 'C++',
    'c\\+\\+': 'C++',
    'c#': 'C#',
    'html': 'HTML',
    'html5': 'HTML5',
    'css': 'CSS',
    'css3': 'CSS3',
    'aws': 'AWS (Amazon Web Services)',
    'amazon web services': 'AWS (Amazon Web Services)',
    'gcp': 'GCP (Google Cloud)',
    'google cloud': 'GCP (Google Cloud)',
    'k8s': 'Kubernetes',
    'kubernetes': 'Kubernetes',
    'postgres': 'PostgreSQL',
    'postgresql': 'PostgreSQL',
    'sklearn': 'Scikit-learn',
    'scikit-learn': 'Scikit-learn',
    'nltk': 'NLTK',
    'spacy': 'spaCy'
}

def get_standard_skill_name(raw_skill):
    raw_lower = raw_skill.lower()
    return SKILL_MAP.get(raw_lower, raw_skill.title())

def clean_and_tokenize(text):
    """Clean and lemmatize text using spaCy if available, fallback to NLTK."""
    if not text:
        return ""
    
    text = text.lower()
    # Normalize whitespaces and clean some special characters
    text = re.sub(r'\s+', ' ', text)
    
    if nlp:
        try:
            doc = nlp(text)
            tokens = []
            for token in doc:
                if not token.is_stop and not token.is_punct and token.text.strip():
                    tokens.append(token.lemma_)
            return " ".join(tokens)
        except Exception as e:
            print(f"spaCy lemmatization error: {e}")
            
    # Fallback to NLTK
    try:
        tokens = nltk.word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        cleaned_tokens = [
            lemmatizer.lemmatize(token) 
            for token in tokens 
            if token.isalnum() and token not in stop_words
        ]
        return " ".join(cleaned_tokens)
    except Exception as e:
        print(f"NLTK lemmatization error: {e}")
        # Standard regex cleanup fallback
        words = re.findall(r'\b\w+\b', text)
        return " ".join(words)

def calculate_similarity(resume_cleaned, job_cleaned):
    """Calculate TF-IDF cosine similarity without scikit-learn."""
    if not resume_cleaned or not job_cleaned:
        return 0

    try:
        from collections import Counter
        import math

        resume_words = resume_cleaned.split()
        job_words = job_cleaned.split()

        documents = [resume_words, job_words]

        # Create vocabulary
        vocabulary = set(resume_words + job_words)

        if not vocabulary:
            return 0

        # Calculate TF-IDF vectors
        vectors = []

        for document in documents:
            word_count = Counter(document)
            total_words = len(document)

            vector = []

            for word in vocabulary:
                # Term Frequency
                tf = word_count[word] / total_words if total_words else 0

                # Inverse Document Frequency
                document_frequency = sum(
                    1 for doc in documents if word in doc
                )

                idf = math.log(
                    len(documents) / document_frequency
                ) + 1

                vector.append(tf * idf)

            vectors.append(vector)

        # Cosine similarity
        dot_product = sum(
            a * b for a, b in zip(vectors[0], vectors[1])
        )

        magnitude_resume = math.sqrt(
            sum(x * x for x in vectors[0])
        )

        magnitude_job = math.sqrt(
            sum(x * x for x in vectors[1])
        )

        if magnitude_resume == 0 or magnitude_job == 0:
            return 0

        similarity = dot_product / (
            magnitude_resume * magnitude_job
        )

        return int(similarity * 100)

    except Exception as e:
        print(f"Similarity calculation failed: {e}")
        return 0

def extract_skills_from_text(text):
    """Find matches for skills from the predefined catalog."""
    found_skills = set()
    text_lower = text.lower()
    
    for skill_pattern in ALL_SKILLS:
        # Match using word boundaries. Add special handling for characters like +, #, .
        pattern = r'\b' + skill_pattern + r'\b'
        if '++' in skill_pattern:
            pattern = r'\b' + skill_pattern.replace('++', r'\+\+') + r'(?!\+)'
        elif '#' in skill_pattern:
            pattern = r'\b' + skill_pattern.replace('#', r'\#')
        elif '.js' in skill_pattern:
            pattern = r'\b' + skill_pattern.replace('.js', r'\.js')
            
        if re.search(pattern, text_lower):
            found_skills.add(get_standard_skill_name(skill_pattern))
            
    return found_skills

def analyze_keywords(resume_text, job_desc_text):
    """Identify top keywords, missing keywords, and repeated keywords (potential stuffing)."""
    # Extract words
    resume_words = re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower())
    job_words = re.findall(r'\b[a-zA-Z]{3,}\b', job_desc_text.lower())
    
    stop_words = set(stopwords.words('english')) if 'stopwords' in nltk.corpus.__dict__ else set()
    
    # Filter stopwords and common generic resume words
    resume_filtered = [w for w in resume_words if w not in stop_words and len(w) > 2]
    job_filtered = [w for w in job_words if w not in stop_words and len(w) > 2]
    
    # Count frequencies
    from collections import Counter
    job_counts = Counter(job_filtered)
    resume_counts = Counter(resume_filtered)
    
    # Get top 20 keywords from Job Description
    top_job_keywords = [word for word, count in job_counts.most_common(15)]
    
    matched_keywords = []
    missing_keywords = []
    
    for word in top_job_keywords:
        if word in resume_counts:
            matched_keywords.append(word)
        else:
            missing_keywords.append(word)
            
    # Find repeated keywords (more than 8 occurrences in the resume, indicating keyword stuffing)
    repeated_keywords = []
    for word, count in resume_counts.items():
        if count >= 8 and word not in stop_words and word not in ['experience', 'project', 'system', 'management', 'work', 'development', 'team', 'using', 'skills']:
            repeated_keywords.append({
                'keyword': word,
                'count': count
            })
            
    return {
        'top_keywords': top_job_keywords[:10],
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'repeated_keywords': repeated_keywords[:5]
    }

def analyze_formatting(text, contact_info):
    """Check font sections, email, phone, links, and length rules."""
    formatting_issues = []
    score = 100
    
    # Check 1: Contact details
    if not contact_info.get('email'):
        formatting_issues.append("Missing Email address in contact information.")
        score -= 15
    if not contact_info.get('phone'):
        formatting_issues.append("Missing Phone number in contact information.")
        score -= 15
        
    # Check 2: Professional Profiles
    if not contact_info.get('linkedin') and not contact_info.get('github'):
        formatting_issues.append("Consider adding links to professional profiles (GitHub, LinkedIn, or Portfolio).")
        score -= 10
        
    # Check 3: Word Count/Length
    word_count = len(text.split())
    if word_count < 200:
        formatting_issues.append(f"Resume is very short ({word_count} words). Add details about your projects and work history.")
        score -= 20
    elif word_count > 1500:
        formatting_issues.append(f"Resume is too long ({word_count} words). Aim to keep it under 2 pages (400-1000 words).")
        score -= 15
        
    # Check 4: Section Headings
    headings_found = []
    for heading in ['experience', 'work', 'education', 'skills', 'projects', 'certifications']:
        if re.search(r'\b' + heading + r'\b', text.lower()):
            headings_found.append(heading)
            
    if 'experience' not in headings_found and 'work' not in headings_found:
        formatting_issues.append("Could not identify a clear 'Work Experience' or 'Employment History' section header.")
        score -= 15
    if 'education' not in headings_found:
        formatting_issues.append("Could not identify an 'Education' section header.")
        score -= 10
    if 'skills' not in headings_found:
        formatting_issues.append("Could not identify a dedicated 'Skills' section header.")
        score -= 10
        
    # Cap score
    score = max(10, score)
    
    return {
        'score': score,
        'issues': formatting_issues,
        'word_count': word_count,
        'has_email': bool(contact_info.get('email')),
        'has_phone': bool(contact_info.get('phone')),
        'has_links': bool(contact_info.get('linkedin') or contact_info.get('github')),
        'headings_found': headings_found
    }

def analyze_experience_alignment(candidate_years, job_desc_text):
    """Compare candidate's experience to job description specifications."""
    # Find required experience years from job description
    # Match: "3+ years", "5 years", "at least 4 years"
    required_years = 0
    exp_pattern = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|work)', job_desc_text, re.IGNORECASE)
    if exp_pattern:
        required_years = int(exp_pattern.group(1))
        
    match_status = "Good Match"
    score = 100
    suggestions = []
    
    if required_years > 0:
        if candidate_years >= required_years:
            score = 100
            match_status = "Exceeds or Matches Requirements"
        else:
            score = int((candidate_years / required_years) * 100)
            match_status = "Below Requirements"
            suggestions.append(f"The job requires {required_years} years of experience, but we parsed {candidate_years} years. Highlight any freelance or relevant project work to bridge this gap.")
    else:
        # Default if not specified in Job Description
        required_years = 2 # default standard
        if candidate_years >= required_years:
            score = 100
        else:
            score = 80
            
    return {
        'candidate_years': candidate_years,
        'required_years': required_years,
        'score': score,
        'match_status': match_status,
        'suggestions': suggestions
    }

def analyze_education_alignment(candidate_degrees, job_desc_text):
    """Determine education fit between candidate degree and job description requirements."""
    # Hierarchy
    hierarchy = {
        'High School Diploma': 1,
        'Associate\'s Degree': 2,
        'Bachelor\'s Degree': 3,
        'Master\'s Degree': 4,
        'PhD': 5
    }
    
    # Get highest candidate degree
    highest_candidate_value = 1
    highest_candidate_degree = "High School Diploma"
    for deg in candidate_degrees:
        val = hierarchy.get(deg, 1)
        if val > highest_candidate_value:
            highest_candidate_value = val
            highest_candidate_degree = deg
            
    # Search for education requirements in Job Description
    req_degree = "Bachelor's Degree" # Default benchmark
    req_val = 3
    
    if re.search(r'\bphd\b|\bph\.d\b|\bdoctorate\b', job_desc_text, re.IGNORECASE):
        req_degree = "PhD"
        req_val = 5
    elif re.search(r'\bmaster\b|\bm\.s\b|\bmsc\b|\bmba\b', job_desc_text, re.IGNORECASE):
        req_degree = "Master's Degree"
        req_val = 4
    elif re.search(r'\bbachelor\b|\bb\.s\b|\bb\.tech\b|\bb\.e\b', job_desc_text, re.IGNORECASE):
        req_degree = "Bachelor's Degree"
        req_val = 3
    elif re.search(r'\bassociate\b', job_desc_text, re.IGNORECASE):
        req_degree = "Associate's Degree"
        req_val = 2
        
    score = 100
    match_status = "Matched"
    if highest_candidate_value < req_val:
        score = 70
        match_status = "Degree Level Below Requested"
        if highest_candidate_value == 1:
            score = 50
    elif highest_candidate_value > req_val:
        score = 100
        match_status = "Exceeds Requirements"
        
    return {
        'candidate_degree': highest_candidate_degree,
        'required_degree': req_degree,
        'score': score,
        'match_status': match_status
    }

def generate_ats_suggestions(skills_missing, formatting_info, exp_info, contact_info):
    """Generate professional, actionable ATS suggestions card lists."""
    suggestions = []
    
    # Achievement suggestion (quantify)
    suggestions.append({
        'title': "Add measurable achievements",
        'description': "Use quantifiable metrics and numbers (e.g. 'Increased traffic by 25%', 'Saved $10K annually') to prove impact. We noticed few metrics in your descriptions.",
        'category': "content"
    })
    
    # Technical keywords suggestion
    if len(skills_missing) > 0:
        missing_sample = ", ".join(list(skills_missing)[:3])
        suggestions.append({
            'title': "Include missing technical keywords",
            'description': f"Integrate matching keywords like {missing_sample} into your experience bullet points to satisfy search term filters.",
            'category': "skills"
        })
        
    # Social links suggestions
    if not contact_info.get('github'):
        suggestions.append({
            'title': "Add GitHub profile",
            'description': "For technical roles, adding a link to a clean GitHub profile with your code repositories boosts credibility.",
            'category': "formatting"
        })
    if not contact_info.get('linkedin'):
        suggestions.append({
            'title': "Add LinkedIn profile link",
            'description': "A professional LinkedIn profile link is expected on modern resumes. Ensure it is updated and matching.",
            'category': "formatting"
        })
        
    # Action verbs
    suggestions.append({
        'title': "Use stronger action verbs",
        'description': "Begin each experience bullet point with strong action verbs (e.g., 'Spearheaded', 'Optimized', 'Architected') rather than passive phrases.",
        'category': "content"
    })
    
    # Format layout issues
    for issue in formatting_info['issues'][:2]:
        suggestions.append({
            'title': "Correct layout formatting issue",
            'description': issue,
            'category': "formatting"
        })
        
    return suggestions

def run_ats_analysis(resume_text, job_desc_text, filename="Resume"):
    """Core analysis orchestrator. Combines NLP, cosine similarities and parsing outputs."""
    # 1. Parsing basics
    contact_info = parse_contact_info(resume_text, nlp)
    candidate_degrees = parse_education(resume_text)
    candidate_years = parse_experience(resume_text)
    
    # 2. Text cleaning
    cleaned_resume = clean_and_tokenize(resume_text)
    cleaned_job = clean_and_tokenize(job_desc_text)
    
    # 3. Overall Content Similarity
    resume_match_score = calculate_similarity(cleaned_resume, cleaned_job)
    
    # 4. Skill Extraction & Scoring
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_desc_text)
    
    matched_skills = list(resume_skills.intersection(job_skills))
    missing_skills = list(job_skills.difference(resume_skills))
    
    # Recommended skills (related to what matched)
    recommended_skills = []
    if 'Python' in matched_skills or 'Flask' in matched_skills:
        if 'Django' not in resume_skills: recommended_skills.append('Django')
        if 'FastAPI' not in resume_skills: recommended_skills.append('FastAPI')
    if 'Docker' in matched_skills:
        if 'Kubernetes' not in resume_skills: recommended_skills.append('Kubernetes')
    if 'React' in matched_skills:
        if 'TypeScript' not in resume_skills: recommended_skills.append('TypeScript')
        if 'Redux' not in resume_skills: recommended_skills.append('Redux')
    if 'MySQL' in matched_skills or 'PostgreSQL' in matched_skills:
        if 'Redis' not in resume_skills: recommended_skills.append('Redis')
        
    recommended_skills = list(set(recommended_skills))[:3]
    
    # If no skills in JD, we measure how many of the candidate skills overlap generally
    if len(job_skills) > 0:
        skills_score = int((len(matched_skills) / len(job_skills)) * 100)
    else:
        # Default score based on content similarity
        skills_score = max(50, resume_match_score)
        
    # 5. Keyword analysis
    keyword_info = analyze_keywords(resume_text, job_desc_text)
    # Keyword match score
    job_top_keywords = keyword_info['top_keywords']
    matched_kw_count = len(keyword_info['matched_keywords'])
    keywords_score = int((matched_kw_count / len(job_top_keywords)) * 100) if job_top_keywords else 80
    
    # 6. Experience & Education scoring
    exp_info = analyze_experience_alignment(candidate_years, job_desc_text)
    edu_info = analyze_education_alignment(candidate_degrees, job_desc_text)
    
    # 7. Formatting analysis
    fmt_info = analyze_formatting(resume_text, contact_info)
    
    # 8. ATS Score computation
    # Skill Match = 40%
    # Keyword Match = 20%
    # Experience = 20%
    # Education = 10%
    # Resume Formatting = 10%
    final_score = int(
        skills_score * 0.40 + 
        keywords_score * 0.20 + 
        exp_info['score'] * 0.20 + 
        edu_info['score'] * 0.10 + 
        fmt_info['score'] * 0.10
    )
    final_score = min(100, max(10, final_score))
    
    # 9. Recommendations list
    suggestions = generate_ats_suggestions(missing_skills, fmt_info, exp_info, contact_info)
    
    # Construct details JSON
    extracted_data = {
        'name': contact_info['name'],
        'email': contact_info['email'] or "Not Found",
        'phone': contact_info['phone'] or "Not Found",
        'github': contact_info['github'] or "",
        'linkedin': contact_info['linkedin'] or "",
        'education': candidate_degrees,
        'experience_years': candidate_years,
        'skills': list(resume_skills)
    }
    
    analysis_results = {
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'recommended_skills': recommended_skills,
        'top_keywords': keyword_info['top_keywords'],
        'matched_keywords': keyword_info['matched_keywords'],
        'missing_keywords': keyword_info['missing_keywords'],
        'repeated_keywords': keyword_info['repeated_keywords'],
        'formatting_issues': fmt_info['issues'],
        'formatting_details': {
            'word_count': fmt_info['word_count'],
            'has_email': fmt_info['has_email'],
            'has_phone': fmt_info['has_phone'],
            'has_links': fmt_info['has_links'],
            'headings_found': fmt_info['headings_found']
        },
        'experience_details': {
            'candidate_years': exp_info['candidate_years'],
            'required_years': exp_info['required_years'],
            'match_status': exp_info['match_status']
        },
        'education_details': {
            'candidate_degree': edu_info['candidate_degree'],
            'required_degree': edu_info['required_degree'],
            'match_status': edu_info['match_status']
        },
        'suggestions': suggestions
    }
    
    return {
        'ats_score': final_score,
        'resume_match_score': resume_match_score,
        'skills_score': skills_score,
        'keywords_score': keywords_score,
        'experience_score': exp_info['score'],
        'education_score': edu_info['score'],
        'formatting_score': fmt_info['score'],
        'extracted_data': extracted_data,
        'analysis_results': analysis_results
    }
