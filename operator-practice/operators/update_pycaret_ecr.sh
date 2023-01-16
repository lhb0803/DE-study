# load data -> train pycaret model
source ~/anaconda3/etc/profile.d/conda.sh
conda activate py38
python /home/ubuntu/airflow/operators/train.py

echo "Build Docker Image..."
sudo docker image build . -t pycaret_lgbm:latest

# push docker image
sudo docker tag pycaret_lgbm:latest 433166909747.dkr.ecr.ap-northeast-2.amazonaws.com/pycaret_lgbm
aws ecr get-login-password --region ap-northeast-2 | sudo docker login --username AWS --password-stdin 433166909747.dkr.ecr.ap-northeast-2.amazonaws.com
sudo docker push 433166909747.dkr.ecr.ap-northeast-2.amazonaws.com/pycaret_lgbm