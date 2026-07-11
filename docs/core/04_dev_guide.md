# Goal

Continue ATS project documentation.

Completed:

✅ `00_Project_Vision.md`
✅ `01_Tech_Stack.md`
✅ `02_System_Architecture.md`

Now we start:

```text
docs/03_Development_Guide.md
```

Purpose:

Define the development process before writing application code.

This document explains:

* How developers set up ATS.
* How environments are created.
* How code is organized.
* How changes are tested.
* How development follows the architecture.

Main principle:

> Build a clean development foundation before building trading functionality.

---

# Chapter 1 — Development Environment Overview

---

# 1.1 Development Philosophy

ATS development follows these principles:

## Documentation Before Implementation

Architecture decisions are documented before coding.

---

## Small Steps

Development is divided into small milestones.

Example:

```text
Setup Environment

↓

Create Backend Foundation

↓

Create Database Connection

↓

Create API Structure

↓

Build Trading Modules
```

---

## Production Mindset

Even during development:

* Write clean code.
* Follow architecture.
* Test changes.
* Avoid shortcuts.

---

# 1.2 Development Environment Architecture

Developer machine:

```text
Developer Computer

↓

Git Repository

↓

Aegis-Trading-System

├── backend

├── frontend

├── docs

├── docker

└── scripts
```

---

# 1.3 Required Development Tools

ATS development requires:

## Code Editor

Recommended:

* Visual Studio Code

Purpose:

* Code editing.
* Extensions.
* Terminal access.

---

## Version Control

Tool:

```text
Git
```

Purpose:

* Track changes.
* Manage versions.
* Collaborate.

Repository:

```text
GitHub
```

---

## Backend Tools

Required:

```text
Python

FastAPI

SQLAlchemy

Alembic
```

---

## Frontend Tools

Required:

```text
Node.js

npm

React

Vite
```

---

## Database Tools

Required:

```text
PostgreSQL
```

---

## Container Tools

Required:

```text
Docker

Docker Compose
```

---

# 1.4 Development Environment Structure

Final local setup:

```text
Developer Machine

│

├── Backend Environment

│   ├── Python

│   ├── FastAPI

│   └── Trading Modules


├── Frontend Environment

│   ├── Node.js

│   ├── React

│   └── Vite


├── Database Environment

│   └── PostgreSQL


└── Docker Environment

    └── Service Containers
```

---

# 1.5 Development Modes

ATS has three main modes.

---

# Development Mode

Purpose:

Building new features.

Configuration:

```text
LIVE_TRADING=false
PAPER_TRADING=true
```

---

# Testing Mode

Purpose:

Automated testing.

Configuration:

```text
TEST_DATABASE=true
BROKER_SIMULATION=true
```

---

# Production Mode

Purpose:

Real operation.

Configuration:

```text
LIVE_TRADING=true
```

---

# 1.6 Environment Separation

Development and production must never share:

* Database.
* API keys.
* Broker credentials.
* Configuration files.

Example:

Wrong:

```text
Development

↓

Production Database
```

---

Correct:

```text
Development

↓

Development Database


Production

↓

Production Database
```

---

# 1.7 Project Setup Workflow

New developer setup:

```text
Install Tools

↓

Clone Repository

↓

Configure Environment

↓

Install Backend

↓

Install Frontend

↓

Setup Database

↓

Run Application

↓

Verify System
```

---

# 1.8 Development Folder Responsibility

Current structure:

```text
Aegis-Trading-System/

backend/

frontend/

docs/

prompts/

scripts/

docker/

.github/
```

---

## backend/

Contains:

* FastAPI application.
* Trading logic.
* Database layer.
* Workers.

---

## frontend/

Contains:

* React dashboard.
* User interface.

---

## docs/

Contains:

* Architecture.
* Development rules.
* Project decisions.

---

## prompts/

Contains:

* AI project instructions.
* Project context.

---

## scripts/

Contains:

* Setup scripts.
* Automation scripts.

---

## docker/

Contains:

* Container configuration.

---

## .github/

Contains:

* GitHub workflows.
* Repository automation.

---

# 1.9 Development Rules

Every developer must follow:

## Rule 1

Never directly modify production data.

---

## Rule 2

Create changes in development first.

---

## Rule 3

Test before merging.

---

## Rule 4

Update documentation when architecture changes.

---

## Rule 5

Keep commits meaningful.

Example:

Good:

```text
Add market data validation module
```

Bad:

```text
Update files
```

---

# 1.10 First Development Milestone

Before writing trading code:

Complete:

```text
Phase 1

Development Foundation
```

Tasks:

1. Install required software.
2. Create Python environment.
3. Setup backend project.
4. Setup frontend project.
5. Setup PostgreSQL.
6. Setup Docker.
7. Verify communication.

---

# Chapter 1 Summary

Development foundation defines:

| Area         | Purpose                |
| ------------ | ---------------------- |
| Tools        | Required software      |
| Environments | Safe separation        |
| Folder Rules | Organization           |
| Workflow     | Consistent development |
| Rules        | Maintain quality       |

---

# Documentation Update

Create:

```text
docs/03_Development_Guide.md
```

Add:

```text
Chapter 1 - Development Environment Overview
```

Status:

✅ Completed

---

# Next Step

Continue:

```text
03_Development_Guide.md

Chapter 2 - Local Machine Setup
```

Chapter 2 will define exact setup:

* Windows/Linux requirements.
* Python installation.
* Node.js installation.
* Git setup.
* VS Code setup.
* Required extensions.

I have loaded the current ATS project context. We are continuing from:

**Current Phase:** Phase 0 – Project Foundation
**Current Document:** `03_Development_Guide.md`
**Completed:** Chapter 1 – Development Environment Overview
**Next:** Chapter 2 – Local Machine Setup

I will follow the existing architecture and MASTER_PROMPT rules.

## 03_Development_Guide.md

# Chapter 2 - Local Machine Setup

## 2.1 Purpose

The purpose of this chapter is to define the standard local development environment required to build and test the Aegis Trading System (ATS).

A consistent development environment reduces setup problems, improves teamwork, and ensures the project behaves the same on different machines.

The local environment will contain:

* Source code management
* Backend development environment
* Frontend development environment
* Database environment
* Required development tools

---

# 2.2 Development Machine Requirements

## Minimum Hardware Requirements

Recommended:

* CPU: 4 cores or higher
* RAM: 16 GB minimum
* Storage: 50 GB free space
* Operating System:

  * Windows 11
  * Linux
  * macOS

Recommended for long-term development:

* CPU: 8 cores+
* RAM: 32 GB
* SSD storage

Reason:

ATS will process:

* Market data
* Indicator calculations
* Strategy evaluation
* Database operations
* WebSocket communication

A stronger development machine improves testing speed and debugging.

---

# 2.3 Required Software Installation

The following software must be installed before development begins.

---

## Git

Purpose:

Git manages source code versions and tracks project changes.

Required for:

* Version control
* Branch management
* GitHub integration

Verification:

```bash
git --version
```

Expected output:

```
git version x.x.x
```

---

## Python

Purpose:

Python is used for backend development.

ATS backend uses:

* FastAPI
* SQLAlchemy
* Alembic
* Trading engine modules

Required version:

Python 3.12+

Verification:

```bash
python --version
```

Expected:

```
Python 3.12.x
```

---

## Node.js

Purpose:

Node.js is required for frontend development.

Used for:

* React development server
* Package management
* Frontend build process

Required:

Node.js LTS version

Verification:

```bash
node --version
```

and

```bash
npm --version
```

---

## PostgreSQL

Purpose:

PostgreSQL is the production database system.

ATS uses PostgreSQL for:

* Market data storage
* Trading records
* User settings
* System logs

Verification:

```bash
psql --version
```

---

## Docker

Purpose:

Docker provides consistent environments.

Future usage:

* PostgreSQL container
* Backend container
* Frontend container
* Production deployment

Verification:

```bash
docker --version
```

---

# 2.4 Project Directory Setup

The project must use the official structure:

```
Aegis-Trading-System/

backend/

frontend/

docs/

prompts/

scripts/

docker/

.github/
```

The root folder is the main project workspace.

All development commands should be executed from this location.

---

# 2.5 Backend Environment Setup

The backend uses a Python virtual environment.

Purpose:

A virtual environment separates ATS dependencies from other Python projects.

Navigate:

```bash
cd backend
```

Create environment:

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

After activation:

Terminal should show:

```
(venv)
```

---

# 2.6 Backend Dependency Management

Backend dependencies will be managed using:

```
requirements.txt
```

Example future structure:

```
backend/

├── app/
├── requirements.txt
├── alembic.ini
└── venv/
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Update dependencies:

```bash
pip freeze > requirements.txt
```

---

# 2.7 Frontend Environment Setup

Navigate:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Run development server:

```bash
npm run dev
```

Frontend will communicate with backend through:

* REST API
* WebSocket connection

---

# 2.8 Environment Configuration

Sensitive information must never be stored directly in source code.

Examples:

* Database password
* API keys
* Broker credentials
* Secret keys

Configuration will use environment variables.

Example:

```
.env
```

Future structure:

```
backend/

.env

DATABASE_URL=
BROKER_API_KEY=
SECRET_KEY=
```

Rules:

* `.env` files are not committed to GitHub.
* `.env.example` files document required variables.

---

# 2.9 Local Database Setup

Development database:

PostgreSQL

Example:

```
Database:
ats_development

User:
ats_user
```

Database responsibilities:

Store:

* Market candles
* Indicators
* Strategy decisions
* Orders
* Trades
* System logs

Database schema will be created later during:

Phase 2 - Database Design

---

# 2.10 Development Verification Checklist

Before starting development, verify:

## Git

✅ Git installed

## Python

✅ Python installed
✅ Virtual environment works

## Node.js

✅ Node installed
✅ npm works

## PostgreSQL

✅ Database server running

## Docker

✅ Docker installed

## Project

✅ Repository cloned
✅ Folder structure exists

---

# 2.11 Testing Environment Rule

Development and production environments must remain separate.

Development:

```
Local Machine
↓
Testing Database
↓
Paper Trading
```

Production:

```
Cloud Server
↓
Production Database
↓
Live Trading
```

Live trading must never run from a developer machine.

---

# Chapter Summary

After completing this chapter:

The developer should have:

* Required software installed
* ATS repository ready
* Backend environment prepared
* Frontend environment prepared
* Database environment prepared

No trading logic is created in this phase.

This chapter only prepares the foundation for future development.

---

## Next Chapter

**Chapter 3 - Project Repository Structure and Git Workflow**

---

Update `CURRENT_STATUS.md` after adding this chapter:

```
03_Development_Guide.md

Completed:
Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup

Next:
Chapter 3 - Project Repository Structure and Git Workflow
```

Continue `03_Development_Guide.md`

# Chapter 3 - Project Repository Structure and Git Workflow

---

# 3.1 Purpose

The purpose of this chapter is to define how the Aegis Trading System (ATS) source code is organized and how Git is used during development.

A clear repository structure helps:

* Developers find code quickly.
* Prevent modules from becoming mixed.
* Maintain clean architecture.
* Support future team development.
* Reduce accidental changes.

Git workflow ensures:

* Every change is tracked.
* Features can be developed safely.
* Problems can be reverted.
* Production code remains stable.

---

# 3.2 Repository Overview

The ATS repository follows this structure:

```
Aegis-Trading-System/

