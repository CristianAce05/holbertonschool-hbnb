# HBnB Evolution – Part 1: Technical Documentation

## Overview

This directory contains the **technical documentation** for **Part 1** of the **HBnB Evolution** project.

The purpose of this part is to define the **architecture**, **business logic design**, and **system interactions** of a simplified AirBnB-like application before implementation begins.

All documentation is written using **UML notation** and serves as the foundation for the development phases in Parts 2 and 3.

---

## Contents

###  HBNB_Part1_Technical_Documentation.md

This document includes:

- **High-Level Package Diagram**
  - Three-layer architecture:
    - Presentation Layer
    - Business Logic Layer
    - Persistence Layer
  - Communication via the **Facade Pattern**

- **Business Logic Class Diagram**
  - Core entities:
    - User
    - Place
    - Review
    - Amenity
  - Attributes, relationships, and constraints
  - Audit fields (`created_at`, `updated_at`)

All diagrams are created using **Mermaid.js** and follow standard **UML conventions**.

---

## Architecture Summary

The HBnB Evolution application follows a **layered architecture**:

- **Presentation Layer**  
  Handles API requests and responses.

- **Business Logic Layer**  
  Contains domain models and business rules, exposed through a facade.

- **Persistence Layer**  
  Manages data storage and retrieval.

This design ensures:
- Clear separation of concerns
- Maintainability and scalability
- Flexibility for future extensions

---

## Notes

- This part contains **documentation only** — no implementation code.
- The documentation is intended to guide:
  - API design (Part 2)
  - Database persistence (Part 3)

---

## Author

Cristian Acevedo  
HBnB Evolution Project  
Holberton School
