import os, sys
import pandas as pd
import numpy as np
import random
from tqdm import tqdm

S3_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
if __name__ == "__main__":
    sys.path.append(os.path.dirname(S3_DIR_PATH))
    
from constants import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_SESSION_TOKEN
from s3 import S3Client

class S3CookingRecipees(S3Client):
    """
    Test for RAG embedding
    """

    def __init__(self, aws_access_key_id: str = AWS_ACCESS_KEY,
                  aws_secret_access_key: str = AWS_SECRET_KEY,
                    bucket_name: str = "stagiaire-alternant", 
                 aws_session_token: str = AWS_SESSION_TOKEN,
                    authorized_access: str = "") -> None:
        super().__init__(aws_access_key_id, aws_secret_access_key, aws_session_token, bucket_name, authorized_access)

    
    def sample_csv(self, sample_size: int = 1e4, csv_path: str = os.path.join(S3_DIR_PATH, "src", "RecipeNLG_dataset.csv")):

        sampled_df = pd.DataFrame()  # Initialize an empty DataFrame to hold the samples
        
        chunk_list = []  
        for chunk in pd.read_csv(csv_path, chunksize=1e6):
            chunk_sample = chunk.sample(frac=sample_size/len(chunk), random_state=42)
            chunk_list.append(chunk_sample)
        
        sampled_df = pd.concat(chunk_list)
        sampled_df = sampled_df.sample(frac=1).reset_index(drop=True)

        sampled_df.to_csv(os.path.join(os.path.dirname(csv_path), "sampled_dataset.csv"), index=False)

        return sampled_df
    
    def csv_to_txt(self, csv_file = os.path.join(S3_DIR_PATH, "src", "sampled_dataset.csv")):


        df = pd.read_csv(csv_file)

        skipped_files = 0
        for idx, row in tqdm(df.iterrows()):
            file_name = f"row_{idx}.txt"
            file_path = os.path.join(self.temp_folder_path, file_name)
            
            # Combine the column values into a text format
            content = (
                f"Title: {row['title']}\n"
                f"Ingredients: {row['ingredients']}\n"
                f"Directions: {row['directions']}\n"
                f"Link: {row['link']}\n"
                f"Source: {row['source']}\n"
                f"NER: {row['NER']}\n"
            )
            
            # Step 4: Write the content to a .txt file
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
            except:
                skipped_files += 1

        print("files skipped", skipped_files)

        return None
        

if __name__ == "__main__":

    s3cooking = S3CookingRecipees()
    # s3cooking.sample_csv()
    # s3cooking.csv_to_txt()
    # keys = s3cooking.list_keys(key="recipees/")
    # s3cooking.delete_keys(keys=keys)
    keys = [f"recipees/recipee_{recipee_id}.txt" for recipee_id, file in enumerate(os.listdir(s3cooking.temp_folder_path))]
    paths = [os.path.join(s3cooking.temp_folder_path, file) for file in os.listdir(s3cooking.temp_folder_path)]
    s3cooking.upload_files(keys=keys, paths=paths)