├── backend/
│
├── frontend/
│
├── docs/
│
├── prompts/
│
├── scripts/
│
├── docker/
│
├── .github/
│
├── README.md
│
└── .gitignore
```

Each folder has one responsibility.

---

# 3.3 Root Directory Responsibilities

## backend/

Purpose:

Contains all server-side application code.

Responsible for:

* Market data processing
* Indicator calculations
* Strategy engine
* Risk management
* Trade execution
* Database operations
* API services
* Background workers

Business logic exists only here.

---

## frontend/

Purpose:

Contains the user interface.

Responsible for:

* Dashboard
* Charts
* Settings pages
* User interactions
* Displaying trading information

Frontend communicates with backend using:

* REST API
* WebSocket

Frontend does not contain trading decisions.

---

## docs/

Purpose:

Contains all project documentation.

Examples:

```
docs/

├── 00_Project_Vision.md

├── 01_Tech_Stack.md

├── 02_System_Architecture.md

├── 03_Development_Guide.md
```

Documentation must be updated before major implementation.

---

## prompts/

Purpose:

Contains AI collaboration instructions and project context.

Example:

```
prompts/

├── PROJECT_CONTEXT.md

└── MASTER_PROMPT.md
```

These files ensure AI assistance follows ATS architecture rules.

---

## scripts/

Purpose:

Contains utility scripts.

Examples:

* Database backup scripts
* Data import scripts
* Testing scripts
* Maintenance scripts

Scripts must not contain core business logic.

---

## docker/

Purpose:

Contains Docker configuration.

Future contents:

```
docker/

├── backend/

├── frontend/

└── postgres/
```

Used for:

* Local development
* Testing
* Deployment preparation

---

## .github/

Purpose:

Contains GitHub configuration.

Future usage:

```
.github/

├── workflows/

└── pull_request_template.md
```

Used for:

* Automated testing
* Code checks
* CI/CD pipelines

---

# 3.4 Backend Internal Structure

The backend follows responsibility-based organization.

Current planned structure:

```
backend/

└── app/

    ├── api/

    ├── core/

    ├── market/

    ├── indicators/

    ├── strategy/

    ├── risk/

    ├── execution/

    ├── database/

    ├── workers/

    └── main.py
```

---

# api/

Responsibility:

Handles communication with frontend and external systems.

Contains:

* REST API routes
* WebSocket endpoints
* Request validation

Does not contain:

* Trading calculations
* Strategy decisions

---

# core/

Responsibility:

Contains application-wide configuration.

Examples:

* Settings
* Environment variables
* Security configuration
* Application startup logic

---

# market/

Responsibility:

Handles market-related operations.

Examples:

* Broker connection
* Market data collection
* Candle management
* Market sessions

---

# indicators/

Responsibility:

Calculates technical indicators.

Examples:

* Moving averages
* RSI
* ATR
* Volume analysis

Indicators only provide data.

They do not make trading decisions.

---

# strategy/

Responsibility:

Contains trading decision logic.

Examples:

* Market bias
* Trend health
* Entry confirmation
* Entry timing
* Exit decisions

---

# risk/

Responsibility:

Protects trading capital.

Examples:

* Position sizing
* Stop loss calculation
* Risk limits
* Exposure control

---

# execution/

Responsibility:

Handles order management.

Examples:

* Order creation
* Broker communication
* Trade tracking

---

# database/

Responsibility:

Handles data persistence.

Examples:

* Database models
* Migrations
* Repository functions

Uses:

* PostgreSQL
* SQLAlchemy
* Alembic

---

# workers/

Responsibility:

Handles background tasks.

Examples:

* Market data updates
* Strategy evaluation loops
* Scheduled tasks

---

# 3.5 Git Branch Strategy

ATS uses a simple professional Git workflow.

Main branches:

```
main

develop
```

---

# main Branch

Purpose:

Production-ready code.

Rules:

* Stable code only.
* No direct development.
* Used for releases.

---

# develop Branch

Purpose:

Main development branch.

Contains:

* Completed features
* Testing changes
* Integration work

---

# Feature Branches

Every new feature uses a separate branch.

Naming:

```
feature/feature-name
```

Examples:

```
feature/database-models

feature/market-data-service

feature/risk-engine
```

---

# Bug Fix Branches

Naming:

```
fix/problem-name
```

Examples:

```
fix/api-timeout

fix/database-connection
```

---

# Documentation Branches

Naming:

```
docs/document-name
```

Example:

```
docs/update-development-guide
```

---

# 3.6 Commit Rules

Commits should describe one clear change.

Good examples:

```
Add market session database model

Create risk calculation service

Update system architecture documentation
```

Bad examples:

```
Update files

Changes

Fix stuff
```

---

# 3.7 Pull Request Rules

Before merging:

Required:

* Code review
* Testing completed
* Documentation updated if needed

Check:

* Does it follow architecture?
* Does it introduce duplicate logic?
* Does it affect existing modules?

---

# 3.8 Git Ignore Rules

Sensitive and unnecessary files must not enter Git.

Examples:

```
.env

venv/

node_modules/

__pycache__/

*.log
```

Reason:

Protect secrets and keep repository clean.

---

# 3.9 Development Workflow

Standard workflow:

```
1. Update documentation

        ↓

2. Create feature branch

        ↓

3. Develop feature

        ↓

4. Test locally

        ↓

5. Commit changes

        ↓

6. Create pull request

        ↓

7. Review

        ↓

8. Merge
```

---

# 3.10 Repository Rules

Never:

* Put backend logic in frontend.
* Put strategy code inside API routes.
* Put database code inside strategy modules.
* Commit passwords or API keys.
* Directly edit production code without review.

Always:

* Keep modules independent.
* Follow one responsibility per module.
* Update documentation before large changes.

---

# Chapter Summary

After completing this chapter:

The developer understands:

* ATS repository structure.
* Purpose of each folder.
* Backend module responsibilities.
* Git branching workflow.
* Commit standards.
* Development process.

This creates a clean foundation before writing application code.

---

# Next Chapter

**Chapter 4 - Backend Development Environment Setup**

---

Update `CURRENT_STATUS.md`:

```
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow

Next:

Chapter 4 - Backend Development Environment Setup
```

Continue `03_Development_Guide.md`

# Chapter 4 - Backend Development Environment Setup

---

# 4.1 Purpose

The purpose of this chapter is to define the standard backend development environment for the Aegis Trading System (ATS).

The backend is the core of ATS.

It controls:

* Market data
* Indicator calculations
* Strategy decisions
* Risk management
* Trade execution
* Database communication
* WebSocket communication

The backend must be reliable, organized, and separated from the frontend.

---

# 4.2 Backend Technology Stack

ATS backend uses:

| Component            | Technology |
| -------------------- | ---------- |
| Programming Language | Python     |
| Web Framework        | FastAPI    |
| ORM                  | SQLAlchemy |
| Migration Tool       | Alembic    |
| Database             | PostgreSQL |
| Validation           | Pydantic   |
| Server               | Uvicorn    |
| Testing              | Pytest     |

---

# 4.3 Backend Folder Structure

The backend follows this structure:

```text
backend/

├── app/

│   ├── api/

│   ├── core/

│   ├── market/

│   ├── indicators/

│   ├── strategy/

│   ├── risk/

│   ├── execution/

│   ├── database/

│   ├── workers/

│   │
│   └── main.py

│
├── tests/

├── alembic/

├── requirements.txt

├── .env

├── .env.example

└── README.md
```

---

# 4.4 Create Python Virtual Environment

Purpose:

A virtual environment isolates ATS dependencies from other Python projects.

Navigate to backend:

```bash
cd backend
```

Create environment:

```bash
python -m venv venv
```

Activate environment.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Successful activation:

```text
(venv)
```

---

# 4.5 Install Backend Dependencies

Create:

```text
requirements.txt
```

The file contains all required backend packages.

Initial packages:

```text
fastapi
uvicorn
sqlalchemy
alembic
psycopg2-binary
pydantic-settings
python-dotenv
pytest
```

Install:

```bash
pip install -r requirements.txt
```

---

# 4.6 Dependency Responsibilities

## FastAPI

Purpose:

Provides backend API services.

Used for:

* REST endpoints
* WebSocket endpoints
* Request handling

---

## Uvicorn

Purpose:

Runs the FastAPI application.

Example:

```bash
uvicorn app.main:app --reload
```

---

## SQLAlchemy

Purpose:

Database communication layer.

Used for:

* Database models
* Queries
* Relationships

---

## Alembic

Purpose:

Database migration management.

Used for:

* Creating tables
* Updating schemas
* Tracking database changes

---

## PostgreSQL Driver

Purpose:

Allows Python to communicate with PostgreSQL.

---

## Pydantic

Purpose:

Data validation.

Used for:

* API request models
* Configuration validation

---

## Pytest

Purpose:

Automated testing.

Used for:

* Unit tests
* Module testing
* Regression testing

---

# 4.7 Environment Configuration

ATS must not store sensitive configuration inside code.

Configuration uses:

```text
.env
```

Example:

```env
DATABASE_URL=postgresql://user:password@localhost/ats
APP_ENV=development
```

---

# 4.8 Environment File Rules

Required files:

```text
.env

.env.example
```

Purpose:

`.env`

Contains real local values.

Example:

```text
DATABASE_URL=real_connection
```

---

`.env.example`

Contains only examples.

Example:

```text
DATABASE_URL=
APP_ENV=
```

---

Rules:

Never:

* Commit `.env`
* Store API keys in code
* Store broker credentials in GitHub

---

# 4.9 Application Entry Point

The backend starts from:

```text
app/main.py
```

Responsibility:

Only application startup.

It should handle:

* FastAPI initialization
* Router registration
* Application lifecycle

It should not contain:

* Strategy logic
* Indicator calculations
* Database queries

---

Example future structure:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Aegis Trading System"
)
```

---

# 4.10 Backend Module Communication

ATS follows controlled communication flow.

Example:

```text
Market Data

      ↓

Indicators

      ↓

Strategy Engine

      ↓

Risk Management

      ↓

Execution Engine

      ↓

Database
```

Each module has one responsibility.

---

# 4.11 Backend Development Rules

## Rule 1

Business logic stays inside backend.

Example:

Correct:

```text
strategy/
    confidence_engine.py
```

Incorrect:

```text
frontend/
    calculate_signal.js
```

---

## Rule 2

Modules communicate through defined interfaces.

Avoid:

* Direct file-to-file dependency
* Circular imports
* Duplicate calculations

---

## Rule 3

Every module must be testable independently.

Example:

Indicator module:

Input:

```text
Candle data
```

Output:

```text
ATR value
```

Strategy module:

Input:

```text
Market state
```

Output:

```text
Trading decision
```

---

# 4.12 Running Backend Locally

Start virtual environment:

```bash
venv\Scripts\activate
```

Run application:

```bash
uvicorn app.main:app --reload
```

Expected:

```text
Application startup complete
```

API documentation:

```text
/api/docs
```

FastAPI automatically provides interactive API testing.

---

# 4.13 Backend Testing

Run tests:

```bash
pytest
```

Testing priorities:

1. Database connection
2. API endpoints
3. Indicator calculations
4. Strategy decisions
5. Risk calculations

---

# 4.14 Backend Development Checklist

Before backend development begins:

## Python

✅ Python installed
✅ Virtual environment created

## Dependencies

✅ requirements.txt created
✅ Packages installed

## Configuration

✅ .env created
✅ .env.example created

## Application

✅ FastAPI starts successfully

## Database

✅ PostgreSQL connection prepared

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Backend technology stack.
* Python environment setup.
* Dependency management.
* Configuration handling.
* Application startup flow.
* Backend module responsibilities.
* Testing approach.

The backend foundation is now ready for actual implementation.

---

# Next Chapter

**Chapter 5 - Frontend Development Environment Setup**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup

Next:

