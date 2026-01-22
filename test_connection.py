# test_connection.py
import database as db
import sys

# This mock function will be used to replace tkinter.messagebox.showerror
# to avoid GUI popups in the headless environment.
def mock_showerror(title, message):
    """A mock function to print error messages instead of showing a GUI popup."""
    print(f"[ERROR POPUP] Title: {title}, Message: {message}")

# Replace the real showerror with our mock version
db.messagebox.showerror = mock_showerror

print("Attempting to connect to the database...")
connection = db.conexao()

if connection:
    print("Database connection successful!")
    connection.close()
    print("Connection closed.")
    sys.exit(0)  # Exit with success code
else:
    print("Database connection failed. Check .env file and database server.")
    sys.exit(1)  # Exit with failure code
