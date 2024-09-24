"""
AWS init package. Every class can be imported from this folder without going deeper in the src/ tree.
"""

__all__ = [
    "S3Client",
]


from s3.src.s3client import S3Client
