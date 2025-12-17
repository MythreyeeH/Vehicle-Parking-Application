# Vehicle Parking Management System

A full-stack web application designed to optimize urban parking resource allocation. Built using the **MVC (Model-View-Controller)** architectural pattern, the system provides a robust interface for both administrators and users to manage real-time parking reservations and analytics.

The system improves parking utilization efficiency while reducing manual intervention and billing errors.

---

## Key Features

* **Role-Based Access Control:** Separate workflows and dashboards for Admins and Users using Flask Sessions.
* **Real-Time Monitoring:** Dynamic tracking of parking spot availability and occupancy.
* **Automated Billing:** Precision cost calculation based on `datetime` tracking and location-specific hourly rates.
* **Data Visualization:** Automated generation of revenue and occupancy trends using `Matplotlib`.
* **Relational Persistence:** A normalized SQLite database ensuring data integrity and reduced redundancy.

---

## Architecture & Design

The project follows the **MVC Paradigm** to ensure scalability and separation of concerns:

* **Model (`models/model.py`):** Defines the relational schema using **Flask-SQLAlchemy (ORM)**.
* **View (`templates/`):** Dynamic UI rendered via **Jinja2** templates and styled with **CSS**.
* **Controller (`controllers/controller.py`):** Manages routing logic, session handling, and business rules.

### Database Schema (Normalized)
The database is designed to reduce redundancy and ensure integrity through relational tables:
1.  **Users/Admins:** Stores secure credentials and profile data.
2.  **Parking Lots:** Defines locations, pricing, and total capacity.
3.  **Parking Spots:** Tracks individual spot status (occupied/vacant) linked to parent lots.
4.  **Reservations:** Logs transaction history, timestamps, and calculated costs using composite keys.

---

## Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python, Flask |
| **Database** | SQLite, Flask-SQLAlchemy (ORM) |
| **Data Analytics** | Matplotlib, OS Library |
| **Frontend** | HTML5, CSS3, Jinja2 Templating |
| **Logic** | Datetime API (for temporal calculations) |

---

## Future Enhancements
- Integration with real-time sensors or IoT-based occupancy detection
- Migration to a scalable cloud-based database
