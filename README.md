# SETGruppe11HIOF

### **SETGruppe11HIOF - Software Engineering Project, Fall 2024**

## **Table of Contents**

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Usage](#usage)
6. [License](#license)
7. [Contact](#contact)

---

### **Project Overview**

This project is part of the Software Engineering course at Østfold University College (HIOF). It is developed by Group 11, consisting of 5(4 in the end..) team members, and aims to develop an MVP for the task at hand. This year's task revolves around developing a smart home prototype that can be used by "everyone", even your everyday non-tech-savvy citizen.

The focus of this project is to apply software development principles and best practices, including version control, code reviews, and agile project management. We use Git and GitHub to collaborate and manage our project efficiently.

---

### **Features**

The features of our Smart Home MVP include: 

- Smart Thermostat management: adjust and monitor room temperature, change modes for the thermostat, real-time updates of thermostat settings and automatic data saving to the database. 

- Smart Bulb management: Control brightness and colour of your smart bulbs, toggle on/off. 

- Car charger management: Start and stop charging through the interface. Track power consumption and estimated charge time remaining.

- Room specific device control: Link smart devices to rooms for better organisation. 

- Weather integration: get real time weather data based on the user's location. 

- User-friendly interface: Intuitive and simple navigation. Accessible device settings and control pages that require minimal learning from the user. Easily add new devices. 

- Ligth/Dark mode: Choose your preferred interface mode, light or dark. 


---

### **Technologies Used**

- **Programming Language: Python
- **Frameworks/Libraries: Django, Django Crispy Forms. 
- **Database: Sqlite3db (Django)
- **Version Control: Git and GitHub
- **Other Tools: Requests, Crispy-Bootstrap5, pip and virtual environment. 

---

### **Installation**

To run this project locally, follow these steps:

1. First and foremost: Python installation is required:  

- Go to the following link for downloading python: [Download Python](https://www.python.org/downloads)

 Installation of PyCharm IDE is advisable, but not necessary. 30-day free trial is given through JetBrains Official: 

[Download Pycharm](https://www.jetbrains.com/pycharm/download/?section=mac) NB! Remember to choose the correct version for your operating system.  



2. Clone the repository: Use the built in terminal in PyCharm or the native terminal on your computer:

   Type in: git clone https://github.com/StefanBStrand/SETGruppe11HIOF.git

3. Navigate to the project directory via the terminal:
  
   cd SETGruppe11HIOF

4. Create a virtual environment (venv): 

 Run this command in the terminal: python -m venv venv

 Activate the virtual environment:

For Windows: venv\Scripts\activate

For Mac/linux: source venv/bin/activate

5. Install dependencies:

 Run this command in the terminal: pip install requirements.txt. 

This will install the following: 

asgiref             3.8.1
certifi             2024.8.30
charset-normalizer  3.4.0
crispy-bootstrap5   2024.10
Django              5.1.1
django-crispy-forms 2.3
djangorestframework 3.15.2
idna                3.10
pip                 24.3.1
python-decouple     3.8
requests            2.32.3
setuptools          68.2.0
sqlparse            0.5.1
tzdata              2024.1
urllib3             2.2.3
wheel               0.41.2


6. Start the project:
  
 When all the above requirements are met, you can now run: python manage.py runserver

 This command will start the server so that the prototype can be inspected and tested. 

 In your browser, type in the following get to the home page: http://127.0.0.1:8000

---

### **Usage**

Now that you have arrived at the home page, the rest should be more or less self explanatory. Try clicking some icons/buttons, follow any instructions that might be present in the interface. 
---


### **License**

This project is licensed under the [MIT License]. See the [LICENSE](LICENSE) file for more details.

---

### **Contact**

For any questions or issues, please contact:

- **Project Lead:** Stefan B Strand. Mail: stefanb@hiof.no || Susanne Svendsrud. Mail: Susanne.svendsrud@hiof.no || Joachim L Christiansen. Mail: joachim.l.christensen@hiof.no || Sebastian Hansen. Mail: Sebastian.hansen@hiof.no
- **GitHub Repository:** [https://github.com/StefanBStrand/SETGruppe11HIOF](https://github.com/StefanBStrand/SETGruppe11HIOF)
