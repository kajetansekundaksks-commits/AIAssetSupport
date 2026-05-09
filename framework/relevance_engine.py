import re

# -----------------------------------
# STOPWORDS
# -----------------------------------

STOPWORDS = {
    "inc",
    "corporation",
    "corp",
    "company",
    "co",
    "ltd",
    "plc",
    "group",
    "holdings",
    "class"
}

# -----------------------------------
# CLEAN TEXT
# -----------------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    return text

# -----------------------------------
# EXTRACT COMPANY KEYWORDS
# -----------------------------------

def extract_company_keywords(company_name):

    cleaned = clean_text(company_name)

    words = cleaned.split()

    keywords = []

    for word in words:

        if word not in STOPWORDS and len(word) > 2:

            keywords.append(word)

    return keywords

# -----------------------------------
# CALCULATE RELEVANCE
# -----------------------------------

def calculate_relevance(
    ticker,
    company_name,
    title,
    summary
):

    title = title or ""
    summary = summary or ""

    text = f"{title} {summary}"

    cleaned_text = clean_text(text)

    keywords = extract_company_keywords(company_name)

    score = 0

    matched_keywords = set()
    
    # -----------------------------------
    # TICKER BONUS
    # -----------------------------------

    if ticker.lower() in cleaned_text:

        score += 2

        matched_keywords.add(ticker.lower())

    # -----------------------------------
    # COMPANY KEYWORDS
    # -----------------------------------

    for keyword in keywords:

        if keyword in cleaned_text:

            score += 1

            matched_keywords.add(keyword)

    # -----------------------------------
    # FINAL DECISION
    # -----------------------------------

    is_relevant = score >= 2

    if ticker.lower() in matched_keywords:

        method = "ticker_match"

    elif matched_keywords:

        method = "keyword_match"

    else:

        method = "no_match"

    return {
        "is_relevant": is_relevant,
        "score": float(score),
        "method": method,
        "matched_keywords": matched_keywords
    }