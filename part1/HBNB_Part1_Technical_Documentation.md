# HBnB Application: Three-Layer Architecture & Facade Pattern

## Objective
This document presents a high-level **package diagram** illustrating the **three-layer architecture** of the HBnB application and the **communication between layers** via the **facade pattern**. It provides a conceptual overview of the application's organization and interactions.

---

## 1. Layered Architecture Overview

The HBnB application is structured into three main layers:

### 1.1 Presentation Layer
- **Purpose:** Handles interaction between users and the application.  
- **Components:**  
  - Services: `UserService`, `PlaceService`, `ReviewService`  
  - API endpoints  
- **Responsibilities:**  
  - Accepts user requests  
  - Forwards requests to the **Business Logic Layer** via a **facade**  
  - Returns responses to users  

### 1.2 Business Logic Layer
- **Purpose:** Implements the core business rules and manages entities.  
- **Components:**  
  - Models: `User`, `Place`, `Review`, `Amenity`  
  - Facade: `HBnBFacade`  
- **Responsibilities:**  
  - Process business operations  
  - Interact with **Persistence Layer** for data storage/retrieval  
  - Expose a simplified interface to the **Presentation Layer**  

### 1.3 Persistence Layer
- **Purpose:** Handles data storage and retrieval.  
- **Components:**  
  - Data Access Objects (DAOs): `UserDAO`, `PlaceDAO`, `ReviewDAO`, `AmenityDAO`  
- **Responsibilities:**  
  - Perform CRUD operations on the database  
  - Serve requests from the **Business Logic Layer**  

---

## 2. Facade Pattern

The **facade pattern** is used to simplify interactions between the **Presentation Layer** and the **Business Logic Layer**:

- Provides a **single interface** (`HBnBFacade`) for all presentation services.
- Hides the complexity of models and persistence operations.
- Example methods: `createUser()`, `getPlaceDetails()`, `addReview()`.

---

## 3. Key Components by Layer

| Layer | Components |
|-------|------------|
| **Presentation Layer** | `UserService`, `PlaceService`, `ReviewService`, API Endpoints |
| **Business Logic Layer** | `HBnBFacade`, `User`, `Place`, `Review`, `Amenity` |
| **Persistence Layer** | `UserDAO`, `PlaceDAO`, `ReviewDAO`, `AmenityDAO` |

---

## 4. Communication Flow

1. **Presentation Layer → Facade:** All user requests go through `HBnBFacade`.
2. **Facade → Models:** Facade calls the relevant models to process business logic.
3. **Models → Persistence Layer:** Models or facade request data access objects to retrieve/store data.
4. **Persistence → Business Logic → Presentation:** Response flows back up through the layers.

---

## 5. Package Diagram (Mermaid)

```mermaid
%% Mermaid package diagram for HBnB three-layer architecture
flowchart TB
    subgraph Presentation_Layer [Presentation Layer]
        US[UserService]
        PS[PlaceService]
        RS[ReviewService]
        API[API Endpoints]
    end

    subgraph Business_Logic_Layer [Business Logic Layer]
        F[HBnBFacade]
        U[User]
        P[Place]
        R[Review]
        A[Amenity]
    end

    subgraph Persistence_Layer [Persistence Layer]
        UDAO[UserDAO]
        PDAO[PlaceDAO]
        RDAO[ReviewDAO]
        ADAO[AmenityDAO]
    end

    %% Communication arrows
    Presentation_Layer -->|uses facade| F
    F --> U
    F --> P
    F --> R
    F --> A
    U --> UDAO
    P --> PDAO
    R --> RDAO
    A --> ADAO
