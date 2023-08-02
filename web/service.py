from subprocess import run

run(['streamlit', 'run', 'web/simple.py', '--server.port', '8502'])
