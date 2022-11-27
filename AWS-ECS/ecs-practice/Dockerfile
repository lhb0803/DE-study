FROM amazon/aws-sam-cli-build-image-python3.8:latest
WORKDIR /usr/src/app
COPY binanceToS3.py ./
COPY rootkey.csv ./
COPY run.sh ./
RUN chmod +x ./run.sh
RUN pip install boto3
RUN pip install pandas -t .
RUN pip install ccxt -t .
# CMD ["python", "binanceToS3.py"]
ENTRYPOINT [ "./run.sh" ]