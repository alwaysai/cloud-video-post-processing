## Cloud-based FFMPEG post-processing of video files

This project was developed as example code to demonstrate an approach to post-processing of video files using ffmpeg, s3, Lambda, ECR, Docker, Serverless.

#### Notice: This pipeline will be sufficient for small-medium sized video files (250-500 MB) however, for larger files, the lambda should be replaced with Fargate or Batch to remove the Lambda runtime limitations. 

Follow the steps below to create the re-encoding pipeline. Be sure to replace the us-west-2 region with your region and replace <aws-account-id> with your AWS account id.  You will need the following dependencies installed before yous begin deployment:
- Docker
- Serverless (Tested with serverless v3.40.0)
- Make sure the ffmpeg command in app.py matches the re-encoding parameters you need

Authenticate with AWS ECR:
```
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-west-2.amazonaws.com
```

Create an ECR repository:
```
aws ecr create-repository --repository-name ffmpeg-lambda
```

Build and push the docker image including the lambda_handler in app.py
```
docker build -t ffmpeg-lambda .
docker tag ffmpeg-lambda:latest <aws_account_id>.dkr.ecr.us-west-2.amazonaws.com/ffmpeg-lambda:latest
docker push <aws_account_id>.dkr.ecr.us-west-2.amazonaws.com/ffmpeg-lambda:latest
```

Deploy the lambda configuration with serverless
```
serverless deploy
```

Remove the lambda configuration with serverless
```
serverless remove
```

What should happen:
1. The python code for using ffmpeg to re-encode the video file will be containerized and published to ECR under the ffmpeg-lambda repository.
2. Serverless will do the following:
   3. Deploy/configure the lambda to use the container.
   4. Configure the input/output s3 buckets (assumes they don't already exist).
   5. Add GetObject and PutObject policies to the buckets to allow the lambda to read/write the respective buckets.
   5. Add an event trigger on the input bucket when .mp4 files are created in that bucket.

To test the pipeline:
```
aws s3 cp sample.mp4 s3://your-input-bucket-name/
```

### References
ffmpeg Master: https://www.johnvansickle.com/ffmpeg/
