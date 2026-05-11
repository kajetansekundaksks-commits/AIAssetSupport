USE AIInvestorResearch;
GO

-- =====================================
-- INVESTORS
-- =====================================
-- This script assumes that framework/import_companies.py
-- has already been executed in order to populate the
-- Companies table required for portfolio holdings.
--
-- Example email addresses are used for demonstration
-- and testing purposes only.
--
-- To test the email delivery pipeline, replace the
-- sample emails with your own email address or test accounts.
-- Investor names are exemplary and inspired by characters from the TV show "Prison Break".
-- =====================================

IF NOT EXISTS (
    SELECT 1 FROM dbo.Investors
    WHERE Email = 'scofield@example.com'
)
BEGIN
    INSERT INTO dbo.Investors (FirstName, LastName, Email)
    VALUES ('Michael', 'Scofield', 'scofield@example.com');
END;

IF NOT EXISTS (
    SELECT 1 FROM dbo.Investors
    WHERE Email = 'lincoln@example.com'
)
BEGIN
    INSERT INTO dbo.Investors (FirstName, LastName, Email)
    VALUES ('Lincoln', 'Burrows', 'lincoln@example.com');
END;

IF NOT EXISTS (
    SELECT 1 FROM dbo.Investors
    WHERE Email = 'mahone@example.com'
)
BEGIN
    INSERT INTO dbo.Investors (FirstName, LastName, Email)
    VALUES ('Alexander', 'Mahone', 'mahone@example.com');
END;

IF NOT EXISTS (
    SELECT 1 FROM dbo.Investors
    WHERE Email = 'bagwell@example.com'
)
BEGIN
    INSERT INTO dbo.Investors (FirstName, LastName, Email)
    VALUES ('Theodore', 'Bagwell', 'bagwell@example.com');
END;

IF NOT EXISTS (
    SELECT 1 FROM dbo.Investors
    WHERE Email = 'kajetan@example.com'
)
BEGIN
    INSERT INTO dbo.Investors (FirstName, LastName, Email)
    VALUES ('Kajetan', 'Sekunda', 'kajetan@example.com');
END;
GO


-- =====================================
-- PORTFOLIOS
-- =====================================

INSERT INTO dbo.Portfolios (InvestorID, PortfolioName)
SELECT InvestorID, 'Michael Scofield Main Portfolio'
FROM dbo.Investors
WHERE Email = 'scofield@example.com'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Portfolios
      WHERE PortfolioName = 'Michael Scofield Main Portfolio'
  );

INSERT INTO dbo.Portfolios (InvestorID, PortfolioName)
SELECT InvestorID, 'Lincoln Main Portfolio'
FROM dbo.Investors
WHERE Email = 'lincoln@example.com'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Portfolios
      WHERE PortfolioName = 'Lincoln Main Portfolio'
  );

INSERT INTO dbo.Portfolios (InvestorID, PortfolioName)
SELECT InvestorID, 'Mahone Strategic Portfolio'
FROM dbo.Investors
WHERE Email = 'mahone@example.com'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Portfolios
      WHERE PortfolioName = 'Mahone Strategic Portfolio'
  );

INSERT INTO dbo.Portfolios (InvestorID, PortfolioName)
SELECT InvestorID, 'Bagwell Opportunistic Portfolio'
FROM dbo.Investors
WHERE Email = 'bagwell@example.com'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Portfolios
      WHERE PortfolioName = 'Bagwell Opportunistic Portfolio'
  );

INSERT INTO dbo.Portfolios (InvestorID, PortfolioName)
SELECT InvestorID, 'Kajetan Personal Portfolio'
FROM dbo.Investors
WHERE Email = 'kajetan@example.com'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Portfolios
      WHERE PortfolioName = 'Kajetan Personal Portfolio'
  );
GO


-- =====================================
-- PORTFOLIO HOLDINGS
-- Requires Companies to be imported first
-- via framework/import_companies.py
-- =====================================

-- Michael: AAPL, MSFT, NVDA
INSERT INTO dbo.PortfolioHoldings (PortfolioID, CompanyID)
SELECT p.PortfolioID, c.CompanyID
FROM dbo.Portfolios p
JOIN dbo.Companies c ON c.Ticker IN ('AAPL', 'MSFT', 'NVDA')
WHERE p.PortfolioName = 'Michael Scofield Main Portfolio'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.PortfolioHoldings ph
      WHERE ph.PortfolioID = p.PortfolioID
        AND ph.CompanyID = c.CompanyID
  );

-- Lincoln: XOM, CVX, CAT
INSERT INTO dbo.PortfolioHoldings (PortfolioID, CompanyID)
SELECT p.PortfolioID, c.CompanyID
FROM dbo.Portfolios p
JOIN dbo.Companies c ON c.Ticker IN ('XOM', 'CVX', 'CAT')
WHERE p.PortfolioName = 'Lincoln Main Portfolio'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.PortfolioHoldings ph
      WHERE ph.PortfolioID = p.PortfolioID
        AND ph.CompanyID = c.CompanyID
  );

-- Mahone: MSFT, NVDA, GOOGL
INSERT INTO dbo.PortfolioHoldings (PortfolioID, CompanyID)
SELECT p.PortfolioID, c.CompanyID
FROM dbo.Portfolios p
JOIN dbo.Companies c ON c.Ticker IN ('MSFT', 'NVDA', 'GOOGL')
WHERE p.PortfolioName = 'Mahone Strategic Portfolio'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.PortfolioHoldings ph
      WHERE ph.PortfolioID = p.PortfolioID
        AND ph.CompanyID = c.CompanyID
  );

-- Bagwell: AMD, NVDA, TSLA
INSERT INTO dbo.PortfolioHoldings (PortfolioID, CompanyID)
SELECT p.PortfolioID, c.CompanyID
FROM dbo.Portfolios p
JOIN dbo.Companies c ON c.Ticker IN ('AMD', 'NVDA', 'TSLA')
WHERE p.PortfolioName = 'Bagwell Opportunistic Portfolio'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.PortfolioHoldings ph
      WHERE ph.PortfolioID = p.PortfolioID
        AND ph.CompanyID = c.CompanyID
  );

-- Kajetan: AAPL, NVDA, JPM, INTC
INSERT INTO dbo.PortfolioHoldings (PortfolioID, CompanyID)
SELECT p.PortfolioID, c.CompanyID
FROM dbo.Portfolios p
JOIN dbo.Companies c ON c.Ticker IN ('AAPL', 'NVDA', 'JPM', 'INTC')
WHERE p.PortfolioName = 'Kajetan Personal Portfolio'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.PortfolioHoldings ph
      WHERE ph.PortfolioID = p.PortfolioID
        AND ph.CompanyID = c.CompanyID
  );
GO