Chapter 5 - Frontend Development Environment Setup
```

Continue `03_Development_Guide.md`

# Chapter 5 - Frontend Development Environment Setup

---

# 5.1 Purpose

The purpose of this chapter is to define the standard frontend development environment for the Aegis Trading System (ATS).

The frontend provides the user interface for monitoring and controlling the trading system.

The frontend is responsible for:

* Displaying market information
* Showing strategy decisions
* Displaying risk information
* Managing user settings
* Receiving real-time updates

The frontend is **not responsible** for trading intelligence.

---

# 5.2 Frontend Technology Stack

ATS frontend uses:

| Component               | Technology   |
| ----------------------- | ------------ |
| Framework               | React        |
| Language                | JavaScript   |
| Build Tool              | Vite         |
| Styling                 | Tailwind CSS |
| API Communication       | Axios        |
| Real-Time Communication | WebSocket    |
| Package Manager         | npm          |

---

# 5.3 Frontend Architecture Principle

The frontend follows a presentation-based architecture.

Flow:

```text
Backend

    ↓

REST API / WebSocket

    ↓

Frontend

    ↓

User Interface
```

The frontend receives prepared information from the backend.

---

# 5.4 Frontend Responsibilities

Frontend handles:

## User Interface

Examples:

* Dashboard
* Charts
* Tables
* Settings pages

---

## User Interaction

Examples:

* Changing trading settings
* Selecting timeframe
* Starting/stopping paper trading

---

## Data Display

Examples:

* Current market price
* Active trades
* Strategy status
* Risk information

---

## Communication

Frontend communicates through:

* REST API
* WebSocket

---

# 5.5 Frontend Restrictions

The frontend must never calculate:

* Technical indicators
* Market bias
* Trend health
* Confidence scores
* Entry signals
* Exit signals
* Risk calculations

Example:

Incorrect:

```javascript
calculateRSI(priceData)
```

Correct:

```javascript
displayRSI(indicatorValue)
```

The backend owns all trading intelligence.

---

# 5.6 Frontend Folder Structure

The planned structure:

```text
frontend/

├── src/

│   ├── api/

│   ├── components/

│   ├── pages/

│   ├── hooks/

│   ├── websocket/

│   ├── utils/

│   ├── assets/

│   ├── App.jsx

│   └── main.jsx

│
├── public/

├── package.json

├── vite.config.js

└── README.md
```

---

# 5.7 Folder Responsibilities

## src/

Contains all frontend application code.

---

## api/

Purpose:

Handles backend API communication.

Examples:

```text
api/

├── marketApi.js

├── tradeApi.js

└── settingsApi.js
```

Responsibilities:

* Sending requests
* Receiving responses

Does not contain:

* Trading calculations

---

## components/

Purpose:

Reusable UI components.

Examples:

* Charts
* Cards
* Tables
* Buttons

---

## pages/

Purpose:

Complete application screens.

Examples:

```text
pages/

├── Dashboard.jsx

├── Trading.jsx

└── Settings.jsx
```

---

## hooks/

Purpose:

Reusable React logic.

Examples:

* Data fetching hooks
* UI state management

---

## websocket/

Purpose:

Handles real-time backend communication.

Examples:

* Price updates
* Trade updates
* System notifications

---

## utils/

Purpose:

General frontend helper functions.

Examples:

* Formatting dates
* Formatting numbers

Never contains strategy calculations.

---

# 5.8 Create React Application

Navigate:

```bash
cd frontend
```

Create React project:

```bash
npm create vite@latest .
```

Select:

```text
Framework:
React

Variant:
JavaScript
```

---

# 5.9 Install Dependencies

Install project packages:

```bash
npm install
```

Install Axios:

```bash
npm install axios
```

---

# 5.10 Install Tailwind CSS

Purpose:

Tailwind provides a consistent styling system.

Installation will be completed during frontend implementation phase.

Reason:

The current phase only prepares the development environment.

---

# 5.11 Running Frontend Locally

Start development server:

```bash
npm run dev
```

Expected:

```text
VITE ready

Local:
http://localhost:5173
```

---

# 5.12 Frontend Environment Configuration

Frontend also uses environment variables.

Example:

```text
.env
```

Example:

```env
VITE_API_URL=http://localhost:8000
```

Purpose:

Allows different environments:

Development:

```text
localhost
```

Production:

```text
cloud server
```

---

# 5.13 API Communication

Frontend communicates with backend using Axios.

Example flow:

```text
User opens dashboard

        ↓

React requests data

        ↓

FastAPI API endpoint

        ↓

Backend returns data

        ↓

React displays information
```

---

# 5.14 WebSocket Communication

Purpose:

Provide real-time updates.

Examples:

* Live market price
* Trade status
* Strategy events

Flow:

```text
Backend WebSocket

        ↓

Frontend WebSocket Client

        ↓

React Component Update
```

---

# 5.15 Frontend State Management

Initial approach:

Use React built-in state management.

Examples:

* useState
* useEffect
* Context API

Additional state libraries will only be added if required.

Reason:

Avoid unnecessary complexity.

---

# 5.16 Frontend Development Rules

Always:

* Keep components reusable.
* Keep API calls separated.
* Keep UI simple.
* Follow backend data contracts.

Never:

* Add trading logic.
* Duplicate backend calculations.
* Store sensitive credentials.
* Directly access the database.

---

# 5.17 Frontend Testing

Testing priorities:

## Component Testing

Check:

* UI rendering
* User interaction

---

## API Testing

Check:

* Backend communication
* Error handling

---

## Real-Time Testing

Check:

* WebSocket connection
* Live updates

---

# 5.18 Frontend Development Checklist

Before frontend development begins:

## Node.js

✅ Node installed
✅ npm works

## Project

✅ React project created
✅ Vite configured

## Communication

✅ Backend API plan understood
✅ WebSocket architecture understood

## Rules

✅ No business logic in frontend

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Frontend technology stack.
* React project structure.
* API communication.
* WebSocket communication.
* Frontend limitations.
* Testing approach.

The frontend foundation is ready for future dashboard development.

---

# Next Chapter

**Chapter 6 - Database Development Environment Setup**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup

Next:

Chapter 6 - Database Development Environment Setup
```

Continue `03_Development_Guide.md`

# Chapter 6 - Database Development Environment Setup

---

# 6.1 Purpose

The purpose of this chapter is to define the database development environment for the Aegis Trading System (ATS).

The database is a critical part of ATS because it stores:

* Market data
* Trading decisions
* Risk information
* Orders
* Executions
* System history
* Configuration data

The database design must prioritize:

* Reliability
* Data integrity
* Scalability
* Performance
* Long-term maintenance

---

# 6.2 Database Technology Stack

ATS uses:

| Component             | Technology |
| --------------------- | ---------- |
| Database              | PostgreSQL |
| ORM                   | SQLAlchemy |
| Migration Tool        | Alembic    |
| Development Container | Docker     |
| Production Database   | PostgreSQL |

---

# 6.3 Database Architecture Principle

The database follows a structured data ownership model.

Flow:

```text
Market Data

    ↓

Database

    ↓

Backend Services

    ↓

Frontend Display
```

The frontend never connects directly to the database.

---

# 6.4 Database Responsibilities

The database stores:

## Market Data

Examples:

* OHLC candles
* Volume
* Timeframes
* Market sessions

---

## Indicator Data

Examples:

* ATR values
* Moving averages
* RSI values
* Calculated market conditions

---

## Strategy Data

Examples:

* Market bias
* Trend health
* Entry confirmation
* Confidence scores
* Trading decisions

---

## Risk Data

Examples:

* Position size
* Stop loss levels
* Risk calculations

---

## Trading Data

Examples:

* Orders
* Positions
* Trades
* Execution records

---

## System Data

Examples:

* User settings
* Application configuration
* Logs

---

# 6.5 PostgreSQL Installation

Development can use either:

Option 1:

Local PostgreSQL installation

or

Option 2:

Docker PostgreSQL container

ATS prefers Docker for consistency.

---

# 6.6 PostgreSQL Using Docker

Purpose:

Create a consistent database environment.

Example future structure:

```text
docker/

└── postgres/

    └── docker-compose.yml
```

Example service:

```yaml
services:

  postgres:

    image: postgres

    environment:

      POSTGRES_DB: ats_development

      POSTGRES_USER: ats_user

      POSTGRES_PASSWORD: password

    ports:

      - "5432:5432"
```

---

# 6.7 Starting Database Container

Start PostgreSQL:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

Expected:

```text
postgres container running
```

---

# 6.8 Database Connection

Backend connects using:

```text
DATABASE_URL
```

Example:

```env
DATABASE_URL=postgresql://ats_user:password@localhost:5432/ats_development
```

The actual value is stored only in:

```text
.env
```

---

# 6.9 SQLAlchemy Setup

Purpose:

SQLAlchemy provides communication between Python and PostgreSQL.

Architecture:

```text
Python Models

      ↓

SQLAlchemy ORM

      ↓

PostgreSQL Tables
```

---

Example future structure:

```text
backend/

app/

└── database/

    ├── connection.py

    ├── models.py

    └── repository.py
```

---

# 6.10 Database Module Responsibilities

## connection.py

Responsible for:

* Database connection
* Session creation
* Engine configuration

---

## models.py

Responsible for:

* Table definitions
* Relationships

Example:

Future models:

* Candle
* Trade
* Order
* Position

---

## repository.py

Responsible for:

* Database queries
* Data access functions

---

# 6.11 Alembic Migration Setup

Purpose:

Alembic manages database structure changes.

Example:

Without migration:

```
Developer changes database manually
↓
Different environments become different
```

With migration:

```
Create migration file
↓
Review change
↓
Apply migration
↓
All environments match
```

---

# 6.12 Migration Workflow

Standard workflow:

```text
Modify SQLAlchemy Model

        ↓

Create Migration

        ↓

Review Migration

        ↓

Apply Migration

        ↓

Database Updated
```

---

# 6.13 Alembic Commands

Initialize:

```bash
alembic init alembic
```

Create migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migration:

```bash
alembic upgrade head
```

Check current version:

```bash
alembic current
```

---

# 6.14 Database Design Rules

ATS database follows these rules:

---

## Rule 1

Never modify production database manually.

All changes use migrations.

---

## Rule 2

Every table must have:

* Primary key
* Created timestamp
* Updated timestamp when required

---

## Rule 3

Historical trading data should never be deleted without a defined policy.

Reason:

Trading analysis requires historical records.

---

## Rule 4

Database tables should represent business concepts.

Example:

Good:

```text
trades
orders
candles
positions
```

Bad:

```text
table1
data_backup2
temp_values
```

---

# 6.15 Database Naming Convention

Tables:

Use plural lowercase names.

Examples:

```text
candles

orders

trades

positions
```

Columns:

Use snake_case.

Examples:

```text
created_at

entry_price

stop_loss
```

---

# 6.16 Development Database Rules

Development database:

Purpose:

* Testing
* Development
* Experiments

Never:

* Connect development code to live trading database.
* Store real credentials locally.
* Test dangerous execution logic with live accounts.

---

# 6.17 Database Testing

Testing includes:

## Connection Test

Verify:

* Backend can connect.
* Credentials work.

---

## Migration Test

Verify:

* Migration runs successfully.
* Database structure matches models.

---

## Data Test

Verify:

* Insert works.
* Query works.
* Relationships work.

---

# 6.18 Database Backup Planning

Future production system requires:

* Automated backups
* Recovery testing
* Database monitoring

Important data:

* Trade history
* Execution records
* Strategy decisions
* Market data

---

# 6.19 Database Development Checklist

Before database implementation:

## PostgreSQL

✅ PostgreSQL available
✅ Database container plan ready

## Backend

✅ SQLAlchemy planned
✅ Alembic planned

## Security

✅ Environment variables planned
✅ No credentials in code

## Architecture

✅ Database responsibilities defined

---

# Chapter Summary

After completing this chapter:

The developer understands:

* PostgreSQL role in ATS.
* Database environment setup.
* SQLAlchemy structure.
* Alembic migration workflow.
* Database rules.
* Testing approach.

