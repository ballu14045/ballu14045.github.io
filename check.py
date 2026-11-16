import subprocess

# ... (rest of your script) ...

print("Attempting to push to GitHub...")
try:
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Auto-published AI rewritten article via AnythingLLM'], check=True)
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    print("Successfully pushed to GitHub!")
except subprocess.CalledProcessError as e:
    print(f"Git operation failed: {e}")
