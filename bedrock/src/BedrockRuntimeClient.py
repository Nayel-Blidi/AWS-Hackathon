import boto3
import json
import os, sys


BEDROCK_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
if __name__ == "__main__":
    sys.path.append(os.path.dirname(BEDROCK_DIR_PATH))

from constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN


class BedrockRuntimeClient():
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

        self.client = boto3.client(service_name='bedrock-runtime', 
                                   aws_access_key_id=aws_access_key_id, 
                                   aws_secret_access_key=aws_secret_access_key, 
                                   aws_session_token=aws_session_token,
                                   region_name='us-east-1')

    def _invoke_bedrock_model(self, model_id: str, prompt_text: str, display: bool = False):
        """
        Function to interact with an AWS Bedrock model using boto3.
        Args:
            model_id (str): The ID of the model in AWS Bedrock to invoke.
            prompt_text (str): The input text to send to the model.
        
        Returns:
            dict: Response from the AWS Bedrock model.
        """
        try:
            # Payload for the model invocation
            payload = {
                "inputText": prompt_text
            }
            
            # Invoke the model on AWS Bedrock
            response = self.client.invoke_model(
                modelId=model_id,  # Specify the Bedrock model ID
                accept='application/json',  # Specify response format
                contentType='application/json',  # Specify content type for the request
                body=json.dumps(payload)  # Convert the payload to JSON string
            )
            
            response_body = json.loads(response['body'].read())
            if display: print(response_body)

            return response_body
        
        except Exception as e:
            print(f"An error occurred while invoking the model: {str(e)}")
            return None


    def _list_foundation_models(self, display: bool = False):
        """
        List the available Amazon Bedrock foundation models.

        :return: The list of available bedrock foundation models.
        """

        response = self.client.list_foundation_models()
        models = response["modelSummaries"]
        if display: print(models)

        return models
    



if __name__ == "__main__":
    model_id = 'amazon.titan-text-lite-v1' 
    prompt_text = 'Give me a recipee of fish and chips?'
    
    bedrock_cli = BedrockRuntimeClient()
    response = bedrock_cli._invoke_bedrock_model(model_id, prompt_text, display=True)
    