The database foundation is prepared for future schema design.

---

# Next Chapter

**Chapter 7 - Docker Development Environment Setup**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup

Next:

Chapter 7 - Docker Development Environment Setup
```

Continue `03_Development_Guide.md`

# Chapter 7 - Docker Development Environment Setup

---

# 7.1 Purpose

The purpose of this chapter is to define how Docker will be used in the Aegis Trading System (ATS) development environment.

Docker provides a consistent environment where ATS services can run independently.

Docker helps with:

* Environment consistency
* Easier setup
* Service isolation
* Future deployment preparation
* Reducing "works on my machine" problems

---

# 7.2 Docker Role in ATS

Docker is not responsible for trading logic.

Docker only manages application environments.

ATS uses Docker for:

* PostgreSQL database
* Backend service
* Frontend service
* Future supporting services

---

# 7.3 Docker Architecture

ATS container architecture:

```text
 id="dockerflow"
                Aegis Trading System

                       |

        ---------------------------------

        |               |               |

    Frontend        Backend        PostgreSQL

     React          FastAPI        Database

        |               |               |

        ---------------------------------

                    Docker Network
```

Each service runs independently.

---

# 7.4 Docker Components

## Docker Image

Purpose:

A blueprint used to create containers.

Example:

```text
Python backend image

PostgreSQL image

Node frontend image
```

---

## Docker Container

Purpose:

A running instance of an image.

Example:

```text
ATS Backend Container

ATS Database Container
```

---

## Docker Network

Purpose:

Allows containers to communicate safely.

Example:

```text
Backend

    ↓

PostgreSQL
```

---

## Docker Volume

Purpose:

Stores persistent data.

Important for:

* PostgreSQL database files
* Logs
* Configuration data

---

# 7.5 Docker Project Structure

The Docker configuration will follow:

```text
Aegis-Trading-System/

├── docker/

│
├── backend/

├── frontend/

├── docker-compose.yml

└── README.md
```

---

# 7.6 Docker Compose

Purpose:

Docker Compose manages multiple containers together.

Instead of starting services individually:

```text
Start database

Start backend

Start frontend
```

Docker Compose starts everything:

```text
docker compose up
```

---

# 7.7 Development Container Architecture

Future development environment:

```text
 id="composeflow"
Docker Compose

        |

        |

--------------------------------

|              |               |

Backend     Frontend       PostgreSQL

FastAPI     React          Database

Port        Port           Port

8000        5173           5432

--------------------------------
```

---

# 7.8 Backend Docker Setup

Purpose:

Create a container for FastAPI.

Responsibilities:

* Install Python
* Install dependencies
* Run backend server

Example future file:

```text
backend/

└── Dockerfile
```

---

Backend container should:

* Start FastAPI application
* Connect to PostgreSQL
* Load environment variables

---

# 7.9 Frontend Docker Setup

Purpose:

Create a container for React application.

Responsibilities:

* Install Node.js
* Install packages
* Run Vite development server

Example future file:

```text
frontend/

└── Dockerfile
```

---

Frontend container should:

* Start React application
* Communicate with backend container

---

# 7.10 PostgreSQL Docker Setup

Purpose:

Provide consistent database environment.

Configuration:

```text
Database:

Name:
ats_development

User:
ats_user

Port:
5432
```

Database storage uses:

```text
Docker Volume
```

Reason:

Container restart should not delete database data.

---

# 7.11 Environment Variables with Docker

Sensitive information must be external.

Example:

```text
.env
```

Contains:

```env
DATABASE_URL=
POSTGRES_PASSWORD=
API_KEYS=
```

Docker loads:

```text
.env

        ↓

Containers
```

---

# 7.12 Docker Network Communication

Inside Docker:

Services communicate using service names.

Example:

Incorrect:

```text
localhost:5432
```

Correct:

```text
postgres:5432
```

Reason:

Containers have their own network.

---

# 7.13 Docker Development Commands

Start all services:

```bash
docker compose up
```

Start in background:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

View running containers:

```bash
docker ps
```

View logs:

```bash
docker compose logs
```

---

# 7.14 Docker Development Workflow

Standard workflow:

```text
Developer changes code

        ↓

Docker rebuild if required

        ↓

Start containers

        ↓

Test application

        ↓

Commit changes
```

---

# 7.15 Docker Rules

Always:

* Keep containers independent.
* Use environment variables.
* Use volumes for persistent data.
* Document container changes.

Never:

* Store passwords in Docker files.
* Put business logic inside containers.
* Modify production containers manually.

---

# 7.16 Docker Testing

Verify:

## Container Status

Check:

```bash
docker ps
```

Expected:

```text
Backend running

Frontend running

PostgreSQL running
```

---

## Backend Connection

Verify:

Backend can communicate with:

* PostgreSQL
* Other services

---

## Database Persistence

Test:

1. Insert data.
2. Restart container.
3. Confirm data remains.

---

# 7.17 Docker Production Preparation

Future production deployment:

```text
Oracle Cloud Server

        ↓

Docker Environment

        ↓

ATS Services

        ↓

PostgreSQL Database
```

Production will require:

* Secure environment variables
* Monitoring
* Backup strategy
* Logging
* Resource limits

---

# 7.18 Docker Development Checklist

Before using Docker:

## Installation

✅ Docker installed
✅ Docker Compose available

## Configuration

✅ Docker structure planned
✅ Environment variables prepared

## Services

✅ Backend container planned
✅ Frontend container planned
✅ Database container planned

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Why ATS uses Docker.
* Docker architecture.
* Container responsibilities.
* Docker Compose workflow.
* Environment handling.
* Future production preparation.

Docker foundation is ready for implementation after application modules are created.

---

# Next Chapter

**Chapter 8 - Development Workflow and Coding Standards**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup

Next:

Chapter 8 - Development Workflow and Coding Standards
```

Continue `03_Development_Guide.md`

# Chapter 8 - Development Workflow and Coding Standards

---

# 8.1 Purpose

The purpose of this chapter is to define the standard development workflow and coding standards for the Aegis Trading System (ATS).

A professional trading platform requires consistent development practices because:

* Trading logic must remain understandable.
* Changes must be traceable.
* Bugs must be easy to locate.
* Future developers must understand the system.

The goal is:

**Clean code → Reliable system → Safer trading decisions**

---

# 8.2 Development Philosophy

ATS follows these principles:

## Accuracy > Speed > Profit

The system is designed to make high-quality decisions while protecting capital.

Development decisions must prioritize:

1. Reliability
2. Maintainability
3. Transparency
4. Scalability
5. Performance

---

# 8.3 Standard Development Process

Every feature follows this workflow:

```text id="devflow01"
Requirement

    ↓

Architecture Review

    ↓

Documentation Update

    ↓

Create Feature Branch

    ↓

Implementation

    ↓

Testing

    ↓

Code Review

    ↓

Merge

    ↓

Documentation Final Update
```

---

# 8.4 Before Writing Code

Before implementation, answer:

## What?

What problem is being solved?

Example:

"Create a market session management module."

---

## Why?

Why does ATS need this?

Example:

"To prevent trading outside allowed exchange hours."

---

## How?

How will it fit into the architecture?

Example:

```text id="archflow01"
Market Module

        ↓

Session Manager

        ↓

Strategy Availability Check
```

---

# 8.5 Feature Development Workflow

## Step 1 - Create Feature Branch

Example:

```bash id="branch01"
git checkout develop

git pull

git checkout -b feature/session-manager
```

---

## Step 2 - Implement Small Changes

Avoid:

* Large uncontrolled changes
* Mixing unrelated features

Prefer:

Small:

```text
Add database model

Add service class

Add API endpoint
```

---

## Step 3 - Test

Before commit:

Check:

* Application starts
* Tests pass
* No errors
* Architecture is respected

---

## Step 4 - Commit

Commit should explain the change.

Good:

```text
Add market session validation service
```

Bad:

```text
Update code
```

---

## Step 5 - Review

Before merging:

Check:

* Is responsibility correct?
* Is code reusable?
* Is documentation updated?

---

# 8.6 Python Coding Standards

ATS backend follows Python best practices.

---

# Naming Rules

Classes:

Use PascalCase.

Example:

```python
class RiskManager:
    pass
```

---

Functions:

Use snake_case.

Example:

```python
def calculate_position_size():
    pass
```

---

Variables:

Use descriptive names.

Good:

```python
entry_price
```

Bad:

```python
ep
```

---

# 8.7 Function Design Rules

Functions should:

* Do one thing.
* Be easy to test.
* Have clear inputs and outputs.

Good:

```python
calculate_atr()
```

Bad:

```python
process_everything()
```

---

# 8.8 Error Handling Rules

Errors must be handled properly.

Example:

Wrong:

```python
try:
    connect()
except:
    pass
```

Reason:

Errors disappear.

---

Correct:

```python
try:
    connect()
except DatabaseError as error:
    log_error(error)
```

---

# 8.9 Logging Standards

ATS requires meaningful logs.

Logs help understand:

* System behavior
* Trading decisions
* Errors
* Performance problems

Example:

Good:

```text
Strategy evaluation completed.
Confidence score: 78
Decision: LONG
```

Bad:

```text
Something happened
```

---

# 8.10 Code Documentation

Comments should explain:

* Why something exists.
* Complex decisions.
* Important business rules.

Avoid comments explaining obvious code.

Bad:

```python
# Add one to number
number += 1
```

Good:

```python
# Prevent duplicate signals during the same candle period
```

---

# 8.11 Backend Coding Rules

Backend modules must follow:

```text id="moduleflow01"
API

↓

Service Layer

↓

Business Logic

↓

Database Layer
```

---

Example:

Correct:

```text
api/

trade_route.py


strategy/

decision_engine.py


database/

trade_repository.py
```

---

Incorrect:

```text
api/

trade_route.py

    contains:

    strategy calculations
    database queries
    risk logic
```

---

# 8.12 Frontend Coding Standards

Frontend follows:

## Component Responsibility

One component:

One purpose.

Example:

Good:

```text
PriceChart.jsx

TradeTable.jsx

RiskCard.jsx
```

---

Avoid:

```text
DashboardEverything.jsx
```

---

# 8.13 Frontend Data Rules

Frontend displays backend data.

Example:

Backend sends:

```json
{
"confidence":85,
"signal":"LONG"
}
```

Frontend displays:

```text
Confidence: 85%

Signal: LONG
```

Frontend does not calculate:

```javascript
confidence = calculateSomething()
```

---

# 8.14 Database Coding Standards

Database changes require:

1. Model update
2. Migration creation
3. Migration review
4. Testing

Never:

* Modify production manually.
* Delete historical trading records without approval.

---

# 8.15 Testing Standards

Every important module requires testing.

---

## Unit Testing

Tests individual functions.

Example:

```text
ATR calculation test
Risk calculation test
```

---

## Integration Testing

Tests modules together.

Example:

```text
Market Data

↓

Strategy Engine

↓

Risk Module
```

---

## API Testing

Tests:

* Endpoints
* Validation
* Responses

---

# 8.16 Code Review Checklist

Before merging:

## Architecture

✅ Correct module location

✅ No responsibility mixing

---

## Quality

✅ Clean code

✅ Error handling

✅ Tests included

---

## Security

✅ No secrets committed

✅ No unsafe configuration

---

## Documentation

✅ Documentation updated

---

# 8.17 AI Development Rules

AI assistance must follow ATS architecture.

Before generating code:

Check:

* Project context
* Existing architecture
* Module responsibility

AI should help with:

* Design
* Explanation
* Code generation
* Review

AI should not:

* Create shortcuts
* Break architecture
* Move business logic to frontend

---

# 8.18 Production Quality Rule

Code is considered complete only when:

