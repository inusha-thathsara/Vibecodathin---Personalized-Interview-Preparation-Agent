import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from interview.engine import InterviewEngine

def test_nonsense_detection_gibberish():
    gibberish = "dfhgbdfbhxdcfqvhn fghfg"
    assert InterviewEngine._is_nonsense(gibberish) is True

def test_nonsense_detection_low_effort():
    assert InterviewEngine._is_nonsense("hi") is True
    assert InterviewEngine._is_nonsense("lol") is True
    assert InterviewEngine._is_nonsense("asdf") is True

def test_nonsense_detection_repeated_chars():
    assert InterviewEngine._is_nonsense("aaaaaaaaaaaaa") is True

def test_substantive_response():
    answer = "I implemented embeddings using sentence-transformers and stored vectors in ChromaDB with metadata filtering."
    assert InterviewEngine._is_nonsense(answer) is False
