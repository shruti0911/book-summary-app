#!/bin/bash

# Set color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking project structure for deployment...${NC}"

# Check for required root files
echo -e "\n${YELLOW}Checking required files:${NC}"
required_files=("requirements.txt" "runtime.txt" "Procfile" "README.md" ".streamlit/config.toml")
for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file found"
  else
    echo -e "${RED}✗${NC} $file not found"
  fi
done

# Check for app structure
echo -e "\n${YELLOW}Checking app structure:${NC}"
if [ -f "app/app.py" ]; then
  echo -e "${GREEN}✓${NC} app/app.py found"
else
  echo -e "${RED}✗${NC} app/app.py not found"
fi

if [ -d "app/helpers" ]; then
  echo -e "${GREEN}✓${NC} app/helpers directory found"
else
  echo -e "${RED}✗${NC} app/helpers directory not found"
fi

if [ -f "app/__init__.py" ]; then
  echo -e "${GREEN}✓${NC} app/__init__.py found"
else
  echo -e "${RED}✗${NC} app/__init__.py not found"
fi

if [ -f "app/helpers/__init__.py" ]; then
  echo -e "${GREEN}✓${NC} app/helpers/__init__.py found"
else
  echo -e "${RED}✗${NC} app/helpers/__init__.py not found"
fi

# Check for duplicated files in app directory
echo -e "\n${YELLOW}Checking for duplicate files:${NC}"
for file in "requirements.txt" "runtime.txt" ".gitignore" "README.md"; do
  if [ -f "app/$file" ]; then
    echo -e "${RED}✗${NC} Duplicate $file found in app directory"
  else
    echo -e "${GREEN}✓${NC} No duplicate $file in app directory"
  fi
done

# Check for nested .git directory
if [ -d "app/.git" ]; then
  echo -e "${RED}✗${NC} Nested .git directory found in app directory"
else
  echo -e "${GREEN}✓${NC} No nested .git directory"
fi

echo -e "\n${YELLOW}Structure check complete!${NC}" 