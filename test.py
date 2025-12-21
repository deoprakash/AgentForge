"""
Standalone Ollama prompt helper.
Prompts the user for input, sends it to a local Ollama model via the CLI,
and prints the reply. No repo-local imports are used.

Usage (PowerShell):
  python test.py

If the model is missing, pull one first, e.g.:
  ollama pull llama3
"""

import shutil
import subprocess
import sys


def main() -> int:
	# Ensure the Ollama CLI is available before proceeding.
	if shutil.which("ollama") is None:
		print("Ollama CLI not found. Install Ollama or add it to PATH.")
		return 1

	prompt = input("Enter your prompt for Ollama: ")
	if not prompt.strip():
		print("No prompt provided. Exiting.")
		return 0

	# Call ollama run with a default model; change model name if desired.
	model = "llama3"
	try:
		result = subprocess.run(
			["ollama", "run", model],
			input=prompt,
			text=True,
			capture_output=True,
			check=False,
		)
	except OSError as exc:
		print(f"Failed to launch Ollama CLI: {exc}")
		return 1

	if result.returncode != 0:
		print("Ollama returned an error:")
		print(result.stderr.strip() or "(no stderr output)")
		return result.returncode

	# Print the model's reply.
	print("\n--- Ollama reply ---\n")
	print(result.stdout.strip())
	return 0


if __name__ == "__main__":
	sys.exit(main())
