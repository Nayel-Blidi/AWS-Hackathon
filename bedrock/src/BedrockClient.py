import boto3
import json
import os, sys


BEDROCK_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
if __name__ == "__main__":
    sys.path.append(os.path.dirname(BEDROCK_DIR_PATH))

from constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN


class BedrockClient():
    """
    Standard S3 class with all purpose methods.
    """

    def __init__(self, 
                 aws_access_key_id:str = AWS_ACCESS_KEY,
                 aws_secret_access_key:str = AWS_SECRET_KEY,
                 aws_session_token: str = AWS_SESSION_TOKEN,
                 ) -> None:
        """
        Initiates a connection to a given Bedrock model.

        Args
        ----
        - aws_access_key_id: the user's access key id (private)
        - aws_secret_access_key: the user's access key (private)

        Note
        ----
        - `key` kwarg refers to a cloud path
        - `path` kwarg refers to a local path
        """

        self.bedrock_client = boto3.client(service_name='bedrock', 
                                   aws_access_key_id=aws_access_key_id, 
                                   aws_secret_access_key=aws_secret_access_key, 
                                   aws_session_token=aws_session_token,
                                   region_name='us-east-1')

    def list_foundation_models(self, display: bool = False):
        """
        List the available Amazon Bedrock foundation models.

        :return: The list of available bedrock foundation models.
        """

        response = self.bedrock_client.list_foundation_models()
        models = response["modelSummaries"]
        if display: print(models)

        return models
        
    def _read_files_from_folder(self, folder_path: str):
        """
        Reads all the files in a folder and return the concatenated content. Skips invalid files.
        """

        concatenated_content = ""
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        concatenated_content += f"\nThis is the content of a file named {os.path.basename(file_path)}:\n" + content + "\n"
                except (UnicodeDecodeError, OSError) as e:
                    print(f"Skipping non-compatible file: {filename} - {str(e)}")
        
        return concatenated_content





if __name__ == "__main__":
    model_id = 'amazon.titan-text-lite-v1' 
    prompt_text = 'What is the future of AI in aerospace?'
    prompt_text = 'Give me a recipee of fish and chips?'
    
    bedrock_cli = BedrockClient()
    bedrock_cli.list_foundation_models()
    
