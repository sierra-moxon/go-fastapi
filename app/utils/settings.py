from os import path
from enum import Enum
import yaml

CONFIG = path.join(path.dirname(path.abspath(__file__)), "../conf/config.yaml")
golr_config = None
route_mapping = None


def get_golr_config():
    global golr_config
    if golr_config is None:
        with open(CONFIG, "r") as f:
            golr_config = yaml.load(f, Loader=yaml.FullLoader)
    return golr_config


class ESOLR(Enum):
    GOLR = get_golr_config()["solr_url"]["url"]


class ESOLRDoc(Enum):
    ONTOLOGY = "ontology_class"
    ANNOTATION = "annotation"
    BIOENTITY = "bioentity"

