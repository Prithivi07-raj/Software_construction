"""
CloudVault Demo Seeder Script
Populates a test user account with realistic demo files for college presentations.
"""
import io
import os
from app import create_app
from models import db, User, FileRecord
from services.storage_service import get_storage_service


def seed():
    app = create_app('development')
    with app.app_context():
        db.create_all()

        demo_email = "demo@cloudvault.local"
        user = User.query.filter_by(email=demo_email).first()

        if not user:
            print(f"Creating demo user: {demo_email}")
            user = User(
                full_name="Alex Project Student",
                email=demo_email
            )
            user.set_password("Password123!")
            db.session.add(user)
            db.session.commit()
            print("Demo user created successfully!")
        else:
            print("Demo user already exists.")

        # Check existing files
        existing_count = FileRecord.query.filter_by(user_id=user.id).count()
        if existing_count > 0:
            print(f"User already has {existing_count} files. Skipping file seed.")
            return

        storage_svc = get_storage_service(app)

        sample_files = [
            (
                "Software_Construction_Project_Spec.pdf",
                b"%PDF-1.4 CloudVault Architecture Specification Document for College Evaluation.",
                "application/pdf"
            ),
            (
                "CloudVault_Architecture_Diagram.png",
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82",
                "image/png"
            ),
            (
                "Cloud_Resource_Cost_Estimation.xlsx",
                b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00Azure Blob vs Local Storage TCO Analysis",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            (
                "CloudVault_Release_v1.0_Source.zip",
                b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00CloudVault complete project archive snapshot.",
                "application/zip"
            ),
            (
                "Azure_Migration_Security_Audit.md",
                b"# CloudVault Security Audit\n\n- User isolation: Enforced\n- CSRF: Enabled\n- Storage Adapter: Ready",
                "text/markdown"
            )
        ]

        print("Seeding sample files for presentation demonstration...")
        for orig_name, raw_bytes, mime in sample_files:
            stored_name, ext = storage_svc.generate_stored_filename(orig_name)
            stream = io.BytesIO(raw_bytes)
            bytes_saved = storage_svc.save_file(user.id, stream, stored_name)
            cat = FileRecord.categorize_extension(ext)

            rec = FileRecord(
                user_id=user.id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_size=bytes_saved,
                file_extension=ext.lstrip('.'),
                mime_type=mime,
                category=cat
            )
            db.session.add(rec)

        db.session.commit()
        print("Demo seed complete!")
        print("\nDemo Credentials:")
        print("Email:    demo@cloudvault.local")
        print("Password: Password123!")


if __name__ == '__main__':
    seed()
