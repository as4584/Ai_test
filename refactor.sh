#!/bin/bash
#
# Refactoring Script: Minimal Real-Time Voice Pipeline
# This script archives non-essential code and restructures the project
# for minimal latency production runtime.
#
# Date: November 30, 2025
# Target: /root/antigravity_bundle/testing/ai_receptionist
#
# IMPORTANT: Review this script before executing!
# This will move significant portions of the codebase to archive/
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/root/antigravity_bundle/testing/ai_receptionist"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}AI Receptionist - Minimal Pipeline Refactor${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Change to project directory
cd "$PROJECT_ROOT" || exit 1

# Confirm with user
echo -e "${YELLOW}WARNING: This will archive significant portions of the codebase.${NC}"
echo -e "${YELLOW}Please ensure you have committed all changes to git first.${NC}"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo -e "${RED}Aborted by user.${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting refactoring process...${NC}"
echo ""

# ============================================================================
# STEP 1: Create archive directory structure
# ============================================================================
echo -e "${BLUE}[Step 1/7]${NC} Creating archive directory structure..."

mkdir -p archive/root
mkdir -p archive/module
mkdir -p archive/config
mkdir -p archive/docs

echo -e "${GREEN}✓ Archive directories created${NC}"
echo ""

# ============================================================================
# STEP 2: Backup current requirements.txt
# ============================================================================
echo -e "${BLUE}[Step 2/7]${NC} Backing up requirements.txt..."

if [ -f requirements.txt ]; then
    cp requirements.txt archive/root/requirements.txt.original
    echo -e "${GREEN}✓ requirements.txt backed up${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found (skipping)${NC}"
fi
echo ""

# ============================================================================
# STEP 3: Archive root-level folders
# ============================================================================
echo -e "${BLUE}[Step 3/7]${NC} Archiving root-level folders..."

# Cache folders
for folder in .streamlit .pytest_cache .ruff_cache __pycache__; do
    if [ -d "$folder" ]; then
        echo "  - Moving $folder"
        mv "$folder" archive/root/ 2>/dev/null || rm -rf "$folder"
    fi
done

# Infrastructure folders
for folder in alembic data docs PRODUCTS scripts tests tools; do
    if [ -d "$folder" ]; then
        echo "  - Moving $folder"
        mv "$folder" archive/root/
    fi
done

echo -e "${GREEN}✓ Root-level folders archived${NC}"
echo ""

# ============================================================================
# STEP 4: Archive root-level files
# ============================================================================
echo -e "${BLUE}[Step 4/7]${NC} Archiving root-level files..."

# Config files
for file in alembic.ini docker-compose.dev.yml pytest.ini; do
    if [ -f "$file" ]; then
        echo "  - Moving $file"
        mv "$file" archive/config/
    fi
done

# Documentation files
for file in COMMIT_MSG.txt EVAL_SYSTEM_README.md REFACTORING_SUMMARY.md \
            TECHNICAL_DEBT_AUDIT.md onboarding_checklist.md pilot_agreement.md; do
    if [ -f "$file" ]; then
        echo "  - Moving $file"
        mv "$file" archive/docs/
    fi
done

# Test files
for file in test_improvements.py test_voice_integration.py; do
    if [ -f "$file" ]; then
        echo "  - Moving $file"
        mv "$file" archive/root/
    fi
done

# Monitoring files
for file in call_monitor.py start_monitor.py; do
    if [ -f "$file" ]; then
        echo "  - Moving $file"
        mv "$file" archive/root/
    fi
done

echo -e "${GREEN}✓ Root-level files archived${NC}"
echo ""

# ============================================================================
# STEP 5: Archive module-level folders and files
# ============================================================================
echo -e "${BLUE}[Step 5/7]${NC} Archiving module-level components..."

cd ai_receptionist || exit 1

# Cache folders
for folder in .pytest_cache .ruff_cache __pycache__; do
    if [ -d "$folder" ]; then
        echo "  - Moving ai_receptionist/$folder"
        rm -rf "$folder"  # Safe to delete cache
    fi
done

# UI and test folders
for folder in static tests; do
    if [ -d "$folder" ]; then
        echo "  - Moving ai_receptionist/$folder"
        mv "$folder" ../archive/module/
    fi
done

# Database and workers
for folder in db workers; do
    if [ -d "$folder" ]; then
        echo "  - Moving ai_receptionist/$folder"
        mv "$folder" ../archive/module/
    fi
done

# Service subfolders
if [ -d "services/billing" ]; then
    echo "  - Moving ai_receptionist/services/billing"
    mv services/billing ../archive/module/
fi

if [ -d "services/flags" ]; then
    echo "  - Moving ai_receptionist/services/flags"
    mv services/flags ../archive/module/
fi

# Service files
if [ -f "services/rag.py" ]; then
    echo "  - Moving ai_receptionist/services/rag.py"
    mv services/rag.py ../archive/module/
fi

if [ -f "services/router.py" ]; then
    echo "  - Moving ai_receptionist/services/router.py"
    mv services/router.py ../archive/module/
fi

# Admin API
if [ -f "app/api/admin.py" ]; then
    echo "  - Moving ai_receptionist/app/api/admin.py"
    mv app/api/admin.py ../archive/module/
fi

# Legacy API folder
if [ -d "api" ]; then
    echo "  - Moving ai_receptionist/api (legacy)"
    mv api ../archive/module/
fi

# Agent folder (optional - evaluate based on use case)
if [ -d "agent" ]; then
    echo "  - Moving ai_receptionist/agent"
    echo -e "${YELLOW}    Note: Agent has hardcoded conversation logic (396 lines)${NC}"
    echo -e "${YELLOW}    This will be replaced by Gemini integration${NC}"
    mv agent ../archive/module/
