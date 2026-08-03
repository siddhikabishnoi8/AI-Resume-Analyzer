# Verification script for AI Resume Analyzer NLP pipeline
import sys

def main():
    print("Testing NLP initialization...")
    try:
        from analyzer import run_ats_analysis, setup_nltk_and_spacy
        from parser import parse_contact_info, parse_education, parse_experience
        print("Success: Modules imported successfully!")
    except Exception as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)
        
    print("\nPreparing mock data...")
    mock_resume = """
    Johnathan Doe
    john.doe@email.com | +1 (555) 019-2834 | San Francisco, CA
    github.com/johndoe | linkedin.com/in/johndoe
    
    Professional Summary
    Senior Software Engineer with 6 years of experience building scalable web applications. 
    Proficient in Python, Flask, and database optimization. Experienced in cloud deployments 
    and Agile methodologies.
    
    Technical Skills
    Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
    Frameworks: Flask, Django, React, Node.js
    Databases: PostgreSQL, MySQL, Redis
    Tools: Docker, Git, AWS (S3, EC2), Jenkins, Agile/Scrum
    
    Work Experience
    Senior Software Engineer | TechCorp Inc. | 2022 - Present
    - Spearheaded development of a microservices backend using Flask and Python, reducing API latency by 30%.
    - Designed and implemented a React dashboard with TypeScript for real-time analytics.
    - Managed relational database migrations using PostgreSQL and optimized SQL queries.
    - Deployed containerized applications using Docker to AWS ECS and maintained CI/CD pipelines in Jenkins.
    
    Software Engineer | WebApps LLC | 2020 - 2022
    - Developed web solutions using Python, Django, and JavaScript.
    - Worked closely with product owners in an Agile environment to deliver bi-weekly sprints.
    
    Education
    Master of Science in Computer Science | Stanford University | 2018 - 2020
    Bachelor of Science in Computer Science | UC Berkeley | 2014 - 2018
    """
    
    mock_job_description = """
    We are looking for a Senior Software Engineer to join our growing engineering team.
    
    Requirements:
    - 5+ years of software development experience.
    - Strong proficiency in Python and backend frameworks like Flask or Django.
    - Experience building user interfaces with React and TypeScript.
    - Solid understanding of relational databases like PostgreSQL or MySQL.
    - Experience with Docker, Kubernetes, and cloud platforms like AWS or Google Cloud.
    - Familiarity with CI/CD, Git, and Agile/Scrum methodologies.
    - Bachelor's degree in Computer Science or a related field; Master's degree is a plus.
    """
    
    print("\nRunning ATS analysis parser...")
    try:
        # Run parsing tests
        contact = parse_contact_info(mock_resume)
        print(f"Contact Info Parsed: {contact}")
        
        edu = parse_education(mock_resume)
        print(f"Education Parsed: {edu}")
        
        exp = parse_experience(mock_resume)
        print(f"Experience Parsed: {exp} years")
        
        # Run overall scoring analysis
        result = run_ats_analysis(mock_resume, mock_job_description)
        
        print("\n=== ATS ANALYSIS TEST RESULTS ===")
        print(f"Final ATS Score: {result['ats_score']}/100")
        print(f"Content Match Score: {result['resume_match_score']}%")
        print(f"Skills Match Score: {result['skills_score']}%")
        print(f"Keywords Match Score: {result['keywords_score']}%")
        print(f"Experience Score: {result['experience_score']}%")
        print(f"Education Score: {result['education_score']}%")
        print(f"Formatting Score: {result['formatting_score']}%")
        print("=================================")
        
        print("\nExtracted Data:")
        for k, v in result['extracted_data'].items():
            print(f"  {k}: {v}")
            
        print("\nAnalysis Highlights:")
        print(f"  Matched Skills: {result['analysis_results']['matched_skills']}")
        print(f"  Missing Skills: {result['analysis_results']['missing_skills']}")
        print(f"  Recommended Skills: {result['analysis_results']['recommended_skills']}")
        print(f"  Top Keywords: {result['analysis_results']['top_keywords']}")
        print(f"  Matched Keywords: {result['analysis_results']['matched_keywords']}")
        print(f"  Formatting Issues Found: {result['analysis_results']['formatting_issues']}")
        
        print("\nSuggestions Generated:")
        for idx, sug in enumerate(result['analysis_results']['suggestions'], 1):
            print(f"  {idx}. {sug['title']} ({sug['category']}): {sug['description']}")
            
        print("\nSuccess: NLP pipeline works flawlessly!")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
