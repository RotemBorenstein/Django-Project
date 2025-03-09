from django.db import connection
from .models import *


def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict '''
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def getLastDate():
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT Max(S.tDate) as lastDate
                        FROM Stock S
                        """)
        result = dictfetchall(cursor)
        if result and result[0]:
            return result[0]['lastDate']
        else:
            return None


def idExists(input_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT I.ID
                        FROM Investor I
                        """)
        invesrtorIDsList = dictfetchall(cursor)

        for dict_ in invesrtorIDsList:
            if input_ID == dict_['ID']:
                return False

        return True


def getPrevAmount(input_ID):
    with connection.cursor() as cursor:
        cursor.execute("""
                            SELECT I.Amount
                            FROM Investor I
                            WHERE I.ID = %s
                            """, [input_ID])
        prevAmount = dictfetchall(cursor)

        if prevAmount and prevAmount[0]:
            return prevAmount[0]['Amount']


def symbolExist(input_Symbol):
    error = False
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT C.Symbol
                        FROM Company C
                        """)
        symbolList = dictfetchall(cursor)
        symbols = [d['Symbol'] for d in symbolList]

        if input_Symbol not in symbols:
            error = True
        return error


def getStockPrice(input_Symbol, lastDate):
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT S.price
                        FROM STOCK S
                        WHERE S.Symbol = %s and S.tDate = %s
                        """, [input_Symbol, lastDate])
        stockPrice = dictfetchall(cursor)
        if stockPrice and stockPrice[0]:
            return stockPrice[0]['price']


def dateCompanyError(lastDate, input_ID, input_Symbol):
    error = False
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT B.ID
                        FROM Buying B
                        WHERE B.tDate = %s and B.ID = %s and B.Symbol = %s
                        """, [lastDate, input_ID, input_Symbol])
        idSymbol = dictfetchall(cursor)

    if len(idSymbol):
        error = True
    return error


def lastTenStocksBuy():
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT TOP 10 *
                        FROM Buying B
                        ORDER BY tDate DESC, ID DESC, Symbol ASC 
                        """)
        lastBought = dictfetchall(cursor)
    return lastBought


def insertBuying(lastDate, input_ID, input_Symbol, input_bQuantity):
    with connection.cursor() as cursor:
        cursor.execute("""
                         INSERT INTO Buying(tdate,ID,Symbol, BQuantity) 
                         VALUES (%s,%s,%s,%s)
                        """, (lastDate, input_ID, input_Symbol, input_bQuantity))