```text id="complete01"
Implemented

    +

Tested

    +

Reviewed

    +

Documented

    =

Completed Feature
```

---

# Chapter Summary

After completing this chapter:

The developer understands:

* ATS development workflow.
* Branch process.
* Coding standards.
* Testing expectations.
* Review requirements.
* Documentation requirements.

This creates a professional development process before actual feature implementation begins.

---

# Next Chapter

**Chapter 9 - Testing Strategy and Quality Assurance**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards

Next:

Chapter 9 - Testing Strategy and Quality Assurance
```

Continue `03_Development_Guide.md`

# Chapter 9 - Testing Strategy and Quality Assurance

---

# 9.1 Purpose

The purpose of this chapter is to define the testing strategy for the Aegis Trading System (ATS).

A trading system must be reliable because incorrect software behavior can directly affect trading decisions and capital protection.

Testing ensures:

* Features work correctly.
* Trading logic behaves as expected.
* System failures are detected early.
* Future changes do not break existing functionality.

ATS follows the principle:

**A feature is not complete until it is tested.**

---

# 9.2 Testing Philosophy

ATS testing prioritizes:

1. Correctness
2. Reliability
3. Safety
4. Maintainability
5. Performance

The goal is not only to test whether code runs.

The goal is to verify that the system behaves correctly under different market conditions.

---

# 9.3 Testing Levels

ATS uses multiple testing levels:

```text id="testflow01"
Unit Testing

      ↓

Integration Testing

      ↓

API Testing

      ↓

System Testing

      ↓

Paper Trading Testing

      ↓

Production Monitoring
```

Each level checks different risks.

---

# 9.4 Unit Testing

## Purpose

Unit testing verifies individual functions and modules.

A unit should be tested independently.

Examples:

* Indicator calculations
* Risk calculations
* Data processing functions
* Utility functions

---

# 9.5 Backend Unit Testing

Backend tests use:

```text
pytest
```

Example structure:

```text id="unitstruct01"
backend/

├── app/

└── tests/

    ├── test_indicators.py

    ├── test_strategy.py

    ├── test_risk.py

    └── test_market.py
```

---

# 9.6 Indicator Testing

Indicators must be tested with known data.

Example:

Input:

```text id="indicatorinput01"
Historical candle data
```

Expected:

```text id="indicatoroutput01"
Correct ATR value

Correct RSI value

Correct moving average value
```

Purpose:

Prevent incorrect market analysis.

---

# 9.7 Strategy Testing

The strategy engine is one of the most important areas.

Tests should verify:

* Market bias calculation
* Trend health evaluation
* Entry confirmation
* Entry timing
* Exit conditions

Example:

Input:

```text id="strategyinput01"
4H:
Bullish

1H:
Healthy trend

15M:
Confirmation

5M:
Entry signal
```

Expected:

```text id="strategyoutput01"
LONG decision
```

---

# 9.8 Risk Testing

Risk management must be heavily tested.

Examples:

Test:

* Position sizing
* Stop loss calculation
* Maximum exposure
* Risk limits

Example:

Input:

```text id="riskinput01"
Account size:
10000

Risk:
1%

Stop loss:
50 points
```

Expected:

```text id="riskoutput01"
Correct position size
```

---

# 9.9 Integration Testing

## Purpose

Integration testing verifies that modules work together.

Example:

```text id="integration01"
Market Data

      ↓

Indicators

      ↓

Strategy

      ↓

Risk

      ↓

Execution
```

---

# 9.10 Integration Test Examples

## Market Data Flow

Verify:

* Data received
* Candle created
* Indicator updated

---

## Strategy Flow

Verify:

* Market state generated
* Decision created
* Reason recorded

---

## Trade Flow

Verify:

* Signal generated
* Risk checked
* Order created

---

# 9.11 API Testing

## Purpose

Verify communication between frontend and backend.

Tests include:

* Endpoint availability
* Request validation
* Response format
* Error handling

---

Example:

Request:

```json id="api001"
{
"timeframe":"5m"
}
```

Response:

```json id="api002"
{
"signal":"LONG",
"confidence":78
}
```

---

# 9.12 WebSocket Testing

Purpose:

Verify real-time communication.

Test:

* Connection established
* Data received
* Connection recovery
* Error handling

Example:

```text id="ws001"
Backend

 ↓

Price Update

 ↓

Frontend Dashboard
```

---

# 9.13 Database Testing

Database testing verifies:

## Connection

Check:

* Backend connects correctly
* Credentials work

---

## Migration

Check:

* Tables created correctly
* Schema updates work

---

## Data Integrity

Check:

* Records save correctly
* Relationships work
* Historical data remains safe

---

# 9.14 Frontend Testing

Frontend testing focuses on:

* User interface
* User interaction
* Data display

---

Test examples:

## Dashboard

Verify:

* Data loads
* Charts display
* Status updates

---

## Settings

Verify:

* User changes save
* Backend receives updates

---

## Error States

Verify:

* Connection errors display correctly
* Missing data handled properly

---

# 9.15 Trading System Testing

Before live trading, ATS must pass:

```text id="liveflow01"
Development Testing

        ↓

Backtesting

        ↓

Paper Trading

        ↓

Limited Live Testing

        ↓

Full Production
```

---

# 9.16 Backtesting Testing

Purpose:

Evaluate strategy behavior using historical data.

Checks:

* Entry quality
* Exit quality
* Risk behavior
* Drawdown
* Performance stability

Important:

Backtesting results do not guarantee future performance.

---

# 9.17 Paper Trading Testing

Purpose:

Test real-time behavior without risking capital.

Verify:

* Market data handling
* Strategy decisions
* Execution simulation
* Risk controls

Paper trading must be completed before live deployment.

---

# 9.18 Regression Testing

Purpose:

Ensure new changes do not break existing features.

Example:

Adding:

```text id="reg001"
New exit logic
```

Must not break:

```text id="reg002"
Entry logic
Risk calculation
Database records
```

---

# 9.19 Performance Testing

ATS should be tested for:

## Response Time

Examples:

* API response speed
* WebSocket latency

---

## Data Processing

Examples:

* Candle processing speed
* Indicator calculation speed

---

## Database Performance

Examples:

* Query speed
* Data storage growth

---

# 9.20 Error Monitoring

Production system requires monitoring for:

* Application errors
* Database errors
* Connection failures
* Trading execution problems

Logs must provide enough information to understand failures.

---

# 9.21 Testing Rules

Always:

* Test before merging.
* Test critical trading logic.
* Keep test data organized.
* Document important test cases.

Never:

* Skip testing because changes are small.
* Test only the happy path.
* Deploy untested trading logic.

---

# 9.22 Quality Assurance Checklist

Before feature approval:

## Code

✅ Clean code
✅ Correct module location
✅ Error handling included

## Testing

✅ Unit tests completed
✅ Integration tests completed if required
✅ Regression checked

## Trading Safety

✅ Strategy behavior verified
✅ Risk behavior verified

## Documentation

✅ Documentation updated

---

# Chapter Summary

After completing this chapter:

The developer understands:

* ATS testing levels.
* Backend testing.
* Frontend testing.
* Trading logic validation.
* Paper trading requirements.
* Quality standards.

Testing becomes part of development, not an afterthought.

---

# Next Chapter

**Chapter 10 - Local Development Workflow**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance

Next:

Chapter 10 - Local Development Workflow
```

Continue `03_Development_Guide.md`

# Chapter 10 - Local Development Workflow

---

# 10.1 Purpose

The purpose of this chapter is to define the daily development workflow for building the Aegis Trading System (ATS).

A consistent workflow helps developers:

* Start development quickly.
* Avoid configuration mistakes.
* Keep code organized.
* Test changes safely.
* Maintain project quality.

The workflow covers:

* Starting the environment
* Developing features
* Testing changes
* Managing Git changes
* Updating documentation

---

# 10.2 Daily Development Workflow Overview

The standard ATS development cycle:

```text
Start Environment

        ↓

Check Current Status

        ↓

Review Documentation

        ↓

Create Feature Branch

        ↓

Implement Change

        ↓

Run Tests

        ↓

Review Code

        ↓

Commit Changes

        ↓

Update Documentation

        ↓

Merge Feature
```

---

# 10.3 Starting the Development Environment

Before coding, verify:

## Repository

Navigate to project:

```bash
cd Aegis-Trading-System
```

Check status:

```bash
git status
```

---

## Backend Environment

Navigate:

```bash
cd backend
```

Activate Python environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

---

## Frontend Environment

Navigate:

```bash
cd frontend
```

Install packages if required:

```bash
npm install
```

---

## Docker Services

Start required services:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

Expected:

```text
PostgreSQL running
```

---

# 10.4 Check Project Status Before Development

Before starting a task:

Review:

* Current phase
* Completed documentation
* Active tasks
* Architecture decisions

Important files:

```text
PROJECT_CONTEXT.md

MASTER_PROMPT.md

docs/
```

Reason:

Development must follow existing architecture.

---

# 10.5 Understanding a New Task

Every development task starts with:

## Goal

What needs to be created or changed?

Example:

"Create market session management."

---

## Architecture

Where does it belong?

Example:

```text
market/

└── session_manager.py
```

---

## Dependencies

What does it require?

Example:

```text
Market Module

Database

Configuration
```

---

## Testing

How will it be verified?

Example:

```text
Session opening test

Holiday test

Extended hours test
```

---

# 10.6 Creating a Feature Branch

Never develop directly on main.

Update develop:

```bash
git checkout develop

git pull
```

Create branch:

```bash
git checkout -b feature/session-management
```

---

# 10.7 Development Implementation Flow

Follow:

```text
Documentation

        ↓

Architecture Design

        ↓

Code

        ↓

Testing

        ↓

Review
```

---

Example:

Adding risk module:

Documentation:

```text
Define purpose and workflow
```

Architecture:

```text
risk/

position_sizing.py
```

Implementation:

```text
Write service
```

Testing:

```text
Verify calculations
```

---

# 10.8 Running Backend During Development

Start backend:

```bash
uvicorn app.main:app --reload
```

Development mode provides:

* Automatic reload
* Error visibility
* Fast iteration

---

# 10.9 Running Frontend During Development

Start frontend:

```bash
npm run dev
```

Frontend development server:

```text
localhost:5173
```

Backend:

```text
localhost:8000
```

---

# 10.10 Debugging Workflow

When a problem occurs:

Follow:

```text
Identify Error

        ↓

Check Logs

        ↓

Find Responsible Module

        ↓

Fix Root Cause

        ↓

Test Again
```

---

# 10.11 Debugging Rules

Never:

* Randomly change multiple files.
* Hide errors.
* Remove tests to make them pass.

Always:

* Understand the cause.
* Fix the correct layer.
* Add tests if needed.

---

# 10.12 Database Development Workflow

Database changes follow:

```text
Update Model

        ↓

Create Migration

        ↓

Review Migration

        ↓

Apply Migration

        ↓

Test Database
```

Example:

Adding a trade table:

```text
database/models.py

        ↓

Alembic migration

        ↓

PostgreSQL update
```

---

# 10.13 Testing Before Commit

Before committing:

Run:

Backend tests:

```bash
pytest
```

Frontend tests:

```bash
npm test
```

Database checks:

```text
Migration successful
```

---

# 10.14 Git Commit Workflow

Check changes:

```bash
git status
```

Add files:

```bash
git add .
```

Commit:

```bash
git commit -m "Add market session validation"
```

Push:

```bash
git push origin feature/session-management
```

---

# 10.15 Pull Request Workflow

A pull request should include:

## Description

Explain:

* What changed
* Why it changed

---

## Testing

Explain:

* Tests performed
* Results

---

## Documentation

Confirm:

* Documentation updated if required

---

# 10.16 Code Review Process

Review questions:

## Architecture

