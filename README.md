# AWS-Hackathon

## Quick start
1. Clone the repo

``your_path> git clone https://github.com/Nayel-Blidi/AWS-Hackathon``

2. Create a venv

``your_path/aws-hackathon> python -m venv .venv``

3. Install the requirements

``your_path/aws-hackathon> pip install -r requirements.txt``

## Loading secrets

4. Copy the ``.env_sample`` template into a new ``.env`` file. The secrets in the ``.env`` file will be loaded into and imported from ``constants.py``

5. Fill the empty fields with you own secrets.
    - AWS keys are updated hourly, make sure to update those regularly
    - You need to update all three access_key, secret_key, and session_token

## Le code (battle plan)

##### ISSUE 1: Develop a method to identify and extract requirements from the Standard and similar standards/Test Plans.

 Embedding du RAG, qui permet de comparer un standard donné par l'utilisateur, à une BDD de standards. L'output permet de récupérer les autres standards existants similaires, et éventuelles leurs test plans

S3: 
- standards/exemples_de_standards + vectorisation
	--> vectorisé dans une "knowledge base" issue de l'embedding de données connues
	--> on peut ainsi comparer un nouveau standard à des standards existants sur le S3
	
- testplan/exemple_de_testplan
	--> des fichiers testplan existants
	--> peuvent être issus de standards de référence

Bedrock:
- On a un modèle d'embedding
- On met en entrée un standard, le modèle retourne des standards similaires, et on peut récupérer les test plans associés s'ils existent 

##### ISSUE 2: Generate a Test Plan document for a specific Standard based on the extracted information.

On récupère les standars et testplans similaires extraits par la ISSUE1, et on demande à générer un test plan:

context + prompt

{standards_similaires} + {test_plans_similaire} + "à partir de ces exemples de standards, génère moi un test plan pour le standard suivant:" + {standard à traiter}

##### ISSUE 3: Compare the Supplier Test Report with the Test Plan and generate an analysis report highlighting the compliance to the Test Plan.

Chatbot:

{test plan} + {supplier test report} + "compare moi ces deux documents et retourne les paramètres qui ne correspondent pas entre les deux"


##### ISSUE 4: API python main

1. python main.py + standard
	1. input standard_file à évaluer
	2. retourne les standards similaires
	3. génère et retourn un test_plan
3. python main.py + report
	1. input test_plan
	2. input supplier_report
	3. génère et retourne une comparaison du test plan à un report
