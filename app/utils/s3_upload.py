import boto3
from fastapi import HTTPException
import os, dotenv
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.users import User
from app.models.file_uploads import FileUpload
from app.utils import s3_upload as s3

import re
import os


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

def gsa_upload(file,filename,type):
    # print(file)
    try:
        file.file.seek(0) 
        if type == "gsa_upload":
            s3_key = f"master_uploads/{filename}"
        elif type == "cpl_upload":
            s3_key = f"cpl_pricelist_uploads/{filename}"

        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(s3_url)

        return {
        "s3_key": s3_key,
        "url": s3_url,
        "size": file.size,
    }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 client error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        file.file.close()


def clean(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value.strip())


def save_uploaded_file(db: Session, client_id: int, file, user_email: str, type):
    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    user = db.query(User).filter_by(email=user_email).first()

    _, ext = os.path.splitext(file.filename)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    filename = (
        f"{clean(client.company_name)}_"
        f"{date_str}_"
        f"{clean(user.name)}"
        f"{ext}"
    )

    result = gsa_upload(file, filename, type)

    db.add(
        FileUpload(
            user_id=user.user_id,
            uploaded_by=user.user_id,
            client_id=client_id,
            original_filename=file.filename,
            s3_saved_filename=filename,
            s3_saved_path=result["url"],
            file_size=result["size"],
        )
    )

    db.commit()
    return result
 