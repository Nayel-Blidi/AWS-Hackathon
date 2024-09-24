import boto3
import json
import os, sys


BEDROCK_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
if __name__ == "__main__":
    sys.path.append(os.path.dirname(BEDROCK_DIR_PATH))

from constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN, KNOWLEDGE_BASE_ID
from bedrock.src.BedrockClient import BedrockClient

class BedrockKnowledgeBase(BedrockClient):
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
        super().__init__(aws_access_key_id, aws_secret_access_key, aws_session_token)

        self.bedrock_agent_client = boto3.client(service_name='bedrock-agent-runtime', 
                                   aws_access_key_id=aws_access_key_id, 
                                   aws_secret_access_key=aws_secret_access_key, 
                                   aws_session_token=aws_session_token,
                                   region_name='us-east-1')
        
        return None


    def retreive_similar(self, prompt: str):
        """
        Embeds a prompt and returns the S3 location of similar references.
        """

        model_id = "amazon.titan-text-premier-v1:0"
        model_arn = f'arn:aws:bedrock:us-east-1::foundation-model/{model_id}'

        models = self.list_foundation_models()
        # print([model["modelId"] for model in models if model["modelId"].startswith("amazon")])
        model_arn = [model["modelArn"] for model in models if model["modelId"] == model_id][0]

        response = self.bedrock_agent_client.retrieve_and_generate(
            input={
                'text': prompt
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': "UQKMGD9ARY",
                    'modelArn': model_arn
                }
            }
        )

        response_files = [ref["retrievedReferences"] for ref in response["citations"]]
        response_files = [ref[0]["location"]["s3Location"]["uri"] for ref in response_files]
        
        return response_files
        
    def list_agent_knowledge_bases(self, agent_id, agent_version):
        """
        List the knowledge bases associated with a version of an Amazon Bedrock Agent.

        :param agent_id: The unique identifier of the agent.
        :param agent_version: The version of the agent.
        :return: The list of knowledge base summaries for the version of the agent.
        """

        knowledge_bases = []

        paginator = self.client.get_paginator("list_agent_knowledge_bases")
        for page in paginator.paginate(
                agentId=agent_id,
                agentVersion=agent_version,
                PaginationConfig={"PageSize": 10},
        ):
            knowledge_bases.extend(page["agentKnowledgeBaseSummaries"])

        return knowledge_bases
    



if __name__ == "__main__":

    bedrock_cli = BedrockKnowledgeBase()  
    response = bedrock_cli.retrieveAndGenerate(document_text="a recipee about pumpkins")  
    print(response)

