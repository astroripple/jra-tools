#!/bin/sh
echo "START Install"
sudo chown -R vscode:vscode .
uv venv --allow-existing
uv sync
echo "FINISH Install"