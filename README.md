\# CampusSentry NLP



\### An NLP System for Classifying, Locating and Assessing the Severity of Campus Incident Reports



\## 1. Project Overview



CampusSentry NLP is a university project that applies Natural Language Processing (NLP) and machine learning to campus incident reporting.



Campus incidents may be reported informally and may contain English, Shona, or a mixture of both languages. CampusSentry processes submitted reports and produces structured information to help staff understand and review incidents.



The system includes a reporting interface, an NLP backend, trained machine learning models, a database, and a staff dashboard.



\## 2. Main Features



\- Submit campus incident reports through a web interface.

\- Classify incidents into categories using a trained machine learning model.

\- Estimate incident severity.

\- Identify the language of a report.

\- Extract relevant entities and potential campus locations.

\- Assign a reference number to each submitted incident.

\- Store incidents in an SQLite database.

\- View submitted incidents through a staff dashboard.

\- Filter and search incident records.

\- Update incident statuses.



\## 3. Technologies Used



\*\*Backend and NLP\*\*

\- Python

\- FastAPI

\- Uvicorn

\- scikit-learn

\- Joblib

\- spaCy and NLTK

\- SQLite



\*\*Frontend\*\*

\- React

\- Vite

\- Tailwind CSS

\- Lucide React



\*\*Research and experimentation\*\*

\- Jupyter

\- pandas

\- NumPy

\- Matplotlib

\- Seaborn

\- Transformers and related machine learning libraries



\## 4. Project Structure



```text

campussentry/

├── api.py

├── requirements.txt

├── README.md

├── app/

├── data/

│   └── campussentry.db

├── frontend/

│   ├── package.json

│   └── src/

├── models/

│   ├── category.joblib

│   ├── language.joblib

│   └── severity.joblib

├── notebooks/

├── reports/

└── src/

&#x20;   ├── pipeline.py

&#x20;   ├── preprocess.py

&#x20;   ├── ner\_rules.py

&#x20;   └── storage.py

```



\## 5. Requirements



Install the following before running the project:



\- Python 3.12 recommended

\- Node.js with npm

\- Git



Internet access is required to clone the repository and install dependencies.



\## 6. Download the Project



Clone the repository:



```bash

git clone https://github.com/pirikisibrighton/campussentry.git

cd campussentry

```



\## 7. Set Up the Python Backend



Create a virtual environment:



\*\*Windows PowerShell\*\*



```powershell

py -3.12 -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



If PowerShell blocks activation, use Command Prompt or run the virtual environment's Python executable directly.



Upgrade pip and install dependencies:



```powershell

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

```



\## 8. Start the Backend



From the project root, run:



```powershell

python -m uvicorn api:app --reload --port 8000

```



The API will be available at:



\- API: http://127.0.0.1:8000

\- Interactive API documentation: http://127.0.0.1:8000/docs

\- Health check: http://127.0.0.1:8000/api/health



Keep this terminal running.



\## 9. Set Up the Frontend



Open a second terminal:



```powershell

cd campussentry/frontend

npm ci

npm run dev

```



If you are already in the project root, the first command is unnecessary; run `cd frontend` instead.



Open the local URL displayed by Vite, normally:



http://localhost:5173



Keep the frontend terminal running as well.



\## 10. Test the Application



1\. Open the frontend in your browser.

2\. Navigate to the incident reporting page.

3\. Enter a descriptive incident report.

4\. Submit it and note the generated reference number.

5\. Open the staff dashboard.

6\. Check whether the incident appears with its predicted category, severity, language, location, and extracted entities.

7\. Test the search, filters, and incident status update features.



The backend can also be tested independently through the interactive API documentation at `/docs`.



\## 11. Database



The application uses SQLite to store submitted incident reports. The database is managed by the backend storage module.



If the database file is missing, initialise it using the project's storage initialisation function before running the application.



Keep backups of important incident data. Use synthetic or sample incident records for academic testing.



\## 12. Security and Limitations



This repository is an academic prototype and is not yet ready for production deployment.



\- Staff authentication and server-side authorisation are not currently implemented.

\- The staff dashboard and its API endpoints must not be exposed publicly with confidential incident data.

\- Incident classification, language detection, severity prediction, and entity extraction may produce incorrect results.

\- NLP predictions should be reviewed by authorised personnel before operational decisions are made.

\- The models' performance depends on the training data and the similarity of new reports to the examples used during development.



Future improvements include staff authentication, role-based access control, stronger input validation, expanded multilingual training data, and further model evaluation.



\## 13. Academic Purpose



CampusSentry NLP demonstrates how NLP and machine learning can be applied to semi-structured campus incident reports. It combines incident classification, language detection, severity estimation, entity extraction, persistent storage, and a web-based interface in one prototype.



\## 14. Repository



GitHub: https://github.com/pirikisibrighton/campussentry



