# Import modules
from configs.imports import *

# Global variables
from configs.environment import *

# Route of pages, fuctions
from configs.route import *

# Python logging
# https://stackoverflow.com/questions/17743019/flask-logging-cannot-get-it-to-write-to-a-file
logging.config.dictConfig(yaml.load(open("./configs/logging.yml")))
