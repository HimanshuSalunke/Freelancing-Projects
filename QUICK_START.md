# Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r ../requirements.txt

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

### 2. Frontend Setup

```bash
# In a new terminal, navigate to project root
cd chatbot_project

# Install frontend dependencies
npm install

# Start the frontend development server
npm run dev
```

The frontend will be available at: http://localhost:3000

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
# Backend URL
BACKEND_URL=http://localhost:8000
```

## Testing the System

### 1. Health Check

Visit the health check endpoint to verify everything is working:
- Frontend: http://localhost:3000/api/health
- Backend: http://localhost:8000/health

### 2. Document Generation

1. Open http://localhost:3000 in your browser
2. Navigate to the Document Requests section
3. Select a document type (e.g., "Bonafide Certificate")
4. Fill in employee details:
   - Employee Name: Nicholas Ortiz
   - Employee ID: EMP0001
   - Designation: Admin Officer
   - Department: Product
   - Joining Date: 2021-07-14
5. Click "Validate Employee" to verify the data
6. Click "Generate Document" to create the PDF
7. Download or preview the generated document

### 3. Employee Search

1. In the Document Form, use the employee search feature
2. Type "Nicholas" in the search box
3. Select from the suggested employees to auto-fill the form

## Running Tests

### Automated Test Script

```bash
# Run the comprehensive test script
python test_fixes.py
```

This will test:
- Backend health
- Frontend health
- Employee search
- Employee validation
- Document generation
- Error handling

### Manual Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend health
curl http://localhost:3000/api/health

# Test employee search
curl -X POST http://localhost:3000/api/employee-search \
  -H "Content-Type: application/json" \
  -d '{"query":"Nicholas"}'

# Test document generation
curl -X POST http://localhost:3000/api/generate-document \
  -H "Content-Type: application/json" \
  -d '{
    "documentType":"1",
    "documentName":"Bonafide Certificate",
    "formData":{
      "employeeName":"Nicholas Ortiz",
      "employeeId":"EMP0001",
      "designation":"Admin Officer",
      "department":"Product",
      "joiningDate":"2021-07-14"
    }
  }'
```

## Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Check for missing environment variables

2. **Frontend not connecting to backend**
   - Verify BACKEND_URL in .env file
   - Check if backend is running on correct port
   - Check CORS settings

3. **PDF generation fails**
   - Check backend logs for detailed error messages
   - Verify employee data is correct
   - Check if all required fields are filled

4. **Employee validation fails**
   - Verify employee exists in the database
   - Check employee data format (dates should be YYYY-MM-DD)
   - Try with different employee data

### Logs

- **Backend logs**: Check terminal where backend is running
- **Frontend logs**: Check browser developer console
- **PDF generation logs**: Check backend terminal for detailed error messages

### File Permissions

Ensure the backend has write permissions for:
- `backend/app/data/document_requests.json`
- `backend/app/data/hr_notifications.log`

## Features Available

### Document Types
1. Bonafide / Employment Verification Letter
2. Experience Certificate
3. Offer Letter Copy
4. Appointment Letter Copy
5. Promotion Letter
6. Relieving Letter
7. Salary Slips
8. Form 16 / Tax Documents
9. Salary Certificate
10. PF Statement / UAN details
11. No Objection Certificate (NOC)
12. Non-Disclosure Agreement Copy
13. ID Card Replacement
14. Medical Insurance Card Copy
15. Business Travel Authorization Letter
16. Visa Support Letter

### Employee Data
The system includes sample employee data for testing:
- Nicholas Ortiz (EMP0001)
- Randy Drake (EMP0002)
- Andrew Quinn (EMP0003)
- And many more...

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify all dependencies are installed
4. Ensure both frontend and backend are running
5. Check the comprehensive documentation in `FRONTEND_BACKEND_FIXES.md`
