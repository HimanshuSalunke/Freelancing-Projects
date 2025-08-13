from __future__ import annotations

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
import os


# Create output folders under project root: ./org_data/policies and ./org_data/it_policies
project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "org_data"
policies_dir = output_dir / "policies"
it_policies_dir = output_dir / "it_policies"
policies_dir.mkdir(parents=True, exist_ok=True)
it_policies_dir.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()


def create_pdf(file_path: Path, title: str, content: list[str]) -> None:
    doc = SimpleDocTemplate(str(file_path), pagesize=A4)
    story = [Paragraph(f"<b>{title}</b>", styles["Title"]), Spacer(1, 12)]
    for paragraph in content:
        story.append(Paragraph(paragraph, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)


# HR Policies
hr_policies = {
    "employee_handbook.pdf": [
        "Welcome to the company! This handbook outlines our mission, values, and policies to ensure a respectful and productive workplace.",
        "Employees are expected to maintain professionalism, integrity, and collaboration at all times.",
    ],
    "leave_policy.pdf": [
        "Employees are entitled to 20 days of paid leave annually.",
        "Leave requests must be submitted at least 5 days in advance, except in emergencies.",
    ],
    "attendance_policy.pdf": [
        "Employees must log in by 9:30 AM and log out after completing 8 hours of work.",
        "Repeated tardiness may result in HR intervention.",
    ],
    "wfh_policy.pdf": [
        "Employees may work from home up to 3 days per week with manager approval.",
        "Ensure a secure and distraction-free workspace when working remotely.",
    ],
    "reimbursement_policy.pdf": [
        "Business-related expenses must be pre-approved by the reporting manager.",
        "Submit claims within 30 days with proper receipts.",
    ],
    "code_of_conduct.pdf": [
        "Treat all colleagues with respect and dignity.",
        "Zero tolerance for harassment, discrimination, or unethical practices.",
    ],
    "performance_review.pdf": [
        "Performance reviews occur bi-annually in June and December.",
        "Reviews assess goal achievement, skill development, and overall contribution.",
    ],
    "onboarding.pdf": [
        "New hires will undergo a 2-week onboarding program.",
        "This includes orientation, training, and introduction to key teams.",
    ],
}


# IT Policies
it_policies = {
    "acceptable_use_policy.pdf": [
        "Company systems and devices should be used primarily for work-related purposes.",
        "Prohibited activities include unauthorized access, downloading illegal software, and sharing confidential data.",
    ],
    "password_policy.pdf": [
        "Passwords must be at least 12 characters long and contain letters, numbers, and symbols.",
        "Change passwords every 90 days and never share them.",
    ],
    "device_policy.pdf": [
        "Employees are responsible for the proper use and safekeeping of assigned devices.",
        "Report lost or stolen devices to IT immediately.",
    ],
    "software_request_sop.pdf": [
        "Submit all software installation requests through the IT helpdesk portal.",
        "Unauthorized software installation is prohibited.",
    ],
    "helpdesk_guide.pdf": [
        "For IT issues, raise a ticket via the helpdesk system with detailed issue description.",
        "IT will respond within 24 hours for standard issues.",
    ],
}


def main() -> None:
    # Create HR policy PDFs
    for filename, content in hr_policies.items():
        title = filename.replace(".pdf", "").replace("_", " ").title()
        create_pdf(policies_dir / filename, title, content)

    # Create IT policy PDFs
    for filename, content in it_policies.items():
        title = filename.replace(".pdf", "").replace("_", " ").title()
        create_pdf(it_policies_dir / filename, title, content)

    print(str(output_dir))


if __name__ == "__main__":
    main()


