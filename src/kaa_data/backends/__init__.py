from kaa_data.backends.campus import CampusBackend
from kaa_data.backends.gom import GomBackend

BACKENDS = {
    "gom": GomBackend,
    "campus": CampusBackend,
}


def get_backend(name: str):
    try:
        return BACKENDS[name]()
    except KeyError as exc:
        raise ValueError(f"Unknown backend: {name}. Choose from: {', '.join(BACKENDS)}") from exc