fi

cd ..

echo -e "${GREEN}✓ Module-level components archived${NC}"
echo ""

# ============================================================================
# STEP 6: Clean up Python cache files
# ============================================================================
echo -e "${BLUE}[Step 6/7]${NC} Cleaning up Python cache files..."

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

echo -e "${GREEN}✓ Cache files cleaned${NC}"
echo ""

# ============================================================================
# STEP 7: Create new minimal requirements.txt
# ============================================================================
echo -e "${BLUE}[Step 7/7]${NC} Creating minimal requirements.txt..."

if [ -f "requirements.minimal.txt" ]; then
    echo "  - Using requirements.minimal.txt as new requirements.txt"
    mv requirements.txt archive/root/requirements.txt.old 2>/dev/null || true
    cp requirements.minimal.txt requirements.txt
    echo -e "${GREEN}✓ Minimal requirements.txt created${NC}"
else
    echo -e "${YELLOW}⚠ requirements.minimal.txt not found${NC}"
    echo -e "${YELLOW}  Creating minimal requirements.txt now...${NC}"
    
    cat > requirements.txt << 'EOF'
# Minimal Production Requirements for Real-Time Voice Pipeline
# Core Web Framework
fastapi==0.118.2
uvicorn[standard]==0.37.0

# HTTP Client
httpx==0.28.1

# Twilio Integration
twilio==9.8.3

# Google Gemini AI
google-generativeai==0.8.3

# Configuration
pydantic==2.12.0
pydantic-settings==2.4.0
python-dotenv==1.1.1
EOF
    
    echo -e "${GREEN}✓ Minimal requirements.txt created from template${NC}"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Refactoring Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

echo -e "${GREEN}Summary:${NC}"
echo "  - All non-essential code moved to archive/"
echo "  - requirements.txt reduced from 50+ to 7-8 packages"
echo "  - Python cache files cleaned"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review archived files in archive/ directory"
echo "  2. Create ai_receptionist/services/ai/gemini.py (NEW)"
echo "  3. Simplify ai_receptionist/app/main.py (remove UI/admin)"
echo "  4. Simplify ai_receptionist/config/settings.py (remove DB/Redis)"
echo "  5. Update ai_receptionist/core/di.py (remove unused dependencies)"
echo "  6. Test the /twilio/webhook endpoint"
echo "  7. Install new dependencies: pip install -r requirements.txt"
echo ""

echo -e "${BLUE}Files to modify manually:${NC}"
echo "  - ai_receptionist/app/main.py (simplify)"
echo "  - ai_receptionist/config/settings.py (simplify)"
echo "  - ai_receptionist/core/di.py (simplify)"
echo ""

echo -e "${GREEN}Archive location:${NC} $PROJECT_ROOT/archive/"
echo ""

echo -e "${YELLOW}Note: Voice service folder (services/voice/) was NOT archived.${NC}"
echo -e "${YELLOW}Review intents.py to decide if Gemini should replace it.${NC}"
echo ""

# Create a summary file
cat > archive/ARCHIVE_SUMMARY.txt << EOF
Archive Summary
===============
Date: $(date)
Project: AI Receptionist - Minimal Voice Pipeline Refactoring

Archived Folders:
-----------------
Root-level:
  - alembic/ (database migrations)
  - data/ (sample data)
  - docs/ (documentation)
  - PRODUCTS/ (product specs)
  - scripts/ (helper scripts)
  - tests/ (root tests)
  - tools/ (admin tools)
  - .streamlit/ (streamlit config)
  - .pytest_cache/ (pytest cache)
  - .ruff_cache/ (ruff cache)

Module-level (ai_receptionist/):
  - static/ (UI components)
  - tests/ (module tests)
  - db/ (database layer)
  - workers/ (background jobs)
  - services/billing/ (billing service)
  - services/flags/ (feature flags)
  - agent/ (conversation bot)
  - api/ (legacy API)

Archived Files:
---------------
Config:
  - alembic.ini
  - docker-compose.dev.yml
  - pytest.ini

Documentation:
  - COMMIT_MSG.txt
  - EVAL_SYSTEM_README.md
  - REFACTORING_SUMMARY.md
  - TECHNICAL_DEBT_AUDIT.md
  - onboarding_checklist.md
  - pilot_agreement.md

Code:
  - call_monitor.py
  - start_monitor.py
  - test_improvements.py
  - test_voice_integration.py
  - services/rag.py
  - services/router.py
  - app/api/admin.py

Dependencies Reduced:
---------------------
Before: 50+ packages
After: 7-8 packages

Removed packages:
  - alembic, SQLAlchemy (database)
  - redis (caching)
  - streamlit (UI framework)
  - openai (replaced by google-generativeai)
  - pytest (testing)
  - All streamlit dependencies (numpy, pandas, altair, etc.)
  - All SQLAlchemy dependencies (greenlet, etc.)
  - All test dependencies (pytest-json-report, pytest-metadata)

Restoration:
------------
To restore any archived component:
  mv archive/root/<folder_or_file> .
  mv archive/module/<folder_or_file> ai_receptionist/

To restore original requirements.txt:
  cp archive/root/requirements.txt.original requirements.txt
EOF

echo -e "${GREEN}Archive summary created: archive/ARCHIVE_SUMMARY.txt${NC}"
echo ""

echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Refactoring script completed successfully!${NC}"
echo -e "${BLUE}============================================${NC}"
