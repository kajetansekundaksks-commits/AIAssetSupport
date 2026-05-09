import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    "class",
    "common",
    "stock"
}

# -----------------------------------
# CLEAN TEXT
# -----------------------------------

def clean_text(text):
    if text is None:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

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

    return list(set(keywords))

# -----------------------------------
# TF-IDF SIMILARITY
# -----------------------------------

def calculate_tfidf_similarity(company_profile, news_text):
    company_profile = clean_text(company_profile)
    news_text = clean_text(news_text)

    if not company_profile or not news_text:
        return 0.0

    documents = [
        company_profile,
        news_text
    ]

    vectorizer = TfidfVectorizer()

    try:
        tfidf_matrix = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        return float(similarity)

    except ValueError:
        return 0.0

# -----------------------------------
# CALCULATE RELEVANCE
# -----------------------------------

def calculate_relevance(
    ticker,
    company_name,
    title,
    summary
):
    ticker = ticker or ""
    company_name = company_name or ""
    title = title or ""
    summary = summary or ""

    text = f"{title} {summary}"
    cleaned_text = clean_text(text)

    keywords = extract_company_keywords(company_name)

    company_profile = " ".join(
        [ticker, company_name] + keywords
    )

    score = 0.0
    matched_keywords = set()

    # -----------------------------------
    # TICKER BONUS
    # -----------------------------------

    ticker_clean = clean_text(ticker)

    if ticker_clean and ticker_clean in cleaned_text:
        score += 2.0
        matched_keywords.add(ticker_clean)

    # -----------------------------------
    # COMPANY KEYWORD MATCH
    # -----------------------------------

    for keyword in keywords:
        if keyword in cleaned_text:
            score += 1.0
            matched_keywords.add(keyword)

    # -----------------------------------
    # TF-IDF SIMILARITY
    # -----------------------------------

    tfidf_similarity = calculate_tfidf_similarity(
        company_profile=company_profile,
        news_text=cleaned_text
    )

    if tfidf_similarity >= 0.25:
        score += 1.5

    # -----------------------------------
    # FINAL DECISION
    # -----------------------------------

    is_relevant = score >= 2.0

    if ticker_clean in matched_keywords:
        method = "ticker_match"
    elif tfidf_similarity >= 0.25:
        method = "tfidf_similarity"
    elif matched_keywords:
        method = "keyword_match"
    else:
        method = "no_match"

    return {
        "is_relevant": is_relevant,
        "score": float(score),
        "method": method,
        "matched_keywords": list(matched_keywords),
        "tfidf_similarity": float(tfidf_similarity)
    }