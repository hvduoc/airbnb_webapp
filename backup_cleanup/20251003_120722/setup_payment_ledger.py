"""
Payment Ledger Installation and Setup Script
Run this to install and configure the Payment Ledger module
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and print status"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} found")
        return True
    else:
        print(f"⚠️  {description} not found: {file_path}")
        return False


def setup_payment_ledger():
    """Main setup function"""
    print("🚀 Payment Ledger Setup")
    print("=" * 50)

    # 1. Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    if not run_command(
        "pip install -r requirements_payments.txt",
        "Installing Payment Ledger dependencies",
    ):
        print("Please install manually: pip install -r requirements_payments.txt")

    # 2. Check if main requirements are installed
    print("\n📋 Checking existing dependencies...")
    run_command("pip install fastapi uvicorn sqlmodel", "Installing core dependencies")

    # 3. Check environment setup
    print("\n🔧 Environment Configuration...")
    env_file = Path(".env")
    env_example = Path(".env.payment.example")

    if not env_file.exists():
        print("⚠️  .env file not found. Creating from example...")
        if env_example.exists():
            # Copy example to .env
            with open(env_example, "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
            print("✅ Created .env from example")
        else:
            print("❌ .env.payment.example not found!")
    else:
        print("✅ .env file exists")

    # 4. Check Google Sheets credentials
    print("\n🔑 Google Sheets API Setup...")
    creds_file = Path("credentials/service-account.json")
    creds_readme = Path("credentials/README.md")

    check_file_exists(creds_readme, "Google Sheets setup instructions")

    if not check_file_exists(creds_file, "Google Service Account credentials"):
        print("\n📝 TO COMPLETE GOOGLE SHEETS SETUP:")
        print("   1. Read instructions in: credentials/README.md")
        print("   2. Create Google Cloud project and service account")
        print("   3. Download credentials as: credentials/service-account.json")
        print("   4. Share your Google Spreadsheet with service account email")
        print("   5. Add GOOGLE_SPREADSHEET_ID to .env file")

    # 5. Database setup
    print("\n🗄️  Database Setup...")
    print("Creating demo users for testing...")

    try:
        # Run the demo users creation script
        result = subprocess.run(
            [sys.executable, "create_payment_users.py"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ Demo users created successfully")
            print(result.stdout)
        else:
            print("⚠️  Demo users creation had issues:")
            print(result.stderr)
            print("\nYou can run this manually after starting the server:")
            print("python create_payment_users.py")
    except Exception as e:
        print(f"⚠️  Could not create demo users: {e}")
        print("Run manually after starting server: python create_payment_users.py")

    # 6. Final instructions
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Complete Google Sheets setup (see credentials/README.md)")
    print("2. Update .env with your configuration")
    print("3. Start the server: uvicorn main:app --reload")
    print("4. Visit: http://localhost:8000/payments/login")
    print("5. Login with demo credentials:")
    print("   - Assistant: assistant / assistant123")
    print("   - Manager:   manager   / manager123")
    print("   - Owner:     owner     / owner123")

    print("\n🔗 Payment Ledger URLs:")
    print("   - Login:     http://localhost:8000/payments/login")
    print("   - Dashboard: http://localhost:8000/payments/dashboard")
    print("   - API Docs:  http://localhost:8000/docs")

    print("\n📊 Features Available:")
    print("   ✅ Payment recording with Google Sheets integration")
    print("   ✅ Cash handover management")
    print("   ✅ Real-time dashboard with charts")
    print("   ✅ Role-based access control (Assistant/Manager/Owner)")
    print("   ✅ Revenue analytics and collector performance")

    if not creds_file.exists():
        print("\n⚠️  IMPORTANT: Google Sheets integration won't work until you:")
        print("   1. Set up service account credentials")
        print("   2. Configure GOOGLE_SPREADSHEET_ID in .env")


def test_installation():
    """Test if installation is working"""
    print("\n🧪 Testing Installation...")

    # Test imports
    try:
        from auth.auth_service import auth_service
        from routes_payments import router
        from services.google_sheets.service import sheets_service

        print("✅ All modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    try:
        setup_payment_ledger()
        test_installation()

        print("\n🎯 Ready to start developing with Payment Ledger!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        print("\nPlease check the error and try again, or install manually:")
        print("1. pip install -r requirements_payments.txt")
        print("2. python create_payment_users.py")
        print("3. Setup Google Sheets credentials")
        sys.exit(1)
