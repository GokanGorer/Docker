import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
print("REDIS_HOST:", os.getenv('REDIS_HOST'))
print("REDIS_PASSWORD:", os.getenv('REDIS_PASSWORD'))

load_dotenv() 
redis_host = os.getenv('REDIS_HOST')
redis_password = os.getenv('REDIS_PASSWORD')

if redis_password:
    cache = redis.Redis(host=redis_host, port=6379, password=redis_password)
else:
    cache = redis.Redis(host=redis_host, port=6379)

app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    df = pd.read_csv('app/titanic.csv')
    table = df.head().to_html(classes='data', index=False)

    survived = df[df['Survived'] == 1]
    gender_counts = survived['Sex'].value_counts().to_dict()

    return render_template(
        'titanic.html',
        table=table,
        gender_counts=gender_counts
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)