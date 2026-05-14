# Enterprise RAG Intelligence System

## Overview
A secure, context-aware Retrieval-Augmented Generation (RAG) system with Role-Based Access Control (RBAC) built using Python and Groq LLM.

## Features
- Multi-format data support (CSV, JSON, TXT)
- Strict RBAC enforcement
- Grounded responses with source citations
- Intelligent query routing
- Minimal hallucinations

## Project Structure

enterprise_rag/
├── data/
│   ├── employees.csv
│   ├── audit_log.json
│   ├── policy.txt
│   └── access_control.json
└── rag_system.py





## Setup
1. Install dependencies:
pip install groq

2. Add your Groq API key in rag_system.py

3. Run:
python rag_system.py

## Test Users & Roles
| Username | Role     | Access                          |
|----------|----------|---------------------------------|
| sara     | HR       | employees.csv, policy.txt       |
| john     | Finance  | employees.csv, policy.txt       |
| mike     | Engineer | audit_log.json, policy.txt      |
| admin    | Admin    | All sources                     |

## Demo Results
- HR cannot access salary data (RBAC enforced)
- Finance can view employee salaries with citations
- Engineer can access audit logs only
- Admin has full access to all data sources