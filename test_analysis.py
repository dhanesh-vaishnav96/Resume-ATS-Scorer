import requests
import os

url = "http://127.0.0.1:8000/api/v1/analyze"
resume_path = r"d:\ATS Score Generator\uploads\879ad5c6-68cd-483d-8dad-1a2925de1b14_Bhawesh_Vyas.pdf"
jd = "We are looking for a B.Tech student with skills in JavaScript, C++, HTML, CSS, and React. Experience with internships is a plus."

if not os.path.exists(resume_path):
    print(f"Error: Resume file not found at {resume_path}")
    exit(1)

with open(resume_path, "rb") as f:
    files = {"resume": (os.path.basename(resume_path), f, "application/pdf")}
    data = {"job_description": jd}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Analysis Successful!")
            print(f"ATS Score: {result.get('ats_score')}")
            print(f"Grade: {result.get('grade')}")
            print(f"Matched Skills: {result.get('skills_matched')}")
            # print(f"Recommendation: {result.get('recommendation')[:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
