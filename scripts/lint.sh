#!/bin/bash

# Cork Mobility Lab - Linting and formatting script

set -e

echo "🔍 Cork Mobility Lab Code Quality Check"
echo "========================================"

echo ""
echo "1️⃣  Formatting with Black..."
black simulation/ apps/api/ tests/ || true

echo ""
echo "2️⃣  Sorting imports with isort..."
isort simulation/ apps/api/ tests/ || true

echo ""
echo "3️⃣  Linting with Ruff..."
ruff check simulation/ apps/api/ tests/ || true

echo ""
echo "4️⃣  Type checking with mypy..."
mypy simulation/ apps/api/ || true

echo ""
echo "✅ Code quality check complete!"
