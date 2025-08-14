#!/usr/bin/env python3
"""
Comprehensive test script for all 16 document types
Tests PDF generation, validation, and form handling
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.document_pdf_generator import DocumentPDFGenerator
from app.services.document_request_handler import DocumentRequestHandler

def create_sample_employee_data():
    """Create sample employee data for testing"""
    return {
        "employeeName": "Rahul Sharma",
        "employeeId": "EMP001",
        "designation": "Senior Software Engineer",
        "department": "Engineering",
        "joiningDate": "2022-01-15",
        "issueDate": datetime.now().strftime('%Y-%m-%d'),
        "relievingDate": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "salaryAmount": "75000",
        "appointmentDate": "2022-01-15",
        "promotionDate": "2023-06-01",
        "newDesignation": "Lead Software Engineer",
        "nocPurpose": "Higher studies",
        "effectiveDate": datetime.now().strftime('%Y-%m-%d'),
        "signingDate": "2022-01-15",
        "reason": "Lost ID card",
        "destination": "New York, USA",
        "purpose": "Client meeting",
        "duration": "5 days",
        "travelDate": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }

def test_document_generation():
    """Test PDF generation for all 16 document types"""
    print("🧪 Testing PDF Generation for All 16 Document Types")
    print("=" * 60)
    
    # Initialize services
    pdf_generator = DocumentPDFGenerator()
    doc_handler = DocumentRequestHandler()
    
    # Sample employee data
    employee_data = create_sample_employee_data()
    
    # Test results
    results = []
    
    # Test all 16 document types
    for doc_type in range(1, 17):
        doc_type_str = str(doc_type)
        doc_name = doc_handler.supported_documents.get(doc_type_str, f"Document Type {doc_type}")
        
        print(f"\n📄 Testing Document {doc_type}: {doc_name}")
        
        try:
            # Create details JSON
            details_json = json.dumps(employee_data)
            
            # Generate PDF
            pdf_content = pdf_generator.generate_document_pdf(
                doc_type_str, 
                doc_name, 
                details_json, 
                "test_user"
            )
            
            # Check if PDF was generated successfully
            if pdf_content and len(pdf_content) > 1000:  # Basic size check
                status = "✅ SUCCESS"
                file_size = len(pdf_content)
                results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "SUCCESS",
                    "file_size": file_size,
                    "error": None
                })
                print(f"   {status} - File size: {file_size:,} bytes")
            else:
                status = "❌ FAILED"
                results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "FAILED",
                    "file_size": 0,
                    "error": "Generated PDF is too small or empty"
                })
                print(f"   {status} - Generated PDF is too small or empty")
                
        except Exception as e:
            status = "❌ ERROR"
            results.append({
                "doc_type": doc_type,
                "doc_name": doc_name,
                "status": "ERROR",
                "file_size": 0,
                "error": str(e)
            })
            print(f"   {status} - {str(e)}")
    
    return results

def test_document_validation():
    """Test document validation for all types"""
    print("\n🔍 Testing Document Validation")
    print("=" * 40)
    
    doc_handler = DocumentRequestHandler()
    employee_data = create_sample_employee_data()
    
    validation_results = []
    
    for doc_type in range(1, 17):
        doc_type_str = str(doc_type)
        doc_name = doc_handler.supported_documents.get(doc_type_str, f"Document Type {doc_type}")
        
        print(f"\n🔍 Validating Document {doc_type}: {doc_name}")
        
        try:
            # Test with complete data
            details_json = json.dumps(employee_data)
            is_valid, message = doc_handler.validate_document_details(details_json, doc_type_str)
            
            if is_valid:
                status = "✅ VALID"
                validation_results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "VALID",
                    "message": message
                })
            else:
                status = "❌ INVALID"
                validation_results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "INVALID",
                    "message": message
                })
            
            print(f"   {status} - {message}")
            
        except Exception as e:
            status = "❌ ERROR"
            validation_results.append({
                "doc_type": doc_type,
                "doc_name": doc_name,
                "status": "ERROR",
                "message": str(e)
            })
            print(f"   {status} - {str(e)}")
    
    return validation_results

def test_document_requests():
    """Test document request submission"""
    print("\n📋 Testing Document Request Submission")
    print("=" * 45)
    
    doc_handler = DocumentRequestHandler()
    employee_data = create_sample_employee_data()
    
    request_results = []
    
    # Test a few key document types
    test_docs = [1, 2, 9, 13, 15, 16]  # Bonafide, Experience, Salary Cert, ID Replacement, Travel Auth, Visa
    
    for doc_type in test_docs:
        doc_type_str = str(doc_type)
        doc_name = doc_handler.supported_documents.get(doc_type_str, f"Document Type {doc_type}")
        
        print(f"\n📋 Testing Request for Document {doc_type}: {doc_name}")
        
        try:
            details_json = json.dumps(employee_data)
            
            # Submit request
            request = doc_handler.submit_document_request(
                doc_type_str,
                doc_name,
                details_json,
                "test_user"
            )
            
            if request.get("pdf_generated", False):
                status = "✅ SUCCESS"
                request_results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "SUCCESS",
                    "request_id": request.get("id"),
                    "pdf_generated": True
                })
            else:
                status = "⚠️ PENDING"
                request_results.append({
                    "doc_type": doc_type,
                    "doc_name": doc_name,
                    "status": "PENDING",
                    "request_id": request.get("id"),
                    "pdf_generated": False,
                    "error": request.get("error")
                })
            
            print(f"   {status} - Request ID: {request.get('id')}")
            
        except Exception as e:
            status = "❌ ERROR"
            request_results.append({
                "doc_type": doc_type,
                "doc_name": doc_name,
                "status": "ERROR",
                "error": str(e)
            })
            print(f"   {status} - {str(e)}")
    
    return request_results

def generate_test_report(generation_results, validation_results, request_results):
    """Generate comprehensive test report"""
    print("\n📊 TEST REPORT SUMMARY")
    print("=" * 50)
    
    # Generation results
    successful_generations = [r for r in generation_results if r["status"] == "SUCCESS"]
    failed_generations = [r for r in generation_results if r["status"] in ["FAILED", "ERROR"]]
    
    print(f"\n📄 PDF Generation Results:")
    print(f"   ✅ Successful: {len(successful_generations)}/16")
    print(f"   ❌ Failed: {len(failed_generations)}/16")
    
    if failed_generations:
        print("\n   Failed Documents:")
        for result in failed_generations:
            print(f"     - Document {result['doc_type']}: {result['doc_name']}")
            if result.get("error"):
                print(f"       Error: {result['error']}")
    
    # Validation results
    successful_validations = [r for r in validation_results if r["status"] == "VALID"]
    failed_validations = [r for r in validation_results if r["status"] in ["INVALID", "ERROR"]]
    
    print(f"\n🔍 Validation Results:")
    print(f"   ✅ Valid: {len(successful_validations)}/16")
    print(f"   ❌ Invalid: {len(failed_validations)}/16")
    
    # Request results
    successful_requests = [r for r in request_results if r["status"] == "SUCCESS"]
    pending_requests = [r for r in request_results if r["status"] == "PENDING"]
    failed_requests = [r for r in request_results if r["status"] == "ERROR"]
    
    print(f"\n📋 Request Submission Results:")
    print(f"   ✅ Successful: {len(successful_requests)}/{len(request_results)}")
    print(f"   ⚠️ Pending: {len(pending_requests)}/{len(request_results)}")
    print(f"   ❌ Failed: {len(failed_requests)}/{len(request_results)}")
    
    # Overall status
    total_tests = len(generation_results) + len(validation_results) + len(request_results)
    successful_tests = len(successful_generations) + len(successful_validations) + len(successful_requests)
    
    print(f"\n🎯 Overall Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if failed_generations:
        print("   - Review failed PDF generation implementations")
    if failed_validations:
        print("   - Check validation logic for document types")
    if failed_requests:
        print("   - Investigate request submission issues")
    
    if not failed_generations and not failed_validations and not failed_requests:
        print("   - All tests passed! System is ready for production.")
    
    return {
        "generation_results": generation_results,
        "validation_results": validation_results,
        "request_results": request_results,
        "summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests/total_tests)*100
        }
    }

def main():
    """Main test function"""
    print("🚀 Starting Comprehensive Document System Test")
    print("=" * 60)
    
    try:
        # Run all tests
        generation_results = test_document_generation()
        validation_results = test_document_validation()
        request_results = test_document_requests()
        
        # Generate report
        report = generate_test_report(generation_results, validation_results, request_results)
        
        # Save report to file
        report_file = Path(__file__).parent / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Test report saved to: {report_file}")
        
        # Exit with appropriate code
        if report["summary"]["success_rate"] == 100:
            print("\n🎉 All tests passed! System is ready for production.")
            sys.exit(0)
        else:
            print(f"\n⚠️ Some tests failed. Success rate: {report['summary']['success_rate']:.1f}%")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
