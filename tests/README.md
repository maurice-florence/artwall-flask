# Firebase Connection Tests

This folder contains test scripts to verify Firebase connectivity and configuration.

## Test Script: `test_firebase_connection.py`

Comprehensive test suite that verifies:

1. ✅ Environment variables are configured
2. ✅ Firebase credentials file exists and is valid
3. ✅ Firebase Admin SDK can be initialized
4. ✅ Database connection works
5. ✅ Write permissions are functional
6. ✅ Expected database structure

## Usage

### Prerequisites

Install required package for colored output:

```powershell
pip install termcolor
```

### Run the test

```powershell
# From project root
python tests/test_firebase_connection.py
```

### Expected Output

```text
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
  Firebase Connection Test Suite
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

============================================================
  Test 1: Environment Variables
============================================================
✓ GOOGLE_APPLICATION_CREDENTIALS is set: PASSED
  → Path: ./firebase-credentials.json
✓ FIREBASE_DATABASE_URL is set: PASSED
  → URL: https://your-project.firebaseio.com

============================================================
  Test 2: Credentials File
============================================================
✓ Credentials file exists: PASSED
✓ Credentials file is valid JSON: PASSED
✓ Credentials file has required fields: PASSED
  → Project ID: your-project-id

... (more tests)

============================================================
  Test Summary
============================================================

Total Tests: 10
Passed: 10
Failed: 0
Warnings: 0
Pass Rate: 100.0%

✓ All tests passed! Firebase is ready to use.
```

## Troubleshooting

### Common Issues

1. **Environment variables not set**
   - Make sure `.env` file exists in project root
   - Check that `GOOGLE_APPLICATION_CREDENTIALS` points to correct file
   - Verify `FIREBASE_DATABASE_URL` is correct

2. **Credentials file not found**
   - Download service account JSON from Firebase Console
   - Place it in your project (don't commit to git!)
   - Update path in `.env` file

3. **Permission errors**
   - Verify you're using a Service Account key (not Web API key)
   - Check Firebase Realtime Database rules
   - Admin SDK should bypass rules, but verify in Firebase Console

4. **Connection timeout**
   - Check your internet connection
   - Verify Firebase Database URL is correct
   - Check if Firebase project is active

## What Each Test Does

### Test 1: Environment Variables

Checks if `.env` file has required Firebase configuration.

### Test 2: Credentials File

Verifies the service account JSON file exists and contains all required fields.

### Test 3: Firebase SDK Initialization

Tests if the Firebase Admin SDK can be initialized with your credentials.

### Test 4: Database Connection

Attempts to connect to your Firebase Realtime Database and read data.

### Test 5: Write Permission

Tries to write a test record to verify write access (creates and deletes `_connection_test` node).

### Test 6: Database Structure

Checks for expected paths: `/posts`, `/users`, `/user-posts`.

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed or error occurred
