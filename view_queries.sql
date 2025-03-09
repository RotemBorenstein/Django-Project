CREATE VIEW diverseInvestorsIDs AS
SELECT DISTINCT B.ID
FROM Buying B inner join Company C on B.Symbol = C.Symbol
GROUP BY B.ID, B.tDate
HAVING COUNT(DISTINCT C.Sector) >= 6;


CREATE VIEW firstCond AS
SELECT DISTINCT C.Symbol, C.Sector
FROM Company C inner join Buying B on C.Symbol = B.Symbol
WHERE NOT EXISTS(
    SELECT DISTINCT B1.tDate
    FROM Buying B1
        EXCEPT
    SELECT DISTINCT B2.tDate
    FROM Company C2 inner join Buying B2 on C2.Symbol = B2.Symbol
    WHERE C.Symbol = C2.Symbol
    );


CREATE VIEW singleSector AS
SELECT C.Sector
FROM firstCond FC inner join Company C on FC.Symbol = C.Symbol
GROUP BY C.Sector
HAVING COUNT(*) = 1;


CREATE VIEW popularCompany AS
SELECT FC.Symbol
FROM singleSector S inner join firstCond FC on S.Sector = FC.Sector;


CREATE VIEW stockPerCompanyAndInvestor AS
SELECT B.id, PC.symbol, SUM(B.BQuantity) as stockSum
FROM popularCompany PC inner join Buying B on PC.Symbol = B.Symbol
GROUP BY B.ID, PC.Symbol;


CREATE VIEW Dates AS
SELECT MIN(S.tDate) as firstDate, Max(S.tDate) as lastDate
FROM Stock S;


CREATE VIEW profitableCompanies AS
SELECT D.firstDate, S1.Symbol
FROM Dates D inner join Stock S1 on S1.tDate = D.firstDate
    inner join Stock S2 on S2.tDate = D.lastDate and S1.Symbol = S2.Symbol
WHERE S2.Price > 1.06 * S1.Price;