* Is this in the correct module?
* Does it follow responsibilities?

---

## Code Quality

* Is it readable?
* Is it reusable?
* Are errors handled?

---

## Trading Safety

* Can this affect trading decisions?
* Has it been tested?

---

# 10.17 Documentation Update Process

Documentation must be updated when:

* Architecture changes
* New modules are added
* New workflows are introduced
* Important decisions are made

Documentation location:

```text
docs/
```

---

# 10.18 End-of-Day Development Process

Before finishing work:

Check:

```text
Code saved

↓

Tests completed

↓

Changes committed

↓

Documentation updated

↓

Task status updated
```

---

# 10.19 Development Environment Shutdown

Stop services:

Docker:

```bash
docker compose down
```

Deactivate Python:

```bash
deactivate
```

Stop development servers:

```text
CTRL + C
```

---

# 10.20 Local Development Rules

Always:

* Start with documentation.
* Keep changes small.
* Test before commit.
* Commit meaningful changes.
* Keep architecture clean.

Never:

* Skip testing.
* Commit secrets.
* Develop directly on production.
* Ignore documentation.

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Daily ATS development workflow.
* Feature development process.
* Debugging process.
* Database change process.
* Git workflow.
* Documentation workflow.

This completes the local development process foundation.

---

# Next Chapter

**Chapter 11 - Environment Separation: Development, Testing, and Production**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance
Chapter 10 - Local Development Workflow

Next:

Chapter 11 - Environment Separation: Development, Testing, and Production
```

Continue `03_Development_Guide.md`

# Chapter 11 - Environment Separation: Development, Testing, and Production

---

# 11.1 Purpose

The purpose of this chapter is to define how Aegis Trading System (ATS) separates different operating environments.

A trading system must clearly separate development, testing, paper trading, and live trading environments.

This prevents:

* Accidental live trades
* Database corruption
* Testing with real capital
* Configuration mistakes
* Uncontrolled changes

ATS follows the principle:

**Never test new ideas with real trading capital.**

---

# 11.2 Environment Overview

ATS uses four main environments:

```text
 id="envflow01"
Development

      ↓

Testing

      ↓

Paper Trading

      ↓

Live Production
```

Each environment has a different purpose.

---

# 11.3 Development Environment

## Purpose

The development environment is where ATS is built.

Used for:

* Writing code
* Testing new features
* Debugging
* Architecture development

---

## Characteristics

Examples:

```text
Machine:

Developer Computer

Database:

Local PostgreSQL

Trading Mode:

No real execution
```

---

## Allowed Activities

✅ Create new modules
✅ Change architecture
✅ Test new ideas
✅ Run simulations

---

## Not Allowed

❌ Connect to live broker account
❌ Execute real orders
❌ Use production database

---

# 11.4 Testing Environment

## Purpose

The testing environment verifies that code behaves correctly before moving forward.

Used for:

* Automated tests
* Integration testing
* Database testing

---

## Characteristics

Example:

```text
Application:

Test Build

Database:

Test Database

Trading Mode:

Simulation
```

---

## Testing Environment Goals

Verify:

* API functionality
* Database operations
* Strategy calculations
* Risk calculations
* System stability

---

# 11.5 Paper Trading Environment

## Purpose

Paper trading tests ATS behavior in real market conditions without risking capital.

This is the bridge between development and live trading.

---

## Characteristics

Example:

```text
Market Data:

Real Market Data

Execution:

Simulated Orders

Capital:

Virtual
```

---

## Paper Trading Validates

* Market data handling
* Strategy decisions
* Entry timing
* Exit logic
* Risk management
* System reliability

---

# 11.6 Live Production Environment

## Purpose

The production environment executes real trading operations.

It is the final environment.

---

## Characteristics

Example:

```text
Server:

Cloud Infrastructure

Database:

Production PostgreSQL

Execution:

Real Broker Account
```

---

## Production Requirements

Before live trading:

Must have:

✅ Tested strategy
✅ Completed paper trading
✅ Backup system
✅ Monitoring system
✅ Error handling
✅ Secure credentials

---

# 11.7 Environment Comparison

| Feature     | Development | Testing | Paper Trading    | Production    |
| ----------- | ----------- | ------- | ---------------- | ------------- |
| Purpose     | Build       | Verify  | Simulate Trading | Real Trading  |
| Database    | Local DB    | Test DB | Paper DB         | Production DB |
| Real Orders | No          | No      | No               | Yes           |
| Real Money  | No          | No      | No               | Yes           |
| Debug Mode  | Enabled     | Limited | Limited          | Disabled      |

---

# 11.8 Database Separation

Each environment must use a separate database.

Example:

```text
Development:

ats_development


Testing:

ats_testing


Paper Trading:

ats_paper


Production:

ats_production
```

---

Reason:

Prevents:

* Test data entering production
* Production data corruption
* Accidental deletion

---

# 11.9 Configuration Separation

Each environment has its own configuration.

Example:

```text
.env.development

.env.testing

.env.paper

.env.production
```

---

Example:

Development:

```env
APP_ENV=development

TRADING_MODE=disabled
```

---

Paper Trading:

```env
APP_ENV=paper

TRADING_MODE=simulation
```

---

Production:

```env
APP_ENV=production

TRADING_MODE=live
```

---

# 11.10 Trading Mode Safety

ATS must always know the current trading mode.

Possible modes:

```text
DISABLED

PAPER

LIVE
```

---

Example:

```text
DISABLED

↓

No execution allowed


PAPER

↓

Simulated execution


LIVE

↓

Real broker execution
```

---

# 11.11 Live Trading Protection Rules

ATS must include safety checks.

Before sending a real order:

System verifies:

```text
Environment = Production

        AND

Trading Mode = LIVE

        AND

Broker Connection Valid

        AND

Risk Rules Passed
```

Only then execution is allowed.

---

# 11.12 Code Promotion Workflow

Changes move through environments:

```text
Development

      ↓

Code Review

      ↓

Testing

      ↓

Paper Trading

      ↓

Production
```

---

A feature must not skip environments.

Example:

Incorrect:

```text
Development

      ↓

Live Trading
```

Correct:

```text
Development

      ↓

Testing

      ↓

Paper Trading

      ↓

Live
```

---

# 11.13 Environment Variables Rules

Sensitive information belongs only in environment configuration.

Examples:

* Database passwords
* Broker API keys
* Secret keys

Never store:

```python
API_KEY="123456"
```

Inside source code.

---

Correct:

```text
Environment Variable

        ↓

Application Configuration

        ↓

Service
```

---

# 11.14 Logging Differences

Different environments require different logging levels.

Development:

```text
Detailed logs

Debug enabled
```

Testing:

```text
Test-focused logs
```

Paper Trading:

```text
Trading decision logs
```

Production:

```text
Important events only

No sensitive information
```

---

# 11.15 Backup Rules

Backup priority increases by environment.

Development:

Basic backup.

Testing:

Reusable test data.

Paper Trading:

Historical simulation data.

Production:

Mandatory:

* Database backup
* Trade records backup
* Configuration backup

---

# 11.16 Environment Checklist

Before moving to the next environment:

## Development

✅ Code works
✅ Tests created
✅ Documentation updated

---

## Testing

✅ Automated tests passed
✅ Database migration tested

---

## Paper Trading

✅ Real-time data tested
✅ Strategy behavior verified
✅ Risk controls verified

---

## Production

✅ Security reviewed
✅ Backup configured
✅ Monitoring active

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Why ATS requires environment separation.
* Difference between development, testing, paper trading, and production.
* Database isolation rules.
* Configuration separation.
* Live trading protection rules.
* Safe deployment workflow.

Environment separation protects the system from unsafe changes and accidental capital risk.

---

# Next Chapter

**Chapter 12 - Configuration Management and Secrets Handling**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance
Chapter 10 - Local Development Workflow
Chapter 11 - Environment Separation: Development, Testing, and Production

Next:

Chapter 12 - Configuration Management and Secrets Handling
```

Continue `03_Development_Guide.md`

# Chapter 12 - Configuration Management and Secrets Handling

---

# 12.1 Purpose

The purpose of this chapter is to define how Aegis Trading System (ATS) manages configuration values and protects sensitive information.

A professional trading platform requires secure configuration management because it handles:

* Database credentials
* Broker API credentials
* Trading settings
* System parameters
* Environment-specific values

The goal:

**Keep configuration flexible and secrets protected.**

---

# 12.2 Configuration Management Principle

ATS separates:

```text id="configflow01"
Application Code

        +

Configuration

        +

Secrets
```

Code defines system behavior.

Configuration defines environment behavior.

Secrets provide secure access.

---

# 12.3 Types of Configuration

ATS configuration is divided into three categories.

---

# 1. Application Configuration

Controls general application behavior.

Examples:

```text id="appconfig01"
Application name

Environment mode

Debug mode

Server settings
```

---

# 2. Trading Configuration

Controls trading-related parameters.

Examples:

```text id="tradeconfig01"
Trading mode

Risk percentage

Maximum positions

Timeframes

Strategy settings
```

---

# 3. Infrastructure Configuration

Controls external services.

Examples:

```text id="infra01"
Database URL

Broker connection

Cloud services

External APIs
```

---

# 12.4 Environment Configuration Files

ATS uses separate configuration files.

Example:

```text id="envfiles01"
.env.development

.env.testing

.env.paper

.env.production
```

---

Each environment contains different values.

Example:

Development:

```env
APP_ENV=development

TRADING_MODE=disabled

DATABASE_NAME=ats_development
```

---

Paper Trading:

```env
APP_ENV=paper

TRADING_MODE=paper

DATABASE_NAME=ats_paper
```

---

Production:

```env
APP_ENV=production

TRADING_MODE=live

DATABASE_NAME=ats_production
```

---

# 12.5 Environment Variable Rules

Environment variables are used for:

* Secrets
* Environment differences
* Deployment configuration

Example:

```env
DATABASE_URL=

BROKER_API_KEY=

BROKER_SECRET_KEY=

SECRET_KEY=
```

---

Rules:

Always:

✅ Store secrets outside code
✅ Use environment variables
✅ Document required variables

Never:

❌ Hardcode passwords
❌ Commit secrets to GitHub
❌ Share production keys

---

# 12.6 .env File Management

Local development:

```text id="envlocal01"
.env
```

Example:

```env
DATABASE_URL=postgresql://localhost/ats

APP_ENV=development
```

---

GitHub must contain:

```text id="envexample01"
.env.example
```

Example:

```env
DATABASE_URL=

APP_ENV=

BROKER_API_KEY=
```

---

Purpose:

Developers know required configuration without exposing secrets.

---

# 12.7 Configuration Loading Architecture

ATS backend follows:

```text id="loadflow01"
Environment Variables

        ↓

Configuration Module

        ↓

Application Services
```

---

Example future structure:

```text
backend/

app/

└── core/

    ├── config.py

    └── security.py
```

---

# 12.8 Configuration Module Responsibility

The configuration module handles:

* Loading environment variables
* Validating values
* Providing application settings

It should not contain:

* Trading logic
* Database logic
* API routes

---

# 12.9 Configuration Validation

ATS should validate important settings during startup.

Examples:

Check:

```text id="validate01"
Database URL exists

Broker credentials exist

Trading mode is valid
```

---

Invalid example:

```text
TRADING_MODE=random_value
```

Application should refuse to start.

---

# 12.10 Secret Management

Secrets include:

* Broker API keys
* Database passwords
* Authentication secrets
* Encryption keys

---

Secrets must be protected because exposure can cause:

* Unauthorized access
* Account compromise
* Financial risk

---

# 12.11 Secret Storage Rules

Development:

Use:

```text
.env
```

---

Production:

Use secure secret management.

Examples:

* Cloud secret manager
* Protected environment variables
* Encrypted storage

---

