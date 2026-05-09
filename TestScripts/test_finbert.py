from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)

text = """
Apple reported stronger than expected quarterly earnings,
driven by strong iPhone sales and services revenue.
"""

result = classifier(text)

print(result)