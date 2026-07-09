# 01 - Technology Stack

Version: 1.0

---

# Purpose

This document defines the official technology stack for the Aegis Trading System (ATS).

Every future development must follow this technology stack unless the architecture is officially updated.

---

# Backend

## Python

Purpose:
Main programming language.

Reason:

- Excellent ecosystem for finance
- Fast development
- Easy maintenance
- Large community
- Perfect for data processing

---

## FastAPI

Purpose:
Backend API framework.

Reason:

- High performance
- Modern Python framework
- Automatic API documentation
- Excellent WebSocket support
- Async support

---

## SQLAlchemy

Purpose:
Database ORM.

Reason:

- Clean database code
- Easy maintenance
- Database independence
- Professional standard

---

## Alembic

Purpose:
Database migrations.

Reason:

- Version control for database
- Safe schema updates
- Production ready

---

## PostgreSQL

Purpose:
Primary database.

Reason:

- Reliable
- Scalable
- Handles millions of rows
- Excellent performance
- Industry standard

SQLite will only be used for testing if needed.

---

# Frontend

## React

Purpose:
Build the user interface.

Reason:

- Component based
- Easy to maintain
- Perfect for dashboards
- Large ecosystem

---

## JavaScript

Purpose:
Frontend programming language.

Reason:

- Easier than TypeScript for Version 1
- Faster learning
- Can migrate to TypeScript later

---

## Vite

Purpose:
Frontend build tool.

Reason:

- Extremely fast
- Modern
- Easy configuration

---

## Tailwind CSS

Purpose:
User interface styling.

Reason:

- Fast development
- Easy maintenance
- Responsive design
- Modern UI

---

## Axios

Purpose:
Communicate with FastAPI.

Reason:

- Easy HTTP requests
- Reliable
- Simple API

---

## WebSocket

Purpose:
Real-time updates.

Reason:

- Live dashboard
- Live prices
- Live trading updates
- No page refresh

---

# Infrastructure

## Git

Purpose:
Version control.

---

## GitHub

Purpose:
Source code hosting.

---

## Docker

Purpose:
Application deployment.

---

## Oracle Cloud

Purpose:
Production hosting.

Free Tier will be used during development.

---

# Database Policy

Official database:

PostgreSQL

Rules:

- Never store business logic in the database.
- Keep calculations in Python.
- Use indexes where necessary.
- Use Alembic for schema changes.

---

# Frontend Policy

React is responsible only for:

- Displaying information
- User interaction
- Sending requests

React must NEVER:

- Calculate indicators
- Calculate trend health
- Calculate confidence
- Make trading decisions

All calculations happen in the backend.

---

# Backend Policy

Backend is responsible for:

- Market data
- Indicator calculations
- Trading logic
- Risk management
- Trade execution
- Logging
- Database

---

# Future Technologies

Possible future additions:

- Redis
- Celery
- Machine Learning
- Mobile App
- Multi-user Support

These are NOT part of Version 1.

---

END OF DOCUMENT