IF DB_ID(N'HardwareStoreDB') IS NULL
BEGIN
    CREATE DATABASE HardwareStoreDB;
END
GO

USE HardwareStoreDB;
GO

IF OBJECT_ID(N'dbo.Order_Details', N'U') IS NOT NULL DROP TABLE dbo.Order_Details;
IF OBJECT_ID(N'dbo.Orders', N'U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID(N'dbo.Products', N'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID(N'dbo.Users', N'U') IS NOT NULL DROP TABLE dbo.Users;
GO

CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(128) NOT NULL,
    Role NVARCHAR(20) NOT NULL,
    Email NVARCHAR(120) NOT NULL UNIQUE,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT CK_Users_Role CHECK (Role IN (N'Admin', N'Customer'))
);

CREATE TABLE dbo.Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    Category NVARCHAR(60) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    StockQuantity INT NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT CK_Products_Price CHECK (Price >= 0),
    CONSTRAINT CK_Products_StockQuantity CHECK (StockQuantity >= 0)
);

CREATE TABLE dbo.Orders (
    OrderID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    OrderDate DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    TotalAmount DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_Orders_Users FOREIGN KEY (UserID)
        REFERENCES dbo.Users(UserID),
    CONSTRAINT CK_Orders_TotalAmount CHECK (TotalAmount >= 0)
);

CREATE TABLE dbo.Order_Details (
    OrderDetailID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    SubtotalPrice DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_OrderDetails_Orders FOREIGN KEY (OrderID)
        REFERENCES dbo.Orders(OrderID)
        ON DELETE CASCADE,
    CONSTRAINT FK_OrderDetails_Products FOREIGN KEY (ProductID)
        REFERENCES dbo.Products(ProductID),
    CONSTRAINT CK_OrderDetails_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderDetails_SubtotalPrice CHECK (SubtotalPrice >= 0)
);
GO

CREATE INDEX IX_Orders_UserID ON dbo.Orders(UserID);
CREATE INDEX IX_OrderDetails_OrderID ON dbo.Order_Details(OrderID);
CREATE INDEX IX_OrderDetails_ProductID ON dbo.Order_Details(ProductID);
GO
