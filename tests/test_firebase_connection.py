import sys

"""
Firebase Connection Test Script
Tests Firebase credentials and database connectivity
"""

import os
import firebase_admin
from firebase_admin import credentials, db
from termcolor import colored
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseConnectionTest:
    """Test suite for Firebase connectivity"""

    def __init__(self):
        self.credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.database_url = os.environ.get("FIREBASE_DATABASE_URL")
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = []

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)

    def print_test(self, test_name, passed, message=""):
        """Print test result"""
        if passed:
            print(f"✓ {test_name}: {colored('PASSED', 'green')}")
            if message:
                print(f"  → {message}")
            self.passed_tests += 1
        else:
            print(f"✗ {test_name}: {colored('FAILED', 'red')}")
            if message:
                print(f"  → {message}")
            self.failed_tests += 1

    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠ {colored('WARNING', 'yellow')}: {message}")
        self.warnings.append(message)

    def test_environment_variables(self):
        """Test 1: Check if environment variables are set"""
        self.print_header("Test 1: Environment Variables")

        # Check GOOGLE_APPLICATION_CREDENTIALS
        if self.credentials_path:
            self.print_test(
                "GOOGLE_APPLICATION_CREDENTIALS is set",
                True,
                f"Path: {self.credentials_path}",
            )
        else:
            self.print_test(
                "GOOGLE_APPLICATION_CREDENTIALS is set",
                False,
                "Environment variable not found in .env file",
            )
            return False

        # Check FIREBASE_DATABASE_URL
        if self.database_url:
            self.print_test(
                "FIREBASE_DATABASE_URL is set", True, f"URL: {self.database_url}"
            )
        else:
            self.print_test(
                "FIREBASE_DATABASE_URL is set",
                False,
                "Environment variable not found in .env file",
            )
            return False

        # Check Client-side Config
        client_vars = [
            "FIREBASE_API_KEY",
            "FIREBASE_AUTH_DOMAIN",
            "FIREBASE_PROJECT_ID",
            "FIREBASE_APP_ID",
        ]

        missing_client_vars = [var for var in client_vars if not os.environ.get(var)]

        if missing_client_vars:
            self.print_test(
                "Client-side Firebase Config",
                False,
                f"Missing variables: {', '.join(missing_client_vars)}",
            )
            return False

        # Check for placeholders
        placeholders = ["YOUR_", "INSERT_", "CHANGE_ME"]
        found_placeholders = []
        for var in client_vars:
            val = os.environ.get(var, "")
            if any(p in val for p in placeholders) or val == "":
                found_placeholders.append(var)

        if found_placeholders:
            self.print_test(
                "Client-side Firebase Config",
                False,
                f"Variables contain placeholders: {', '.join(found_placeholders)}",
            )
            return False

        self.print_test(
            "Client-side Firebase Config",
            True,
            "All required client-side variables are set and appear valid",
        )

        return True

    def test_credentials_file(self):
        """Test 2: Check if credentials file exists and is valid JSON"""
        self.print_header("Test 2: Credentials File")

        # Check if credentials_path is set
        if not self.credentials_path:
            self.print_test(
                "Credentials file exists", False, "Credentials path not set"
            )
            return False

        # Check if file exists
        if not os.path.exists(self.credentials_path):
            self.print_test(
                "Credentials file exists",
                False,
                f"File not found at: {self.credentials_path}",
            )
            return False
        else:
            self.print_test(
                "Credentials file exists", True, f"Found at: {self.credentials_path}"
            )

        # Check if file is readable
        try:
            with open(self.credentials_path, "r", encoding="utf-8") as f:
                creds_data = json.load(f)

            self.print_test(
                "Credentials file is valid JSON", True, "Successfully parsed JSON"
            )

            # Check for required fields
            required_fields = [
                "type",
                "project_id",
                "private_key_id",
                "private_key",
                "client_email",
            ]
            missing_fields = [
                field for field in required_fields if field not in creds_data
            ]

            if missing_fields:
                self.print_test(
                    "Credentials file has required fields",
                    False,
                    f"Missing fields: {', '.join(missing_fields)}",
                )
                return False
            else:
                self.print_test(
                    "Credentials file has required fields",
                    True,
                    f"Project ID: {creds_data.get('project_id')}",
                )

            # Check if it's a service account
            if creds_data.get("type") != "service_account":
                self.print_warning(
                    f"Credentials type is '{creds_data.get('type')}', expected 'service_account'"
                )

            return True

        except json.JSONDecodeError as e:
            self.print_test(
                "Credentials file is valid JSON", False, f"JSON parse error: {str(e)}"
            )
            return False
        except Exception as e:
            self.print_test(
                "Credentials file is readable", False, f"Error reading file: {str(e)}"
            )
            return False

    def test_firebase_initialization(self):
        """Test 3: Initialize Firebase Admin SDK"""
        self.print_header("Test 3: Firebase SDK Initialization")

        try:
            # Check if already initialized
            if firebase_admin._apps:
                self.print_warning("Firebase already initialized, using existing app")
                app = firebase_admin.get_app()
            else:
                # Initialize Firebase
                cred = credentials.Certificate(self.credentials_path)
                app = firebase_admin.initialize_app(
                    cred, {"databaseURL": self.database_url}
                )

            self.print_test(
                "Firebase Admin SDK initialized", True, f"App name: {app.name}"
            )
            return True

        except Exception as e:
            self.print_test("Firebase Admin SDK initialized", False, f"Error: {str(e)}")
            return False

    def test_database_connection(self):
        """Test 4: Test database connectivity"""
        self.print_header("Test 4: Database Connection")

        try:
            # Get database reference
            ref = db.reference("/")

            self.print_test(
                "Database reference obtained",
                True,
                "Successfully connected to root reference",
            )

            # Try to read from database
            try:
                # Read a small amount of data (or check if database exists)
                data = ref.get()  # type: ignore[misc]

                if data is None:
                    self.print_test(
                        "Database read operation",
                        True,
                        "Database is empty (this is normal for new projects)",
                    )
                else:
                    data_keys = list(data.keys()) if isinstance(data, dict) else []
                    self.print_test(
                        "Database read operation",
                        True,
                        f"Found {len(data_keys)} top-level keys: {', '.join(data_keys[:5])}",
                    )

            except Exception as e:
                self.print_test(
                    "Database read operation", False, f"Error reading data: {str(e)}"
                )
                return False

            return True

        except Exception as e:
            self.print_test("Database connection", False, f"Error: {str(e)}")
            return False

    def test_database_write_permission(self):
        """Test 5: Test write permissions (optional)"""
        self.print_header("Test 5: Database Write Permission (Optional)")

        try:
            # Create a test reference
            test_ref = db.reference("_connection_test")

            # Try to write test data
            import time

            test_data = {
                "timestamp": time.time(),
                "message": "Connection test from Python",
            }

            test_ref.set(test_data)

            self.print_test(
                "Database write operation", True, "Successfully wrote test data"
            )

            # Try to read it back
            read_data = test_ref.get()  # type: ignore[misc]

            if (
                read_data
                and isinstance(read_data, dict)
                and read_data.get("message") == test_data["message"]
            ):
                self.print_test(
                    "Database read-after-write",
                    True,
                    "Successfully verified written data",
                )
            else:
                self.print_test(
                    "Database read-after-write", False, "Data mismatch after write"
                )

            # Clean up test data
            test_ref.delete()
            self.print_test("Database cleanup", True, "Test data removed")

            return True

        except Exception as e:
            self.print_test("Database write operation", False, f"Error: {str(e)}")
            self.print_warning(
                "Write test failed. This might be due to database rules. "
                "Admin SDK should have full access."
            )
            return False

    def test_database_structure(self):
        """Test 6: Check for expected database structure"""
        self.print_header("Test 6: Database Structure Check")

        try:
            ref = db.reference("/")
            data = ref.get()  # type: ignore[misc]

            expected_paths = ["posts", "users", "user-posts"]

            if data is None:
                self.print_warning(
                    "Database is empty. Expected paths will be created when data is added."
                )
                return True

            existing_paths = list(data.keys()) if isinstance(data, dict) else []

            for path in expected_paths:
                if path in existing_paths:
                    self.print_test(
                        f"Path '/{path}' exists", True, "Structure is ready"
                    )
                else:
                    self.print_warning(
                        f"Path '/{path}' not found (will be created automatically)"
                    )

            return True

        except Exception as e:
            self.print_test("Database structure check", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "🔥" * 30)
        print(colored("  Firebase Connection Test Suite", "cyan", attrs=["bold"]))
        print("🔥" * 30)

        # Test 1: Environment variables
        if not self.test_environment_variables():
            print(
                "\n"
                + colored("Tests aborted: Environment variables not configured", "red")
            )
            return False

        # Test 2: Credentials file
        if not self.test_credentials_file():
            print("\n" + colored("Tests aborted: Credentials file invalid", "red"))
            return False

        # Test 3: Firebase initialization
        if not self.test_firebase_initialization():
            print("\n" + colored("Tests aborted: Cannot initialize Firebase", "red"))
            return False

        # Test 4: Database connection
        if not self.test_database_connection():
            print("\n" + colored("Tests aborted: Cannot connect to database", "red"))
            return False

        # Test 5: Write permissions (continue even if failed)
        self.test_database_write_permission()

        # Test 6: Database structure
        self.test_database_structure()

        # Print summary
        self.print_summary()

        return self.failed_tests == 0

    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")

        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {colored(self.passed_tests, 'green')}")
        print(f"Failed: {colored(self.failed_tests, 'red')}")
        print(f"Warnings: {colored(len(self.warnings), 'yellow')}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        if self.failed_tests == 0:
            print(
                colored(
                    "✓ All tests passed! Firebase is ready to use.",
                    "green",
                    attrs=["bold"],
                )
            )
        else:
            print(
                colored(
                    "✗ Some tests failed. Please check the configuration.",
                    "red",
                    attrs=["bold"],
                )
            )

        if self.warnings:
            print(f"\n{colored('Warnings:', 'yellow', attrs=['bold'])}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")


def main():
    """Main test runner"""
    try:
        tester = FirebaseConnectionTest()
        success = tester.run_all_tests()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{colored('FATAL ERROR:', 'red', attrs=['bold'])} {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
