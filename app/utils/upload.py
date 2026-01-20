import boto3
from fastapi import HTTPException
import os, dotenv
from botocore.exceptions import ClientError

dotenv.load_dotenv()
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION =  os.getenv('AWS_REGION_s3')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET')


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET
)

def gsa_upload(file,filename):
    # print(file)
    try:
        file.file.seek(0)  # REQUIRED
        s3_key = f"master_uploads/{filename}"

        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        return {
        "s3_key": s3_key,
        "url": f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}",
        "size": file.size,
    }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 client error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        file.file.close()