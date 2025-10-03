"""
Create Demo Users for Payment Ledger System
Run this script to create initial users for testing
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from sqlmodel import select

from db import get_session_context
from models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_demo_users():
    """Create demo users for Payment Ledger system"""
    
    with get_session_context() as session:
        users = [
            {
                "username": "assistant",
                "email": "assistant@example.com",
                "full_name": "Trợ lý Thu tiền",
                "password": "assistant123",
                "role": "user"
            },
            {
                "username": "manager", 
                "email": "manager@example.com",
                "full_name": "Quản lý Tài chính",
                "password": "manager123",
                "role": "manager"
            },
            {
                "username": "owner",
                "email": "owner@example.com", 
                "full_name": "Chủ Kinh doanh",
                "password": "owner123",
                "role": "admin"
            }
        ]
        
        for user_data in users:
            # Check if user already exists
            existing_user = session.exec(
                select(User).where(User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"✅ User '{user_data['username']}' already exists - skipping")
                continue
                
            # Create new user
            hashed_password = pwd_context.hash(user_data["password"])
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                accessible_properties="[]"  # Empty JSON array for all properties access
            )
            
            session.add(user)
            print(f"✅ Created user: {user_data['username']} ({user_data['full_name']})")
        
        session.commit()
        print("\n🎉 Demo users created successfully!")
        print("\n📋 Login credentials:")
        print("=" * 50)
        print("Trợ lý:   assistant / assistant123")
        print("Quản lý:  manager   / manager123") 
        print("Chủ:      owner     / owner123")
        print("=" * 50)
        print("\n🔗 Access Payment Ledger at: http://localhost:8000/payments/login")

def verify_users():
    """Verify that demo users were created correctly"""
    with get_session_context() as session:
        users = session.exec(select(User)).all()
        
        print(f"\n📊 Total users in database: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.full_name}) - Role: {user.role}")

if __name__ == "__main__":
    print("🚀 Creating Payment Ledger demo users...")
    print("=" * 60)
    
    try:
        create_demo_users()
        verify_users()
        
        print("\n✅ Setup complete! You can now:")
        print("  1. Start the server: uvicorn main:app --reload")
        print("  2. Visit: http://localhost:8000/payments/login")
        print("  3. Login with any of the demo accounts above")
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        print("\nPlease make sure:")
        print("  1. Database is initialized (run the main app first)")
        print("  2. All required packages are installed")
        sys.exit(1)