Production secrets should never exist:

* In source code
* In Git history
* In documentation

---

# 12.12 Broker Credential Management

Broker credentials require additional protection.

Example:

```text id="brokerflow01"
Broker API Key

        ↓

Environment Variable

        ↓

Execution Service

        ↓

Broker API
```

---

Rules:

Only execution-related services should access broker credentials.

Other modules should not know them.

Example:

Strategy module:

❌ No broker key access

Execution module:

✅ Broker connection access

---

# 12.13 Database Credential Management

Database access follows least privilege.

Example:

Different users:

```text id="dbusers01"
Application User

Migration User

Administrator User
```

---

Reason:

Limits damage if credentials are exposed.

---

# 12.14 Frontend Configuration Security

Frontend environment variables are public after build.

Therefore:

Never place:

* Broker keys
* Database passwords
* Private secrets

Inside frontend configuration.

---

Frontend can contain:

```env
VITE_API_URL=
```

Because it only points to backend services.

---

# 12.15 Configuration Change Workflow

Configuration changes follow:

```text id="configchange01"
Identify Requirement

        ↓

Update Documentation

        ↓

Modify Configuration

        ↓

Test Environment

        ↓

Apply Change
```

---

Example:

Adding new broker:

1. Document required keys.
2. Add environment variables.
3. Test connection.
4. Enable only in required environment.

---

# 12.16 Configuration Backup

Backup:

✅ Configuration templates
✅ Documentation
✅ Example files

Do not backup publicly:

❌ Passwords
❌ API keys
❌ Private credentials

---

# 12.17 Security Checklist

Before deployment:

## Secrets

✅ No secrets in code
✅ No secrets in Git
✅ Environment variables configured

---

## Configuration

✅ Environment separated
✅ Values validated
✅ Documentation updated

---

## Trading Safety

✅ Live mode requires confirmation
✅ Broker credentials protected

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Configuration management.
* Environment variables.
* Secret protection.
* Broker credential handling.
* Database credential security.
* Production safety practices.

Proper configuration management protects ATS from security risks and accidental trading issues.

---

# Next Chapter

**Chapter 13 - Logging and Monitoring Standards**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance
Chapter 10 - Local Development Workflow
Chapter 11 - Environment Separation: Development, Testing, and Production
Chapter 12 - Configuration Management and Secrets Handling

Next:

Chapter 13 - Logging and Monitoring Standards
```

Continue `03_Development_Guide.md`

# Chapter 13 - Logging and Monitoring Standards

---

# 13.1 Purpose

The purpose of this chapter is to define how Aegis Trading System (ATS) records, tracks, and monitors system activity.

A trading system must be transparent.

Every important event should be understandable:

* What happened?
* When did it happen?
* Why did it happen?
* Which component caused it?

The goal:

**Every trading decision must be explainable.**

---

# 13.2 Logging Philosophy

ATS uses logging for:

* Debugging problems
* Understanding system behavior
* Tracking trading decisions
* Monitoring system health
* Investigating failures

Logs are not only for errors.

Logs provide system history.

---

# 13.3 Logging Categories

ATS divides logs into different categories.

```text id="logflow01"
Application Logs

        ↓

Market Data Logs

        ↓

Strategy Decision Logs

        ↓

Trade Execution Logs

        ↓

Error Logs
```

Each category has a different purpose.

---

# 13.4 Application Logs

## Purpose

Track general application behavior.

Examples:

* Application startup
* Service status
* Configuration loading
* Background workers

Example:

```text id="applog01"
2026-07-09 10:00:00

ATS Backend Started Successfully
```

---

# 13.5 Market Data Logs

## Purpose

Track market data processing.

Examples:

* Data received
* Candle creation
* Data connection status

Example:

```text id="marketlog01"
Received 5-minute candle

Symbol:
SPX500

Time:
10:05

Status:
Processed
```

---

# 13.6 Indicator Logs

## Purpose

Track indicator calculations when required.

Examples:

* Calculation errors
* Missing data
* Invalid values

Example:

```text id="indicatorlog01"
ATR calculation failed

Reason:
Insufficient candle history
```

---

# 13.7 Strategy Decision Logs

## Purpose

Record why ATS made a decision.

This is one of the most important logs.

A trading decision should include:

```text id="decisionlog01"
Time

Market

Timeframe

Market Bias

Trend Health

Entry Confirmation

Confidence Score

Decision

Reason
```

---

Example:

```text id="decisionexample01"
Time:
10:15

Bias:
Bullish

Trend:
Healthy

Confidence:
82

Decision:
LONG

Reason:
Multi-timeframe confirmation completed
```

---

# 13.8 Risk Management Logs

## Purpose

Track capital protection decisions.

Examples:

* Position sizing
* Stop loss calculation
* Risk rejection

Example:

```text id="risklog01"
Trade rejected

Reason:
Maximum daily risk reached
```

---

# 13.9 Trade Execution Logs

## Purpose

Track order lifecycle.

Includes:

* Order creation
* Order submission
* Order result
* Position changes

Example:

```text id="executionlog01"
Order Submitted

Symbol:
SPX500

Side:
BUY

Status:
Accepted
```

---

# 13.10 Error Logs

## Purpose

Capture failures.

Examples:

* API failures
* Database errors
* Connection problems
* Unexpected exceptions

Example:

```text id="errorlog01"
Database connection failed

Service:
Market Data Worker
```

---

# 13.11 Log Levels

ATS uses standard log levels.

| Level    | Purpose                          |
| -------- | -------------------------------- |
| DEBUG    | Detailed development information |
| INFO     | Normal system activity           |
| WARNING  | Possible issue                   |
| ERROR    | Failure requiring attention      |
| CRITICAL | Serious system failure           |

---

Example:

Development:

```text id="logleveldev01"
DEBUG enabled
```

Production:

```text id="loglevelprod01"
INFO and above
```

---

# 13.12 Logging Structure

Logs should contain consistent information.

Recommended format:

```text id="logformat01"
Timestamp

Environment

Service

Event

Details

Status
```

Example:

```text
2026-07-09 10:30

Production

Strategy Engine

Decision Generated

LONG

Success
```

---

# 13.13 Backend Logging Architecture

Future structure:

```text id="loggingstructure01"
backend/

app/

└── core/

    └── logging.py
```

Responsibility:

* Configure logging
* Define formats
* Control log levels

---

# 13.14 Frontend Logging

Frontend logs are limited.

Frontend should log:

* Connection issues
* UI errors
* API failures

Frontend should not log:

* Trading decisions
* Strategy calculations
* Sensitive information

---

# 13.15 Database Logging

Database monitoring includes:

* Connection status
* Query problems
* Migration errors
* Storage usage

Important database events:

* Backup completion
* Migration execution
* Connection failures

---

# 13.16 Monitoring Purpose

Monitoring answers:

## Is ATS running?

Check:

* Services
* Containers
* Database

---

## Is ATS healthy?

Check:

* Errors
* Performance
* Connections

---

## Is ATS trading safely?

Check:

* Risk controls
* Execution status
* Decision logs

---

# 13.17 System Health Monitoring

Important metrics:

## Application

* CPU usage
* Memory usage
* Service uptime

---

## Database

* Connection count
* Storage usage
* Query performance

---

## Trading System

* Active positions
* Order status
* Strategy decisions
* Risk state

---

# 13.18 Alerting System

Future ATS versions should support alerts.

Examples:

Critical alerts:

* Backend stopped
* Database unavailable
* Broker disconnected
* Execution failure

Warning alerts:

* High latency
* Missing market data
* Unusual behavior

---

# 13.19 Monitoring During Development

Development monitoring focuses on:

* Errors
* Debugging
* Testing behavior

Example:

Developer checks:

```text id="devmonitor01"
Backend logs

↓

Database logs

↓

Browser console
```

---

# 13.20 Monitoring During Paper Trading

Paper trading monitoring focuses on:

* Strategy decisions
* Signal quality
* Execution simulation
* Risk behavior

Important:

Paper trading creates confidence before live trading.

---

# 13.21 Monitoring During Production

Production monitoring focuses on:

* System availability
* Trading safety
* Execution reliability
* Capital protection

Production requires:

* Persistent logs
* Alerts
* Backups
* Monitoring dashboard

---

# 13.22 Log Security Rules

Never log:

❌ Passwords
❌ API keys
❌ Private credentials

Be careful with:

* Account information
* Broker responses
* Sensitive data

---

# 13.23 Logging Checklist

Before production:

## Application

✅ Logging configured
✅ Log levels defined

---

## Trading

✅ Decision logs available
✅ Execution logs available

---

## Security

✅ Secrets removed from logs

---

## Monitoring

✅ Health checks created
✅ Critical alerts planned

---

# Chapter Summary

After completing this chapter:

The developer understands:

* ATS logging strategy.
* Trading decision transparency.
* Error tracking.
* Monitoring requirements.
* Production observability.

Logging and monitoring make ATS easier to debug, safer to operate, and more trustworthy.

---

# Next Chapter

**Chapter 14 - Deployment Preparation Guide**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance
Chapter 10 - Local Development Workflow
Chapter 11 - Environment Separation: Development, Testing, and Production
Chapter 12 - Configuration Management and Secrets Handling
Chapter 13 - Logging and Monitoring Standards

Next:

Chapter 14 - Deployment Preparation Guide
```

Continue `03_Development_Guide.md`

# Chapter 14 - Deployment Preparation Guide

---

# 14.1 Purpose

The purpose of this chapter is to define how Aegis Trading System (ATS) will be prepared for future deployment.

Deployment is the process of moving ATS from a development environment into a production environment where it can operate reliably.

The goal:

**Deploy a stable, secure, and maintainable trading platform.**

Deployment is not only moving code.

It includes:

* Infrastructure preparation
* Security configuration
* Database setup
* Service management
* Monitoring
* Backup planning

---

# 14.2 Deployment Philosophy

ATS follows this deployment principle:

```text
Develop Safely

        ↓

Test Completely

        ↓

Deploy Carefully

        ↓

Monitor Continuously
```

Production deployment happens only after:

* Testing is completed.
* Paper trading is completed.
* System behavior is understood.

---

# 14.3 Production Infrastructure Overview

Future ATS production environment:

```text id="productionflow01"
Oracle Cloud Server

        ↓

Docker Environment

        ↓

ATS Services

        ↓

PostgreSQL Database

        ↓

Broker Connection
```

---

# 14.4 Production Components

Production will contain:

## Backend Service

Technology:

* Python
* FastAPI
* Uvicorn

Responsibilities:

* Trading logic
* Market processing
* Risk management
* Execution control

---

## Frontend Service

Technology:

* React
* Vite build

Responsibilities:

* Dashboard
* Monitoring interface
* User controls

---

## Database Service

Technology:

* PostgreSQL

Responsibilities:

* Market history
* Trading records
* System data

---

# 14.5 Server Requirements

Production server should consider:

## CPU

Required for:

* Indicator calculations
* Strategy processing
* Background workers

---

## RAM

Required for:

* Application services
* Database cache
* Market data processing

---

## Storage

Required for:

* Historical market data
* Logs
* Database backups

---

## Network

Required for:

* Broker communication
* Market data connection
* User access

---

# 14.6 Deployment Architecture

Production architecture:

```text id="deployarch01"
                Users

                  |

                  |

              Frontend

                  |

                  |

               Backend

                  |

        -------------------

        |                 |

    PostgreSQL        Broker API

```

---

# 14.7 Docker Production Strategy

Production uses Docker because it provides:

* Consistent environments
* Easier updates
* Service isolation
* Simple rollback

Production containers:

```text id="prodcontainers01"
ATS Frontend Container

ATS Backend Container

PostgreSQL Container
```

---

# 14.8 Production Configuration

Production uses separate configuration.

Example:

