import re
import os
import boto3
from fastapi import HTTPException
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.users import User
from app.models.file_uploads import FileUpload
from app.config import settings

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION_S3,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET
)

def gsa_upload(file,filename,type):
    try:
        file.file.seek(0) 
        if type == "gsa_upload":
            s3_key = f"master_uploads/{filename}"
        elif type == "cpl_upload":
            s3_key = f"cpl_pricelist_uploads/{filename}"
        elif type == "logo_upload":
            s3_key = f"company_logos/{filename}"

        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION_S3}.amazonaws.com/{s3_key}"

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
 