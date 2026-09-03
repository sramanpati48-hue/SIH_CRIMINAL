# Agent Instructions: SIH 26189 AI-Assisted Criminal Network Analysis System

## Project Overview
- **Project Title:** SIH 26189 AI-Assisted Criminal Network Analysis System
- **Purpose:** Provide an explainable, human-in-the-loop AI platform to extract, link, and visualize criminal networks for investigative support.

## Core Rules & Ethics
1. **Synthetic Data Only:** The system and all development activities must use synthetic data exclusively. Never use real criminal, police, phone, banking, or personally identifiable data.
2. **No Guilt Prediction:** The system is an investigation-support platform, not a guilt-prediction or automatic accusation system. Never state that a person is guilty or criminal based on a model score. Use terms like *investigative lead*, *pattern*, *priority*, or *requires human verification*.
3. **Traceability:** Every relationship and alert must include source evidence, timestamps where available, confidence scores, and verification status.
4. **Human-in-the-Loop:** Human users must always be able to accept, reject, or correct extracted information and model-generated leads.

## Technical & Coding Standards
1. **Frontend:** Use **TypeScript** in strict mode for all UI components.
2. **Backend:** Use **Python** with explicit type hints, Pydantic validation, and modular service boundaries.
3. **Database Queries:** Always use parameterized SQL and Cypher queries to prevent injection vulnerabilities.
4. **Security:** Never store secrets, API keys, or credentials in source control.

## Development & Execution Workflow
1. **Scope Control:** Do not modify unrelated files.
2. **Pre-Change Plan:** Before changing files, explicitly list the intended changes.
3. **Verification:** Run relevant tests, linting, and type checks after each milestone.
4. **Reporting:** Clearly report all changed files, commands executed, and verification results back to the user.
