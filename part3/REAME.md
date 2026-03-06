Part 3 Introduction: Advanced Backend with Authentication and Database Integration

Welcome to Part 3 of the HBnB Project. In this stage, you will upgrade the application's backend by adding user authentication, authorization, and database support. Instead of storing data in memory, you will integrate a relational database using SQLAlchemy and SQLite for development, and later configure MySQL for production environments.

The goal of this phase is to make the backend secure, persistent, and scalable, preparing the application for real-world deployment.

Project Objectives
Authentication and Authorization

You will implement JWT-based authentication using Flask-JWT-Extended to secure API access. Additionally, you will introduce role-based access control using the is_admin attribute to limit certain endpoints to administrators only.

Database Integration

The existing in-memory storage will be replaced with a SQLite database for development. SQLAlchemy will be used as the ORM to manage database interactions, and the system will later be configured to use MySQL in production.

Persistent CRUD Operations

All existing CRUD operations will be refactored to interact with the database layer, ensuring that data persists between application sessions.

Database Design and Visualization

You will design the application's database schema and represent it visually using Mermaid.js diagrams. This will ensure all relationships between entities are clearly defined.

Data Validation and Consistency

Model-level validations and constraints will be implemented to maintain data integrity and consistency within the database.

Learning Goals

By completing this part of the project, you will learn how to:

Implement JWT authentication to protect API endpoints and manage user sessions.

Apply role-based authorization to restrict certain actions based on user roles (regular users vs administrators).

Replace temporary in-memory storage with a persistent SQLite database using SQLAlchemy.

Configure MySQL as the database for production environments.

Design and visualize a relational database schema using Mermaid.js.

Ensure the backend is secure, scalable, and reliable for real-world use cases.

Project Context

In the earlier stages of the project, the application relied on in-memory storage, which is useful for testing and prototyping but unsuitable for production systems.

In Part 3, you will transition to SQLite, a lightweight relational database suitable for development environments. At the same time, you will prepare the system to support MySQL, which is more appropriate for production deployments.

You will also implement JWT-based authentication, ensuring that only verified users can access certain API endpoints. Additionally, role-based access control will be introduced to manage permissions between regular users and administrators.

This phase provides practical experience with real-world backend development practices, including authentication systems and database management.

Project Resources

The following resources will help guide you through this stage of the project:

Flask-JWT-Extended Documentation – JWT Authentication

SQLAlchemy Documentation – ORM usage and database interaction

SQLite Documentation – Development database system

MySQL Documentation – Production database setup

Flask Official Documentation – Backend framework reference

Mermaid.js Documentation – Creating ER diagrams

Project Structure

The tasks in this part are organized progressively to help you build a fully functional and secure backend system.

Update the User Model

You will modify the User model to include secure password storage using bcrypt and update the registration process accordingly.

Implement JWT Authentication

JWT tokens will be used to protect API endpoints and ensure that only authenticated users can access protected resources.

Add Endpoint Authorization

You will introduce role-based permissions to restrict specific actions to administrators only.

Integrate SQLite Database

Replace the existing in-memory storage system with a SQLite database during development.

Map Entities with SQLAlchemy

Existing entities such as User, Place, Review, and Amenity will be mapped to database tables using SQLAlchemy, including their relationships.

Prepare for MySQL Deployment

Configure the application so it can use SQLite during development and MySQL in production environments.

Design the Database Schema

Create Entity-Relationship diagrams using Mermaid.js to visualize the structure of the database and the relationships between entities.

Each step builds upon previous work to ensure the backend evolves from a simple prototype into a production-ready system.

By the end of Part 3, your backend will use a secure authentication system and a persistent relational database, ensuring that only authorized users can access or modify specific resources. These improvements reflect industry-standard backend practices used in modern web applications.
