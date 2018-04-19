echo "...Setting up working directory..."
sudo mkdir www2/ && cd www2/

echo "...installing required packages..."
sudo apt-get update
sudo apt-get -y install git python3 virtualenv nginx supervisor gunicorn

echo "...cloning repository..."
sudo git clone $1 ./repo/
cd repo/

echo "...setting up virtual environment..."
sudo virtualenv --python=python3 env
source env/bin/activate

echo "...installing project dependencies..."
pip install -r requirements.txt

echo "..starting and configuring nginX.."
sudo /etc/init.d/nginx/start
sudo rm /etc/nginx/sites-enabled/default
sudo touch /etc/nginx/sites-available/flask_api
sudo ln -s /etc/nginx/sites-available/flask_api /etc/nginx/sites-enabled/flask_api

sudo echo "server {
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}" > /etc/nginx/sites-enabled/flask_api
