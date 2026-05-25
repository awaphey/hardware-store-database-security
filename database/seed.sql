USE HardwareStoreDB;
GO

INSERT INTO dbo.Users (Username, PasswordHash, Role, Email)
VALUES
    (N'admin', CONVERT(NVARCHAR(128), HASHBYTES('SHA2_256', N'AdminPass123!'), 2), N'Admin', N'admin@hardwarestore.test'),
    (N'alicia', CONVERT(NVARCHAR(128), HASHBYTES('SHA2_256', N'CustomerPass123!'), 2), N'Customer', N'alicia@example.com'),
    (N'ben', CONVERT(NVARCHAR(128), HASHBYTES('SHA2_256', N'CustomerPass456!'), 2), N'Customer', N'ben@example.com');

INSERT INTO dbo.Products (ProductName, Category, Price, StockQuantity)
VALUES
    (N'NVIDIA RTX 4070 Super Graphics Card', N'Graphics Card', 2999.00, 8),
    (N'27-inch 165Hz Gaming Monitor', N'Monitor', 899.00, 12),
    (N'Mechanical Keyboard - Blue Switch', N'Keyboard', 249.00, 20),
    (N'Wireless Gaming Mouse', N'Mouse', 189.00, 15);
GO
