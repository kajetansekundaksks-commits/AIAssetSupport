IF DB_ID('AIInvestorResearch') IS NULL
BEGIN
    CREATE DATABASE AIInvestorResearch;
END
GO

USE AIInvestorResearch;
GO

CREATE TABLE dbo.Investors (
    InvestorID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(150) NOT NULL UNIQUE,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);
GO

CREATE TABLE dbo.Companies (
    CompanyID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Ticker VARCHAR(10) NOT NULL,
    CompanyName VARCHAR(100) NOT NULL,
    Exchange VARCHAR(20) NULL,
    Country VARCHAR(20) NULL,
    Sector VARCHAR(50) NULL,

    CONSTRAINT UQ_Companies_Ticker UNIQUE (Ticker)
);
GO

CREATE TABLE dbo.CompanyKeywords (
    KeywordID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CompanyID INT NOT NULL,
    Keyword VARCHAR(100) NOT NULL,

    CONSTRAINT FK_CompanyKeywords_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES dbo.Companies(CompanyID)
);
GO

CREATE TABLE dbo.Portfolios (
    PortfolioID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    InvestorID INT NOT NULL,
    PortfolioName VARCHAR(100) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_Portfolios_Investors
        FOREIGN KEY (InvestorID)
        REFERENCES dbo.Investors(InvestorID)
);
GO

CREATE TABLE dbo.PortfolioHoldings (
    HoldingID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    PortfolioID INT NOT NULL,
    CompanyID INT NOT NULL,
    AddedAt DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_PortfolioHoldings_Portfolios
        FOREIGN KEY (PortfolioID)
        REFERENCES dbo.Portfolios(PortfolioID),

    CONSTRAINT FK_PortfolioHoldings_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES dbo.Companies(CompanyID),

    CONSTRAINT UQ_Portfolio_Company
        UNIQUE (PortfolioID, CompanyID)
);
GO

CREATE TABLE dbo.News (
    NewsID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CompanyID INT NOT NULL,
    PublishedAt DATETIME2 NOT NULL,
    Source VARCHAR(100) NULL,
    Title VARCHAR(300) NOT NULL,
    Url VARCHAR(500) NULL,
    Content NVARCHAR(MAX) NULL,
    RelevanceScore FLOAT NULL,
    RelevanceMethod VARCHAR(100) NULL,
    TfidfSimilarity FLOAT NULL,

    CONSTRAINT FK_News_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES dbo.Companies(CompanyID),

    CONSTRAINT UQ_News_Url
        UNIQUE (Url)
);
GO

CREATE TABLE dbo.SentimentAnalysis (
    SentimentID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    NewsID INT NOT NULL,
    SentimentLabel VARCHAR(20) NOT NULL,
    SentimentScore FLOAT NOT NULL,
    ConfidenceScore FLOAT NULL,
    ModelName VARCHAR(100) NULL,
    AnalyzedAt DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_SentimentAnalysis_News
        FOREIGN KEY (NewsID)
        REFERENCES dbo.News(NewsID),

    CONSTRAINT UQ_SentimentAnalysis_NewsID
        UNIQUE (NewsID)
);
GO

CREATE TABLE dbo.DailyBriefs (
    BriefID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    InvestorID INT NOT NULL,
    BriefDate DATE NOT NULL,
    BriefText NVARCHAR(MAX) NULL,
    GeneratedAt DATETIME2 DEFAULT GETDATE(),
    IsSent BIT NOT NULL DEFAULT 0,
    SentAt DATETIME2 NULL,

    CONSTRAINT FK_DailyBriefs_Investors
        FOREIGN KEY (InvestorID)
        REFERENCES dbo.Investors(InvestorID),

    CONSTRAINT UQ_DailyBriefs_Investor_Date
        UNIQUE (InvestorID, BriefDate)
);
GO

CREATE TABLE dbo.EmailDeliveryLog (
    DeliveryID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    BriefID INT NOT NULL,
    RecipientEmail VARCHAR(150) NOT NULL,
    DeliveryStatus VARCHAR(20) NOT NULL,
    SentAt DATETIME2 DEFAULT GETDATE(),
    ErrorMessage NVARCHAR(MAX) NULL,

    CONSTRAINT FK_EmailDeliveryLog_DailyBriefs
        FOREIGN KEY (BriefID)
        REFERENCES dbo.DailyBriefs(BriefID)
);
GO

CREATE TABLE dbo.MarketData (
    MarketDataID INT IDENTITY(1,1) PRIMARY KEY,
    CompanyID INT NOT NULL,
    TradeDate DATE NOT NULL,

    OpenPrice FLOAT NULL,
    HighPrice FLOAT NULL,
    LowPrice FLOAT NULL,
    ClosePrice FLOAT NULL,
    Volume BIGINT NULL,

    LastPrice FLOAT NULL,
    LastPriceTime DATETIME2 NULL,

    CreatedAt DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_MarketData_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES dbo.Companies(CompanyID),

    CONSTRAINT UQ_MarketData_Company_Date
        UNIQUE (CompanyID, TradeDate)
);
GO