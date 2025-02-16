import boto3
import subprocess
import os
import shutil
import time

s3 = boto3.client("s3")

def lambda_handler(event, context):
    # Clean up /tmp/ before execution
    cleanup_tmp()
    record = event["Records"][0]
    bucket_name = record["s3"]["bucket"]["name"]
    object_key = record["s3"]["object"]["key"]
    input_file = f"/tmp/{os.path.basename(object_key)}"
    output_file = "/tmp/re-encoded-video.mp4"
    # Download the video from S3
    s3.download_file(bucket_name, object_key, input_file)
    try:
        # Run FFmpeg
        command = [
            "ffmpeg", "-err_detect", "aggressive",
            "-fflags", "discardcorrupt",
            "-i", input_file,
            "-r", "30", "-c:v", "libx264",
            "-movflags", "faststart", "-an", "-tune", "zerolatency",
            output_file
        ]
        subprocess.run(command, check=True)
        # Upload the re-encoded video
        output_bucket = "aai-test-video-output"
        output_key = f"processed/{os.path.basename(object_key)}"
        s3.upload_file(output_file, output_bucket, output_key)
        return {
            "status": "success",
            "input_file": f"s3://{bucket_name}/{object_key}",
            "output_file": f"s3://{output_bucket}/{output_key}"
        }
    except Exception as e:
        print("Error:", str(e))
        return {"status": "failed", "error": str(e)}

def cleanup_tmp():
    """ Cleans up the /tmp directory to ensure no leftover files persist across executions """
    tmp_dir = "/tmp"
    try:
        for filename in os.listdir(tmp_dir):
            file_path = os.path.join(tmp_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symbolic link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directories
        print("✅ /tmp directory cleaned up successfully.")
    except Exception as e:
        print(f"⚠️ Error cleaning up /tmp/: {e}")
