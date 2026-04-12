import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app import create_app
from models import query_db

app = create_app()
client = app.test_client()

def login(email, password='123456'):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    if res.status_code == 200:
        return res.json['token']
    print(f'Login failed for {email}: {res.json}')
    return None

def run_test():
    print('--- Starting Flask Test Client E2E Workflow ---')

    # 1. Student Login & Submit
    student_token = login('student@test.com')
    if not student_token: return
    headers = {'Authorization': f'Bearer {student_token}'}
    
    res = client.post('/api/student/request', headers=headers)
    
    if res.status_code == 201:
        req_id = res.json.get('request', {}).get('id')
        print('Student created request:', res.json)
    else:
        res = client.get('/api/student/status', headers=headers)
        if res.status_code == 200:
            reqs = res.json.get('requests', [])
            if reqs:
                req_id = reqs[0]['id']
                print('Using existing student request:', req_id)
            else:
                print('No request found or created.')
                return
        else:
            print('Failed to get student requests:', res.status_code, res.data)
            return

    # 2. Faculty Login & Approve
    print('Logging in as Faculty...')
    faculty_token = login('faculty@test.com')
    if not faculty_token: return
    headers = {'Authorization': f'Bearer {faculty_token}'}
    print(f'Sending faculty approval for {req_id}...')
    res = client.post(f'/api/faculty/approve/{req_id}', json={'action': 'approve', 'remarks': 'Looks good'}, headers=headers)
    print('Faculty approve request response:', res.status_code, res.json)

    # 3. Admin Login & Clear Depts
    print('Logging in as Admin...')
    admin_token = login('admin@test.com')
    if not admin_token: return
    headers = {'Authorization': f'Bearer {admin_token}'}
    res = client.get('/api/admin/departments', headers=headers)
    depts = res.json.get('departments', [])
    for dept in depts:
        if dept['name'].lower() != 'faculty':
            print(f'Sending admin clearance for {dept["name"]} on {req_id}...')
            res = client.post(f'/api/admin/approve/{req_id}', json={'department_id': dept['id'], 'action': 'approve', 'remarks': 'Cleared'}, headers=headers)
            print(f'Admin approve dept {dept["name"]} response:', res.status_code, res.json)

    # 4. HOD Login & Approve
    print('Logging in as HOD...')
    hod_token = login('hod@test.com')
    if not hod_token: return
    headers = {'Authorization': f'Bearer {hod_token}'}
    print(f'Sending HOD approval for {req_id}...')
    res = client.post(f'/api/hod/approve/{req_id}', json={'action': 'approve', 'remarks': 'HOD Approved'}, headers=headers)
    print('HOD approve request response:', res.status_code, res.json)

    # 5. Staff Login & Generate Ticket
    print('Logging in as Staff...')
    staff_token = login('staff@test.com')
    if not staff_token: return
    headers = {'Authorization': f'Bearer {staff_token}'}
    print(f'Sending Staff ticket generation for {req_id}...')
    res = client.post(f'/api/staff/hallticket/{req_id}', headers=headers)
    print('Staff generate hall ticket response:', res.status_code, res.json)

    # 6. Student Login & Get Ticket
    print('Logging in as Student (Final)...')
    student_token = login('student@test.com')
    headers = {'Authorization': f'Bearer {student_token}'}
    print(f'Fetching Student hall ticket for {req_id}...')
    res = client.get(f'/api/staff/hallticket/{req_id}', headers=headers)
    print('Student get hall ticket response:', res.status_code, res.json)
    print('--- Test Complete ---')

if __name__ == '__main__':
    run_test()
