# BioBank Project

The BioBank web-based application allows researchers to keep track of a Bio data inventory. 

This web app is also powered by a Generative A.I 3.5 Turbo GPT model in the backend, I have named "God's Eye". "God's Eye" continuously monitors, logs, and interprets every User action within the BioBank webapp, ensuring data security, data integrity and prompt incident response measures by the Administrator.

The interface can: 

1. View Bio data collections and their associated Samples data 🗂️
2. Add a New Collection ➕
3. Add or Delete new Sample ➕❌
4. Search & Filter any features of the Samples data 🔍
5. Manage Users from a dedicated Admin Portal (includes User Authentication) 👥🛠️
6. Visualize Donor Data Statistics 📊📈
7. Download a God's Eye Log Report 👁️📑

## Table of Contents
1. [Database Schema](#database-schema)
2. [OOP Class Diagram](#oop-class-diagram)
3. [Installation](#installation)
4. [Usage](#usage)


## Database Schema

I added a few more tables to the Database. Below is the **BioBank Database Schema**:

![BioBank Database Schema](/BioBank_database_schema.png)

## OOP Class Diagram

This project adheres to modern Object-Oriented Programming principles. For a detailed overview, refer to the  **Object-Oriented Programming Class Diagram**:

![OOP Class Diagram](/OOP_Class_Diagram.png)


## Installation

Follow these steps to install the project:

1. Clone the repository (Set up your own virtual environment if necessary):

   ```bash
   git clone https://github.com/emaseruka1/bio_bank_project.git

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt

## Usage

1.  Start the app by running:

    ```bash

    python app/main.py

2. Go to your localhost with the following url. (I advise that you use Google Chrome):

    http://localhost:5555

3. Login as Admin with these details:

    🆔 ID: 1
   
    👤 Username: Admin
   
    🔑 Password: Admin1
