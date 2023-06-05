# Running it all through Docker

```bash
docker build -t easter .

docker run -it -v $(pwd):/tf --rm easter python src/run_training.py

docker run -it -v $(pwd):/tf --rm easter python src/run_evaluation.py

docker run -it -v $(pwd):/tf --rm easter python src/predict_line.py --path /tf/data/lines/a01/a01-132x/a01-132x-00.png
```