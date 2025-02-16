FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
RUN yum install -y tar xz

# Download and extract the static build of FFmpeg
RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ && \
    mv ffmpeg-*-static/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*-static/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg-*-static

# Verify FFmpeg installation
RUN ffmpeg -version

# Copy function code
COPY app.py /var/task/

# Set the CMD to your function handler
CMD ["app.lambda_handler"]

