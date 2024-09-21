
import boto3
import os
import sys
import threading
import gzip
from tqdm import tqdm
import pandas as pd
import numpy as np

SERVER_DIR_PATH = os.path.abspath(__file__).split("services")[0]
if __name__ == "__main__":
    sys.path.append(SERVER_DIR_PATH)

from main import AWS_KEY_ID, AWS_KEY_ACCESS

class S3Admin():
    """
    Management S3 superclass with enhanced methods.
    """

    def __init__(self) -> None:
        
        self.client = boto3.client(service_name='s3', 
                                   aws_access_key_id=AWS_KEY_ID, 
                                   aws_secret_access_key=AWS_KEY_ACCESS, 
                                   region_name='eu-west-1')
        
        # S3Client neeeds a working folder to download/upload files from a unique entry point
        self.temp_folder_path = os.path.join(SERVER_DIR_PATH, 'temp')
        if not os.path.exists(self.temp_folder_path):
            os.mkdir(self.temp_folder_path)
            print("S3Admin >> Temporary folder created:", self.temp_folder_path)


    def list_bucket(self):
        """
        Returns a list of all the buckets present on the organization S3 storage.
        """
        response = self.client.list_buckets()

        list_bucket = []
        for bucket in response['Buckets']:
            list_bucket.append(bucket["Name"])

        return list_bucket
    

    def list_files(self, bucket_name, prefix:str="", display=False):
        """
        Returns a list of all the files present in a bucket.
        """
        response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        file_list = [""] * len(response["Contents"])
        for file_idx, file in enumerate(response["Contents"]):
            file_list[file_idx] = file['Key']
            if display:
                print("S3Admin >> Found file:", file["Key"])

        return file_list
    

    def list_root(self, bucket_name, prefix:str="", display=False):
        """
        Returns the list of top folders present in a bucket.
        """
        paginator = self.client.get_paginator('list_objects_v2')
        
        folder_names = []
        # Paginate through all objects in the bucket
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for common_prefix in page['CommonPrefixes']:
                    folder_names.append(common_prefix['Prefix'].rstrip('/'))
                    if display:
                        print("S3Admin >> Found folder:", folder_names[-1])
                    
        return folder_names
    
    def _count_files(self, bucket_name, prefix:str="", display=False):
        """
        Returns the list of top folders present in a bucket.
        """
        paginator = self.client.get_paginator('list_objects_v2')
        
        folder_counts = {}
        # Paginate through all objects in the bucket
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter='/'):
            if 'CommonPrefixes' in page:
                for common_prefix in page['CommonPrefixes']:
                    folder_name = common_prefix['Prefix'].rstrip('/')
                    folder_counts[folder_name] = 0

        # Count objects in each main folder
        for folder_name in folder_counts:
            for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_name + '/'):
                if 'Contents' in page:
                    folder_counts[folder_name] += len(page['Contents'])
            if display:
                print(f"S3Admin >> Folder {folder_name} holds {folder_counts[folder_name]} files")

        return folder_counts

    def _overwatch_report(self, display=False):
        """
        A wide range overwatch of all the files present in each bucket.
        Can't read more than 1000 file per bucket, usefull to detect anomalies.
        """

        df_files = pd.DataFrame([["", ""]], columns=["bucket", "name"])
        df_folders = pd.DataFrame([["", "", ""]], columns=["bucket", "folder", "file_count"])
        print("S3Admin >> Starting Owerwatch report...")
        for bucket in tqdm(self.list_bucket()):
            # File listing
            files = self.list_files(bucket_name=bucket, display=display)
            buckets = [bucket]*len(files)
            new_df = pd.DataFrame(list(zip(buckets, files)), columns=["bucket", "name"])
            df_files = pd.concat([df_files, new_df])

            # File counting
            folders = self._count_files(bucket_name=bucket, display=display)
            new_df = pd.DataFrame(list(zip([bucket]*len(folders), folders.keys(), folders.values())), 
                                  columns=["bucket", "folder", "file_count"])
            df_folders = pd.concat([df_folders, new_df])

        df_files = df_files.iloc[1:, :]
        path = os.path.join(self.temp_folder_path, "files_list.csv")
        df_files.to_csv(path, index=False, header=True)
        print("S3Admin >> Owerwatch files report saved under:", path)

        df_folders = df_folders.iloc[1:, :]
        path = os.path.join(self.temp_folder_path, "folders_count.csv")
        df_folders.to_csv(path, index=False, header=True)
        print("S3Admin >> Owerwatch folders report saved under:", path)

        return df_files, df_folders
        
    
    def get_inventory(self, bucket_name, prefix:str=None) -> str:
        """
        Find the most recent bucket inventory and returns its cloud path.
        """

        # List objects within the eponymous folder (default logging folder)
        if not prefix:
            prefix = bucket_name
        response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Filter for CSV files and sort by last modified time
        csv_files = [obj for obj in response['Contents'] if obj['Key'].endswith(('.csv.gz', '.csv'))]
        if not csv_files:
            print("S3Admin >> No files found in the specified prefix.")
            return None
        
        last_inventory = max(csv_files, key=lambda x: x['LastModified'])["Key"]
        print("S3Admin >> Found inventory:", last_inventory)

        return last_inventory


    def dowload_inventory(self, bucket_name, prefix:str=None) -> str:
        """
        Downloads S3 inventory and returns its local path.
        """

        key = self.get_inventory(bucket_name=bucket_name)
        path = os.path.join(self.temp_folder_path, os.path.split(key)[1])

        self.client.download_file(bucket_name, key, path)
        print("S3Admin >> Dowloaded inventory:", path)

        return path


    def parse_inventory(self, bucket_name, prefix:str=None, 
                        logless:bool=True, logfull:bool=False) -> pd.DataFrame:
        """
        Parses a S3 .gz local archive inventory and saves and returns it as a csv file.
        """

        key = self.dowload_inventory(bucket_name=bucket_name)

        # Open the .gz file and read its content using pandas
        with gzip.open(os.path.join(self.temp_folder_path, os.path.split(key)[1]), 'rt') as f:
            df = pd.read_csv(f, names=["bucket", "name", "size_bytes", "date_modification", "storage_class"])

        if logless:
            # Filters rows where the values in the specified column do not start with '2022', '2023', or '2024'
            # i.e filters logs starting by a datetime 
            df = df[~df["name"].astype(str).str.startswith(('2022-', '2023-', '2024-'))]
        elif logfull:
            # Keeps only the logs
            df = df[df["name"].astype(str).str.startswith(('2022-', '2023-', '2024-'))]
        else:
            df = df

        path = os.path.join(self.temp_folder_path, f"{bucket_name}.csv")
        df.to_csv(path, index=False)
        print("S3Admin >> Inventory parsed and saved:", path)

        return df
    

    def delete_df(self, df:pd.DataFrame, bucket_column_name:str, key_colummn_name:str, skip_confirm:bool=False):
        """
        Deletes all the files listed in the DataFrame by reading the bucket and key columns.

        Args
        ----
        - df: the pandas DataFrame (csv) recording the files to delete. Must at least feature a
        bucket name and file key columns
        - bucket_column_name: the name of the df column that features the buckets name
        - key_colummn_name: the name of the df column that features the keys name
        """

        deleted = {}
        buckets = np.unique(df[bucket_column_name].tolist())

        confirm = "y"
        if not skip_confirm:
            print("S3Admin >> The following dataframe content will be parsed and deleted:")
            print(df.head())
            confirm = input("S3Admin >> Confirm [Y/n] ?")
        if confirm == "y" or confirm == "Y":
            for bucket_idx, bucket in enumerate(buckets):
                print(f"S3Admin >> Deleting content from bucket {bucket} ({bucket_idx+1}/{len(buckets)})")
                keys = df[df[bucket_column_name] == bucket][key_colummn_name].tolist()
                deleted[bucket] = self.delete_keys(bucket_name=bucket, keys=keys)
            
        return deleted
    

    def delete_keys(self, bucket_name:str, keys:list[str]):
        """
        Deletes from the bucket the files specified in keys, 
        and returns the list of the successuflly deleted files
        """

        batched_keys = []
        for batch_start in range(0, len(keys), 1000):
            batched_keys.append(keys[batch_start:batch_start+1000])

        deleted_counter = 0
        for batch in tqdm(batched_keys):
            response = self.client.delete_objects(Bucket=bucket_name, 
                                                  Delete={'Objects': [{'Key': key} for key in batch]})
            deleted_counter += len(response.get('Deleted', []))

        if deleted_counter == len(keys):
            print(f"S3Admin >> All {deleted_counter} objects from {bucket_name} successfully deleted")
        else:
            print(f"S3Admin >> Only {deleted_counter} out of {len(keys)} objects from {bucket_name} successfully deleted ")

        return None


session = S3Admin()

# l_buckets = session.list_bucket()
# l_files = session.list_files()
# session.parse_inventory(bucket_name="susai-models-inf",
#                         logless=False, logfull=True)


# session._overwatch_report()
# session.list_root(bucket_name="capeng-dataverse", display=True)

# l = session.list_bucket()
# for bucket in tqdm(l):
#     session.parse_inventory(bucket_name=bucket, logless=False, logfull=True)

# df=pd.read_csv(os.path.join(session.temp_folder_path, "capeng-dataverse.csv"))
# session.delete_df(df=df, bucket_column_name="bucket", key_colummn_name="name")

