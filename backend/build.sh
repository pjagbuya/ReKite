#!/usr/bin/env bash
# Render build script

set -o errexit

# Upgrade pip and install wheel
pip install --upgrade pip setuptools wheel

# Install cryptography with pre-built wheels (avoid Rust compilation)
pip install cryptography --only-binary=cryptography

# Install remaining dependencies
pip install -r requirements.txt