```text id="prodconfig01"
.env.production
```

Contains:

```env
APP_ENV=production

DATABASE_URL=

BROKER_API_KEY=

TRADING_MODE=live
```

---

Rules:

Never use:

* Development configuration
* Testing database
* Local credentials

---

# 14.9 Deployment Workflow

Standard deployment:

```text id="deploymentflow01"
Code Completed

        ↓

Tests Passed

        ↓

Code Review

        ↓

Build Docker Images

        ↓

Deploy to Server

        ↓

Run Health Checks

        ↓

Monitor
```

---

# 14.10 Database Deployment

Database deployment requires:

## Before Deployment

Check:

* Migration files exist
* Database backup created

---

## Deployment

Process:

```text id="dbdeploy01"
Backup Database

        ↓

Run Migration

        ↓

Verify Tables

        ↓

Start Application
```

---

# 14.11 Database Backup Strategy

Production database contains valuable information:

* Trade history
* Strategy decisions
* Market data

Backup requirements:

## Automated Backups

Schedule:

* Daily backups
* Regular snapshots

---

## Backup Testing

A backup is only useful if recovery works.

Test:

```text id="backup01"
Create Backup

        ↓

Restore Backup

        ↓

Verify Data
```

---

# 14.12 Application Updates

Production updates should be controlled.

Workflow:

```text id="updateflow01"
New Version

        ↓

Testing Environment

        ↓

Paper Trading

        ↓

Production Update
```

---

# 14.13 Rollback Strategy

Every deployment should have a rollback plan.

If problems occur:

```text id="rollback01"
Problem Detected

        ↓

Stop New Version

        ↓

Restore Previous Version

        ↓

Investigate Issue
```

---

# 14.14 Security Preparation

Before production:

Required:

## Server Security

* Firewall rules
* Secure access
* Updated software

---

## Application Security

* Protected secrets
* Secure API access
* Authentication

---

## Database Security

* Strong passwords
* Limited permissions
* Backup protection

---

# 14.15 Production Monitoring

After deployment monitor:

## Application

* Backend status
* API response
* Errors

---

## Database

* Connections
* Storage
* Performance

---

## Trading System

* Market data flow
* Strategy execution
* Trade status

---

# 14.16 Live Trading Safety Controls

Before enabling live trading:

ATS must verify:

```text id="livesafety01"
Production Environment

        AND

Trading Mode = LIVE

        AND

Risk System Active

        AND

Broker Connection Valid

        AND

Monitoring Active
```

---

# 14.17 Deployment Checklist

Before first production deployment:

## Infrastructure

✅ Server ready
✅ Docker installed
✅ Network configured

---

## Application

✅ Backend deployed
✅ Frontend deployed
✅ Database connected

---

## Security

✅ Secrets protected
✅ Access restricted

---

## Trading Safety

✅ Paper trading completed
✅ Risk controls verified
✅ Monitoring active

---

# 14.18 Future Cloud Deployment

ATS plans to use:

Oracle Cloud

Future deployment tasks:

* Server creation
* Docker installation
* Database deployment
* SSL configuration
* Monitoring setup
* Backup automation

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Production deployment preparation.
* Cloud deployment planning.
* Docker production usage.
* Database deployment.
* Backup strategy.
* Rollback planning.
* Live trading safety requirements.

Deployment is treated as an engineering process, not a simple code upload.

---

# Next Chapter

**Chapter 15 - Development Maintenance and Long-Term Project Management**

---

Update `CURRENT_STATUS.md`:

```text
03_Development_Guide.md

Completed:

Chapter 1 - Development Environment Overview
Chapter 2 - Local Machine Setup
Chapter 3 - Project Repository Structure and Git Workflow
Chapter 4 - Backend Development Environment Setup
Chapter 5 - Frontend Development Environment Setup
Chapter 6 - Database Development Environment Setup
Chapter 7 - Docker Development Environment Setup
Chapter 8 - Development Workflow and Coding Standards
Chapter 9 - Testing Strategy and Quality Assurance
Chapter 10 - Local Development Workflow
Chapter 11 - Environment Separation: Development, Testing, and Production
Chapter 12 - Configuration Management and Secrets Handling
Chapter 13 - Logging and Monitoring Standards
Chapter 14 - Deployment Preparation Guide

Next:

Chapter 15 - Development Maintenance and Long-Term Project Management
```

Continue `03_Development_Guide.md`

# Chapter 15 - Development Maintenance and Long-Term Project Management

---

# 15.1 Purpose

The purpose of this chapter is to define how Aegis Trading System (ATS) will be maintained and improved over the long term.

A professional trading platform is not finished after the first release.

ATS will continue to evolve through:

* New features
* Strategy improvements
* Performance improvements
* Security updates
* Infrastructure changes

The goal:

**Maintain a reliable system that remains understandable years after development begins.**

---

# 15.2 Long-Term Development Philosophy

ATS follows:

```text id="maintainflow01"
Build Carefully

        ↓

Document Decisions

        ↓

Monitor Performance

        ↓

Improve Safely

        ↓

Maintain Stability
```

---

# 15.3 Project Maintenance Areas

ATS maintenance covers:

```text id="maintenanceareas01"
Code

Documentation

Dependencies

Database

Infrastructure

Security

Trading Logic
```

---

# 15.4 Code Maintenance

## Purpose

Keep the codebase clean and understandable.

Regular activities:

* Review old code
* Remove unused code
* Improve readability
* Refactor repeated logic

---

## Code Quality Rules

Always:

✅ Keep modules focused
✅ Remove unnecessary complexity
✅ Maintain architecture rules

Never:

❌ Create quick fixes without documentation
❌ Duplicate existing functionality
❌ Ignore technical problems

---

# 15.5 Technical Debt Management

## Purpose

Technical debt is the cost created by temporary solutions.

Example:

Quick solution:

```text id="debt01"
Create temporary calculation inside strategy module
```

Future problem:

```text id="debt02"
Difficult to maintain

Hard to test

Architecture violation
```

---

ATS manages technical debt by:

* Recording issues
* Prioritizing improvements
* Fixing important problems

---

# 15.6 Documentation Maintenance

Documentation must stay synchronized with the system.

Update documentation when:

* Architecture changes
* New modules are created
* Workflows change
* Important decisions are made

---

Important documents:

```text id="docsmaintain01"
PROJECT_CONTEXT.md

MASTER_PROMPT.md

docs/

README.md
```

---

# 15.7 Dependency Management

ATS depends on external software:

Examples:

Backend:

* Python packages

Frontend:

* npm packages

Infrastructure:

* Docker images

---

Dependencies require:

* Regular updates
* Security checks
* Compatibility testing

---

Update process:

```text id="dependencyflow01"
Check Update

        ↓

Review Changes

        ↓

Test Locally

        ↓

Deploy Safely
```

---

# 15.8 Version Management

ATS uses version control.

Example:

```text id="version01"
Version 1.0

Foundation Release


Version 1.1

New Features


Version 2.0

Major Architecture Changes
```

---

Version numbers should represent meaningful changes.

---

# 15.9 Git Repository Maintenance

Maintain:

* Clean branches
* Clear commit history
* Organized releases

Recommended branches:

```text id="gitbranches01"
main

↓

Production Code


develop

↓

Active Development


feature/*

↓

New Features
```

---

# 15.10 Database Maintenance

Database maintenance includes:

* Migration management
* Backup verification
* Performance checks
* Storage monitoring

---

Rules:

Never:

❌ Delete trading history without approval
❌ Change production tables manually

Always:

✅ Use migrations
✅ Test database changes

---

# 15.11 Trading Strategy Maintenance

Trading logic requires careful management.

Changes to strategy must include:

* Reason for change
* Expected improvement
* Backtest results
* Paper trading validation

---

Strategy update workflow:

```text id="strategyupdate01"
Idea

↓

Documentation

↓

Backtest

↓

Paper Trading

↓

Production Review
```

---

# 15.12 AI-Assisted Development Maintenance

ATS uses AI as a development assistant.

AI can help with:

* Code generation
* Code review
* Documentation
* Debugging

---

AI must follow:

```text id="aimaintain01"
PROJECT_CONTEXT.md

        +

MASTER_PROMPT.md

        +

Current Architecture
```

---

AI must not:

❌ Change architecture without review
❌ Create undocumented modules
❌ Move business logic incorrectly

---

# 15.13 Backup Strategy

Important ATS data:

* Database records
* Trade history
* Strategy decisions
* Configuration templates
* Documentation

---

Backup levels:

## Development

Basic backup.

---

## Paper Trading

Historical testing data backup.

---

## Production

Mandatory:

* Automated database backup
* Configuration backup
* Recovery testing

---

# 15.14 Disaster Recovery Planning

Purpose:

Recover ATS after major failure.

Possible failures:

* Server failure
* Database corruption
* Credential issues
* Software problems

---

Recovery process:

```text id="recovery01"
Detect Problem

↓

Stop Unsafe Operations

↓

Restore Backup

↓

Verify System

↓

Resume Operation
```

---

# 15.15 Performance Improvement

ATS performance should be monitored continuously.

Areas:

## Backend

* API response time
* Worker performance
* Indicator calculation speed

---

## Database

* Query performance
* Storage growth

---

## Frontend

* Rendering performance
* Data updates

---

# 15.16 Future Developer Onboarding

Even if ATS starts as a single developer project, future contributors should understand:

* Architecture
* Development workflow
* Trading philosophy
* Coding standards

Required documents:

```text id="onboard01"
README.md

PROJECT_CONTEXT.md

MASTER_PROMPT.md

Development Guide

Architecture Documents
```

---

# 15.17 Regular Maintenance Schedule

Recommended:

## Weekly

* Review errors
* Check logs
* Review open issues

---

## Monthly

* Dependency review
* Documentation review
* Performance review

---

## Before Major Release

* Full testing
* Architecture review
* Backup verification

---

# 15.18 Maintenance Checklist

## Code

✅ Clean architecture
✅ No unnecessary complexity
✅ Tests maintained

---

## Documentation

✅ Updated decisions
✅ Current workflows
✅ Architecture matches reality

---

## Security

✅ Secrets protected
✅ Dependencies updated

---

## Trading

✅ Strategy changes validated
✅ Risk controls tested

---

# Chapter Summary

After completing this chapter:

The developer understands:

* Long-term ATS maintenance.
* Technical debt management.
* Documentation responsibility.
* Dependency updates.
* Backup planning.
* Strategy change management.
* AI-assisted development rules.

Aegis Trading System is designed not only to be built, but to be maintained and improved for years.

---

# `03_Development_Guide.md` Completion Status

```text
Completed:

✅ Chapter 1 - Development Environment Overview
✅ Chapter 2 - Local Machine Setup
✅ Chapter 3 - Project Repository Structure and Git Workflow
✅ Chapter 4 - Backend Development Environment Setup
✅ Chapter 5 - Frontend Development Environment Setup
✅ Chapter 6 - Database Development Environment Setup
✅ Chapter 7 - Docker Development Environment Setup
✅ Chapter 8 - Development Workflow and Coding Standards
✅ Chapter 9 - Testing Strategy and Quality Assurance
✅ Chapter 10 - Local Development Workflow
✅ Chapter 11 - Environment Separation: Development, Testing, and Production
✅ Chapter 12 - Configuration Management and Secrets Handling
✅ Chapter 13 - Logging and Monitoring Standards
✅ Chapter 14 - Deployment Preparation Guide
✅ Chapter 15 - Development Maintenance and Long-Term Project Management
```

---

# Phase 0 Documentation Status

**COMPLETE ✅**

Completed documentation foundation:

✅ README.md
✅ 00_Project_Vision.md
✅ 01_Tech_Stack.md
✅ 02_System_Architecture.md
✅ 03_Development_Guide.md

---
