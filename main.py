import boto3, uuid
from fastapi import FastAPI, UploadFile
import cv2, io, numpy as np
from .trOCR_recognition import handle_image

app = FastAPI()
s3 = boto3.client(
	"s3",
	endpoint_url="http://localhost:9000", # если MinIO локальный
	aws_access_key_id="minio",
	aws_secret_access_key="minio123"
)
BUCKET = "processed-images"

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
		img_array = np.frombuffer(await image.read(), np.uint8)
		img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

		processed_img = handle_image(img)
		ext = mime_to_ext.get(image.content_type, ".png")

		_, buffer = cv2.imencode(ext, processed_img)
		key = f"{uuid.uuid4()}{ext}"
	
		s3.put_object(Bucket=BUCKET, Key=key, Body=buffer.tobytes(), ContentType="image/png")
		url = s3.generate_presigned_url(
			"get_object",
			Params={"Bucket": BUCKET, "Key": key},
			ExpiresIn=3600
		)
		urls.append(url)

	return {"images": urls}
