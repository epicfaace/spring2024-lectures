import os
import re
import json
import hashlib
import shutil
import traceback
import requests
from io import BytesIO
from dataclasses import dataclass
from typing import Optional, List, Any, Union


def download_file(url: str, filename: str):
    """Download `url` and save the contents to `filename`.  Skip if `filename` already exists."""
    if not os.path.exists(filename):
        print(f"Downloading {url} to {filename}")
        response = requests.get(url)
        with open(filename, "wb") as f:
            shutil.copyfileobj(BytesIO(response.content), f)


def cached(url: str) -> str:
    """Download `url` if needed and return the location of the cached file."""
    name = re.sub(r"[^\w_-]+", "_", url)
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()

    path = os.path.join("var", url_hash + "-" + name)
    download_file(url, path)
    return path


def get_stack():
    """Return the current stack as a string."""
    stack = traceback.extract_stack()
    stack = [frame.name for frame in stack]  # Take only names
    i = None
    for j, name in enumerate(stack):
        if name == "<module>":
            i = j
    stack = stack[i + 1:]  # Delete everything up to the last module
    stack = stack[:-2]  # Remove the current two functions (get_stack and point/figure/etc.)
    return stack

def note(message: str):
    """Make a note (bullet point) with `message`."""
    print("note:", message)
    stack = json.dumps(get_stack())
    arg = json.dumps(message)
    add_content([f"addText({stack}, {arg});"])


def see(obj: Any):
    """References `obj` in the code, but don't print anything out."""
    print("see:", obj)


def image(path: str):
    """Show the image at `path`."""
    print("image:", path)
    stack = json.dumps(get_stack())
    arg = json.dumps(path)
    add_content([f"addImage({stack}, {arg});"])


has_added_content = False

def add_content(lines: List[str]):
    """
    Add content that would be displayed by `view.html`.
    The first time we call this function, we clear the content.
    `lines`: list of Javascript lines.
    """
    global has_added_content
    mode = "w" if not has_added_content else "a"
    has_added_content = True
    with open("content.js", mode) as f:
        for line in lines:
            print(line, file=f)

############################################################

@dataclass(frozen=True)
class Spec:
    name: Optional[str] = None
    author: Optional[str] = None
    organization: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[Union[str, List[str]]] = None
    references: Optional[List[Any]] = None


@dataclass(frozen=True)
class MethodSpec(Spec):
    pass


@dataclass(frozen=True)
class DataSpec(Spec):
    num_tokens: Optional[int] = None
    vocabulary_size: Optional[int] = None


@dataclass(frozen=True)
class ArchitectureSpec(Spec):
    num_parameters: Optional[int] = None
    num_layers: Optional[int] = None
    dim_model: Optional[int] = None
    num_heads: Optional[int] = None
    dim_head: Optional[int] = None
    description: Optional[str] = None
    references: Optional[List[Any]] = None


@dataclass(frozen=True)
class TrainingSpec(Spec):
    context_length: Optional[int] = None
    batch_size_tokens: Optional[int] = None
    learning_rate: Optional[float] = None
    weight_decay: Optional[float] = None
    optimizer: Optional[str] = None
    hardware: Optional[str] = None
    num_epochs: Optional[int] = None
    num_flops: Optional[int] = None
    references: Optional[List[Any]] = None


@dataclass(frozen=True)
class ModelSpec(Spec):
    data: Optional[DataSpec] = None
    architecture: Optional[ArchitectureSpec] = None
    training: Optional[TrainingSpec] = None
