import os

print("Starting the test_write script...")

try:
    file_path = 'app/static/avatars/test_file.txt'
    print(f"Attempting to write to {file_path}...")
    with open(file_path, 'w') as f:
        f.write('This is a test file.')
    print(f"File created successfully at {file_path}")
except Exception as e:
    print(f"Error creating file: {e}")
