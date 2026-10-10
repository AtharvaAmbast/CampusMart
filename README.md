# CampusMart

CampusMart is a robust, Python-based campus marketplace web application designed to facilitate peer-to-peer commerce and communication within a university ecosystem. It provides a centralized platform for students to list items, manage their profiles, and negotiate purchases through an integrated messaging system.

## Technical Architecture & Stack

The project operates on a standard Model-View-Controller (MVC) architecture, optimized for lightweight deployment and rapid development.

* **Backend Framework:** Python with Flask handling the core routing, business logic, and session management.
* **Frontend:** HTML5 and CSS rendered dynamically server-side using the Jinja2 templating engine.
* **Database:** SQLite, providing a lightweight, disk-based database ideal for standard CRUD operations and marketplace relationships.
* **Object-Relational Mapping (ORM):** Database schemas and relationships are defined programmatically via `models.py`, likely utilizing SQLAlchemy to map Python objects to SQLite tables.



## Directory Structure & Core Files

The repository is structured to separate application logic, database models, and presentation layers:

* `app.py`: The main application entry point. This file initializes the Flask application, configures the SQLite database connection, establishes user sessions, and defines all backend routing endpoints (e.g., `/`, `/login`, `/item/<id>`).


* `models.py`: Contains the database schema definitions. It defines the core tables necessary for the application's functionality:


* **User Model:** Handles authentication data, linking users to their listed items and messages.
* **Item Model:** Stores marketplace listings, including descriptions, pricing, and foreign keys associating the item with a specific seller (User).
* **Message/Chat Model:** Manages direct user-to-user communication for the inbox and chat interfaces.


* `requirements.txt`: The dependency manifest detailing the exact versions of Flask, Jinja2, database connectors, and any other necessary Python libraries.


* `templates/`: The directory housing all Jinja2 HTML templates:


* `base.html`: The foundational template containing the HTML `<head>`, navigation bars, and structural layout inherited by all other pages.


* `index.html`: The main landing page displaying the feed of available marketplace items.


* `item.html`: A dynamic view rendering the specific details, price, and seller information of an individual listing.


* `login.html` & `register.html`: The user authentication interfaces mapping to backend session handlers.


* `profile.html`: The user dashboard for managing active listings and updating account details.


* `inbox.html` & `chat.html`: The user interface for the internal messaging system, allowing users to view ongoing conversations and send direct messages regarding items.





## Local Installation & Setup

The following instructions are configured specifically for a Windows environment.

### Prerequisites

* Python 3.8 or higher installed and added to your system PATH.
* Git installed (if cloning the repository).

### Installation Steps

1. **Get the Code:** Download the project files and extract them, or clone the repository using Git.
2. **Navigate to the Directory:** Open Command Prompt in the project's root directory containing the source code
3. **Initialize a Virtual Environment:** It is highly recommended to use a virtual environment to prevent dependency conflicts with other Python projects on your machine.
```cmd
python -m venv venv

```


4. **Activate the Virtual Environment:**
```cmd
venv\Scripts\activate

```


*(Note: Your command prompt should now display `(venv)` at the beginning of the line).*

5. **Install Dependencies:** Read the `requirements.txt` file and install the necessary packages:


```cmd
pip install -r requirements.txt

```


## Launching the Application

1. Ensure your Command Prompt/PowerShell is currently in the project root and the `(venv)` is activated.
2. Execute the primary Python script to start the Flask development server:


```cmd
python app.py

```


3. The terminal will output the local network address the server is listening on. By default, Flask runs on port 5000.
4. Open your preferred web browser and navigate to:
```text
http://127.0.0.1:5000

```
