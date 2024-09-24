import sys, os
import numpy as np

from constants import MAIN_DIR

from s3 import S3Client
from bedrock import BedrockKnowledgeBase, BedrockRuntimeClient


def welcome_user():
    print("\nQualificationAssistant >> To perform a Standard similarities search, enter '1' or 'similarity'.")
    print("QualificationAssistant >> To generate a TestPlan for a Standard, enter '2' or 'generation'.")
    print("QualificationAssistant >> To compare a TestPlan and a SupplierReport, enter '3' or 'comparison'.")
    print("QualificationAssistant >> To exit the bot, enter '0' or 'exit'.")
    return input("QualificationAssistant >> Your request: ")


def use_case_1():
    """
    This use case retreives all Standards similar to the written content present in the inputs/ folder.
    """

    # The prompt is the input/ folder content
    print("\nQualificationAssistant >> Reading all files in _inputs/.")
    knowledge_client = BedrockKnowledgeBase()
    files_content = knowledge_client._read_files_from_folder(os.path.join(MAIN_DIR, "_inputs"))
    if not files_content: 
        print("QualificationAssistant >> No valid file found in _inputs/.")
        return False

    # Pompt is embedded and compared to similar content 
    print("QualificationAssistant >> Comparing inputs with the existing database.")
    bucket_name = "stagiaire-alternant" # TODO REPLACE WITH stagiaire-alternant-standards
    s3_locations = knowledge_client.retreive_similar(prompt=files_content)
    s3_locations = np.unique([location.split(sep=bucket_name+"/", maxsplit=1)[-1] 
                                for location in knowledge_client.retreive_similar(prompt=files_content)]).tolist()

    # Similar content is downloaded into the outputs/ folder
    s3_cli = S3Client(bucket_name=bucket_name)
    s3_cli._empty_folder(os.path.join(MAIN_DIR, "_outputs"))
    s3_cli.download_files(keys=s3_locations, 
                            paths=[os.path.join(MAIN_DIR, "_outputs", os.path.basename(file)) for file in s3_locations])
    print(f"QualificationAssistant >> Retreived and saved {len(s3_locations)} files into _outputs/")
    return True


def use_case_2():
    """
    This use case retreives all Standards and TestPlans similar to the Standard content present in the inputs/ folder
    and generates a TestPlan for the input Standard.
    """

    # The prompt is the input/ folder content
    print("\nQualificationAssistant >> Reading all files in _inputs/.")
    knowledge_client = BedrockKnowledgeBase()
    files_content = knowledge_client._read_files_from_folder(os.path.join(MAIN_DIR, "_inputs"))
    if not files_content: 
        print("QualificationAssistant >> No valid file found in _inputs/.")
        return False

    # Pompt is embedded and compared to similar content 
    print("QualificationAssistant >> Comparing inputs with the existing database.")
    s3_locations = knowledge_client.retreive_similar(prompt=files_content)
    s3_locations = np.unique([location.split(sep="stagiaire-alternant-standards"+"/", maxsplit=1)[-1] 
                                for location in knowledge_client.retreive_similar(prompt=files_content)]).tolist()

    # Similar Standards are downloaded into the outputs/ folder
    s3_cli = S3Client(bucket_name="stagiaire-alternant-standards")
    s3_cli._empty_folder(os.path.join(MAIN_DIR, "_outputs"))
    print("QualificationAssistant >> Dowloading RAG Standards.")
    s3_cli.download_files(keys=s3_locations, 
                            paths=[os.path.join(MAIN_DIR, "_outputs", f"standard_{os.path.basename(file)}") for file in s3_locations])
    print(f"QualificationAssistant >> Retreived and saved {len(s3_locations)} Standards files into _outputs/")

    # Similar TestPlans are downloaded into the outputs/ folder
    s3_cli = S3Client(bucket_name="stagiaire-alternant-testplans")
    print("QualificationAssistant >> Dowloading RAG TestPlans.")
    s3_cli.download_files(keys=s3_locations, 
                            paths=[os.path.join(MAIN_DIR, "_outputs", f"testplans_{os.path.basename(file)}") for file in s3_locations])
    print(f"QualificationAssistant >> Retreived and saved {len(s3_locations)} TestPlans files into _outputs/")

    # Now the downloaded RAG content is merged into a model prompt 
    knowledge_client = BedrockKnowledgeBase()
    rag_content = knowledge_client._read_files_from_folder(os.path.join(MAIN_DIR, "_outputs"))
    input_content = knowledge_client._read_files_from_folder(os.path.join(MAIN_DIR, "_input"))
    prompt = rag_content \
             + "\n Using these standards and test plans file examples, I want you to generate a test plan for the following file:" \
             + input_content \
             + "\n Now generate a test plan similar to the previous examples for this input."
    
    # Using this RAG prompt, a GPT model generates an output
    runtime_client = BedrockRuntimeClient()
    response_text = runtime_client._invoke_bedrock_model(model_id='amazon.titan-text-lite-v1', prompt_text=prompt)
    with open(os.path.join(MAIN_DIR, "_generated_TestPlan.txt")) as f:
        f.write(response_text)
    return True


def use_case_3():
    """
    This use case loads a TestPlan and an SupplierReport from the inputs/ folder and will
    generate a report on the coherence of the two.
    """

    # The TestPlan and SupplierReport are loaded from the inputs/ folder
    knowledge_client = BedrockKnowledgeBase()
    file_content = knowledge_client._read_files_from_folder(os.path.join(MAIN_DIR, "_inputs"))
    prompt = file_content \
             + "This is the content of a test plan and the corresponding supplier report." \
             + "Compare the two, highlight the differences, and make a general report on the differences and issues raised."
    
    # A NLP model will compare the contents using the created augmented prompt
    runtime_client = BedrockRuntimeClient()
    response_text = runtime_client._invoke_bedrock_model(model_id='amazon.titan-text-lite-v1', prompt_text=prompt)
    with open(os.path.join(MAIN_DIR, "_generated_Comparison.txt")) as f:
        f.write(response_text)
    return True


if __name__ == "__main__":

    if not os.path.exists(os.path.join(MAIN_DIR, "_outputs")): os.mkdir(os.path.join(MAIN_DIR, "_outputs"))
    if not os.path.exists(os.path.join(MAIN_DIR, "_inputs")): os.mkdir(os.path.join(MAIN_DIR, "_inputs"))

    print("\nQualificationAssistant >> Hello. I am \033[1mQualificationAssistant\033[0m, an AI bot",
          "that helps you process industry standards and regulatory requirements.")

    while True:
        # A reminder of the available use cases.
        use_case = welcome_user()

        if use_case not in ["0", "1", "2", "3", "exit", "similarity", "generation", "comparison"]:
            # Invalid input
            print("\nQualificationAssistant >> Invalid request, please enter a valid input. Type 'exit' to leave. \n")
        else:
            # Valid use case
            if use_case in ["0", "exit"]:
                # To leave the app
                print("\nQualificationAssistant >> Bye o7.\n")
                break

            if use_case in ["1", "similarity"]:
                # Retreives files similar to the text found in inputs/. You can also 'prompt' the
                # model by writting a simple .txt file in inputs/ with your querry. 
                use_case_1()
                
            if use_case in ["2", "generation"]:
                # Generates a TestPlan for a given Standard by using a database knowledge
                use_case_2()

            if use_case in ["3", "comparison"]:
                # Compares a TestPlan and a SupplierReport
                use_case_3()
