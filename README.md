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
