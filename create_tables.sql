IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'FabricaImbuteliere')
BEGIN
    CREATE DATABASE FabricaImbuteliere;
END
GO

USE FabricaImbuteliere;
GO

--Tabel: Products
IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL DROP TABLE dbo.Products;
GO

CREATE TABLE dbo.Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    ProductCode NVARCHAR(50) NOT NULL,
    IdealCycleTimeSec INT NOT NULL
);
GO

INSERT INTO dbo.Products (ProductName, ProductCode, IdealCycleTimeSec)
VALUES ('Apa plata 0.5L', 'APA_PLATA_05', 30);
GO


-- Tabel: Shifts
IF OBJECT_ID('dbo.Shifts', 'U') IS NOT NULL DROP TABLE dbo.Shifts;
GO

CREATE TABLE dbo.Shifts (
    ShiftID INT IDENTITY(1,1) PRIMARY KEY,
    ShiftName NVARCHAR(50),
    StartTime DATETIME2(0),
    EndTime DATETIME2(0)
);
GO

INSERT INTO dbo.Shifts (ShiftName, StartTime, EndTime)
VALUES ('Schimb 1', '2025-11-19 08:00:00', '2025-11-19 16:00:00');
GO


-- Tabel: MachineEvents
IF OBJECT_ID('dbo.MachineEvents', 'U') IS NOT NULL DROP TABLE dbo.MachineEvents;
GO

CREATE TABLE dbo.MachineEvents (
    EventID INT IDENTITY(1,1) PRIMARY KEY,
    EventTime DATETIME2(0) NOT NULL,
    EventType NVARCHAR(50) NOT NULL,
    ShiftID INT NOT NULL FOREIGN KEY REFERENCES dbo.Shifts(ShiftID),
    Details NVARCHAR(255)
);
GO


-- Tabel: ProductionCycles
IF OBJECT_ID('dbo.ProductionCycles', 'U') IS NOT NULL DROP TABLE dbo.ProductionCycles;
GO

CREATE TABLE dbo.ProductionCycles (
    CycleID INT IDENTITY(1,1) PRIMARY KEY,
    Timestamp DATETIME2(0) NOT NULL,
    ShiftID INT NOT NULL FOREIGN KEY REFERENCES dbo.Shifts(ShiftID),
    ProductID INT NOT NULL FOREIGN KEY REFERENCES dbo.Products(ProductID),
    GoodPiece BIT NOT NULL,
    ActualCycleTimeSec INT NOT NULL
);
GO
