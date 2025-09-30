import boto3, uuid
from fastapi import FastAPI, UploadFile
import cv2, io, numpy as np
from trOCR_recognition import handle_image
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
s3 = boto3.client(
	"s3",
	endpoint_url=os.getenv("S3_ENDPOINT_URL"), # если MinIO локальный
	aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
	aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
BUCKET = os.getenv("BUCKET")




mime_to_ext = {
	"image/png": ".png",
	"image/jpeg": ".jpg",
	"image/jpg": ".jpg",
	"image/webp": ".webp"
}

@app.post("/get_spelling_mistakes")
async def get_spelling_mistakes(images: list[UploadFile]):
	urls = []

	for image in images:
		processed_img = await handle_image(image)
		ext = mime_to_ext.get(image.content_type, ".png")

		_, buffer = cv2.imencode(ext, processed_img)
		key = image.filename
		s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.tobytes(), ContentType="image/png")
		url = s3.generate_presigned_url(
			"get_object",
			Params={"Bucket": BUCKET, "Key": key},
			ExpiresIn=3600
		)
		urls.append(url)

	return {"images": urls}
