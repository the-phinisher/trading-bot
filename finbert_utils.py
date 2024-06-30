from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple

device_prority = [
    ("cuda", torch.cuda.is_available()),
    ("mps", torch.backends.mps.is_available()),
]

device = "cpu"
for device_name, is_available in device_prority:
    if is_available:
        device = device_name
    

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]

def estimate_sentiment(news):
    if news:
        tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)

        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
            "logits"
        ]
        result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
        probability = result[torch.argmax(result)]
        sentiment = labels[torch.argmax(result)]
        return probability, sentiment
    else:
        return 0, labels[-1]


if __name__ == "__main__":
    print("device:", device)
    # mix of news
    tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!','traders were happy!', 'the stock remained almost the same', 'mathematical equations solved'])
    print(tensor, sentiment)
    assert sentiment == 'neutral'
    # positive news
    tensor, sentiment = estimate_sentiment(['traders were happy!', 'stock grew significantly'])
    print(tensor, sentiment)
    assert sentiment == 'positive'
    # negative news
    tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!'])
    print(tensor, sentiment)
    assert sentiment == 'negative'
    # neutral news
    tensor, sentiment = estimate_sentiment(['the stock remained almost the same'])
    print(tensor, sentiment)
    assert sentiment == 'neutral'
    # irrelevant news
    tensor, sentiment = estimate_sentiment(['mathematical equations solved'])
    print(tensor, sentiment)
    assert sentiment == 'neutral'
