# **HBnB Evolution – Part 1: Technical Documentation**

---

## **1. Context and Objective**

**HBnB Evolution** is a simplified AirBnB-like application. This technical documentation provides a **blueprint for its architecture, business logic, and interactions**.  

**Objective:**  

- Ensure clarity in the **three-layered design**.  
- Document **entity relationships and API flows**.  
- Provide a guide for the **implementation phases**.

---

## **2. Architecture Overview**

HBnB Evolution follows a **three-layer architecture**:  

**1. Presentation Layer (Services / API)**  

- Handles user interaction.  
- Provides API endpoints for operations such as user registration, place listing, review submission, etc.  
- Communicates with the Business Logic Layer **through a Facade interface**.

**2. Business Logic Layer (Models / Core Logic)**  

- Contains the core models: `User`, `Place`, `Review`, `Amenity`.  
- Implements business rules:  
  - Reviews must belong to a user and a place.  
  - Places belong to an owner.  
- Exposes a **Facade** for simplified interaction with the Presentation Layer.

**3. Persistence Layer (Database / Repositories)**  

- Responsible for storing and retrieving data from the database.  
- Provides CRUD operations via Repository or DAO classes.  

**Key Design Principle:**  

- **Facade Pattern:**  
  - Presentation Layer calls **a single interface (`HbnbFacade`)** instead of interacting with each model.  
  - Reduces coupling, simplifies API calls, and enforces business rules consistently.

---

## **3. High-Level Package Diagram**

This diagram illustrates the three layers and their interactions via the **Facade Pattern**:

```mermaid
classDiagram
%% === Presentation Layer ===
class PresentationLayer {
    <<package>>
    +UserService
    +PlaceService
    +ReviewService
    +AmenityService
    +APIEndpoints
}

%% === Business Logic Layer ===
class BusinessLogicLayer {
    <<package>>
    +User
    +Place
    +Review
    +Amenity
    +HbnbFacade
}

%% === Persistence Layer ===
class PersistenceLayer {
    <<package>>
    +UserRepository
    +PlaceRepository
    +ReviewRepository
    +AmenityRepository
    +DatabaseConnection
}

%% === Layer Relationships ===
PresentationLayer --> BusinessLogicLayer : <<uses>> via Facade
BusinessLogicLayer --> PersistenceLayer : <<uses>> for CRUD operations

