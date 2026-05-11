-- =====================================
-- SAMPLE QUERIES
-- =====================================

USE AIInvestorResearch;
GO

-- =====================================
-- 1. Latest generated briefs
-- =====================================

SELECT
    b.BriefID,
    i.FirstName,
    i.LastName,
    b.BriefDate,
    b.GeneratedAt
FROM dbo.DailyBriefs b
JOIN dbo.Investors i
    ON b.InvestorID = i.InvestorID
ORDER BY b.GeneratedAt DESC;
GO


-- =====================================
-- 2. Email delivery log
-- =====================================

SELECT
    DeliveryID,
    RecipientEmail,
    DeliveryStatus,
    SentAt
FROM dbo.EmailDeliveryLog
ORDER BY SentAt DESC;
GO


-- =====================================
-- 3. Portfolio holdings by investor
-- =====================================

SELECT
    i.FirstName,
    i.LastName,
    p.PortfolioName,
    c.Ticker,
    c.CompanyName,
    c.Sector
FROM dbo.PortfolioHoldings ph
JOIN dbo.Portfolios p
    ON ph.PortfolioID = p.PortfolioID
JOIN dbo.Investors i
    ON p.InvestorID = i.InvestorID
JOIN dbo.Companies c
    ON ph.CompanyID = c.CompanyID
ORDER BY i.LastName, c.Ticker;
GO


-- =====================================
-- 4. Latest news with sentiment
-- =====================================

SELECT TOP 20
    c.Ticker,
    n.Title,
    n.Source,
    n.PublishedAt,
    s.SentimentLabel,
    s.SentimentScore
FROM dbo.News n
JOIN dbo.Companies c
    ON n.CompanyID = c.CompanyID
LEFT JOIN dbo.SentimentAnalysis s
    ON n.NewsID = s.NewsID
ORDER BY n.PublishedAt DESC;
GO


-- =====================================
-- 5. News volume by company
-- =====================================

SELECT
    c.Ticker,
    COUNT(*) AS NewsCount
FROM dbo.News n
JOIN dbo.Companies c
    ON n.CompanyID = c.CompanyID
GROUP BY c.Ticker
ORDER BY NewsCount DESC;
GO


-- =====================================
-- 6. Sentiment distribution
-- =====================================

SELECT
    SentimentLabel,
    COUNT(*) AS CountBySentiment
FROM dbo.SentimentAnalysis
GROUP BY SentimentLabel;
GO


-- =====================================
-- 7. Companies by sector
-- =====================================

SELECT
    Sector,
    COUNT(*) AS CompanyCount
FROM dbo.Companies
GROUP BY Sector
ORDER BY CompanyCount DESC;
GO