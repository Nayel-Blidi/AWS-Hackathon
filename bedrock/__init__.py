"""
AWS init package. Every class can be imported from this folder without going deeper in the src/ tree.
"""

__all__ = [
    "S3Admin",
    "S3Client",
]


from .src.s3admin import S3Admin
from .src.s3client import S3Client
