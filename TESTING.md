# Running Unit Tests

This document provides instructions on how to run the unit tests for the Flask AI Interviewer application.

## Prerequisites

- Python 3.x installed.
- Flask and other dependencies from `requirements.txt` installed. It's recommended to use a virtual environment.

```bash
# (Optional, but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

## Running Tests

The tests are written using the `unittest` module.

1.  **Navigate to the project root directory** (the directory containing `app.py` and the `tests` folder).

2.  **Run the tests using the following command:**

    ```bash
    python -m unittest discover tests
    ```

    Alternatively, you can run a specific test file:

    ```bash
    python -m unittest tests.test_app
    ```

    Or even a specific test case or method:
    ```bash
    python -m unittest tests.test_app.AppTestCase
    python -m unittest tests.test_app.AppTestCase.test_upload_qa_csv
    ```

## Expected Output

If all tests pass, you will see output similar to this:

```
.......
----------------------------------------------------------------------
Ran 7 tests in 0.123s

OK
```

Each dot (`.`) represents a passing test. If any tests fail, you will see details about the failures.
