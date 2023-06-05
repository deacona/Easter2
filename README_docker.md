# Running it all through Docker

```bash
docker build -t easter .
docker run -it -v $(pwd):/tf --rm easter /bin/bash
python
```

```python
import os
os.chdir("src")
from easter_model import train

train()

from predict import test_on_iam
checkpoint_path = "Empty"

test_on_iam(show=False, partition="validation", checkpoint=checkpoint_path, uncased=True)

test_on_iam(show=False, partition="test", checkpoint=checkpoint_path, uncased=True)

exit()
```

```bash
cd src
python predict_line.py --path ../data/lines/a01/a01-132x/a01-132x-00.png
```