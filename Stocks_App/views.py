from django.shortcuts import render
from .models import *
from .utils import *


def index(request):
    return render(request, 'index.html')


def Query_Results(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT I.Name, ROUND(SUM(S.Price * B.BQuantity),3) as TotalSum
                        FROM Investor I inner join diverseInvestorsIDs DI on I.ID = DI.ID
                        inner join Buying B on DI.ID = B.ID
                        inner join Stock S on S.Symbol = B.Symbol and S.tDate = B.tDate
                        GROUP BY DI.ID, I.Name
                        ORDER BY TotalSum DESC
                        """)
        sql_res1 = dictfetchall(cursor)
        cursor.execute("""
                        SELECT maxInvestor.symbol, I.Name, maxInvestor.maxNum as Quantity
                        FROM stockPerCompanyAndInvestor SPC inner join
                        (SELECT SPC.symbol, MAX(stockSum) as maxNum
                        FROM stockPerCompanyAndInvestor SPC
                        GROUP BY SPC.symbol) AS maxInvestor
                        on SPC.symbol = maxInvestor.symbol and SPC.stockSum = maxInvestor.maxNum
                        inner join Investor I on SPC.id = I.ID
                        ORDER BY symbol ASC, I.Name ASC
                        """)
        sql_res2 = dictfetchall(cursor)

        cursor.execute("""
                        SELECT PC.Symbol, COUNT(B.ID) as BuyersNumber
                        FROM profitableCompanies PC left join Buying B on 
                        PC.Symbol = B.Symbol and PC.firstDate = B.tDate
                        GROUP BY PC.Symbol
                        ORDER BY PC.Symbol ASC;
                        """)
        sql_res3 = dictfetchall(cursor)

    return render(request, 'Query_Results.html',
                  {'sql_res1': sql_res1, 'sql_res2': sql_res2, 'sql_res3': sql_res3})


def Add_Transaction(request):
    idErrorFlag = False
    dateErrorFlag = False

    if request.method == 'POST' and request.POST:
        input_ID = int(request.POST['ID'])
        input_transactionSum = float(request.POST['transactionSum'])

        with connection.cursor() as cursor:
            lastDate = getLastDate()
            idErrorFlag = idExists(input_ID)

            if not idErrorFlag:
                prevAmount = getPrevAmount(input_ID)

            cursor.execute("""
                            SELECT MAX(T.tDate) as maxDate
                            FROM Transactions T
                            WHERE  T.ID = %s
                            """, [input_ID])
            dateTransactions = dictfetchall(cursor)[0]['maxDate']

            if lastDate == dateTransactions:
                dateErrorFlag = True

            if idErrorFlag is False and dateErrorFlag is False:
                investor_instance = Investor.objects.get(id=input_ID)
                newAmount = prevAmount + input_transactionSum
                Transactions.objects.create(tdate=lastDate, id=investor_instance, tamount=input_transactionSum)
                investor_instance.amount = newAmount
                investor_instance.save()

    with connection.cursor() as cursor:
        cursor.execute("""
                        SELECT TOP 10 *
                        FROM Transactions T
                        ORDER BY tDate DESC, ID DESC
                        """)
        lastTransactions = dictfetchall(cursor)

    return render(request, 'Add_Transaction.html',
                  {'lastTransactions': lastTransactions, 'idErrorFlag': idErrorFlag,
                   'dateErrorFlag': dateErrorFlag})


def Buy_Stocks(request):
    minusErrorFlag = False
    idErrorFlag = False
    companyErrorFlag = False
    dateCompanyErrorFlag = False

    if request.method == 'POST' and request.POST:
        input_ID = int(request.POST['ID'])
        input_Symbol = request.POST['Symbol']
        input_bQuantity = int(request.POST['BQuantity'])

        lastDate = getLastDate()
        idErrorFlag = idExists(input_ID)
        companyErrorFlag = symbolExist(input_Symbol)
        dateCompanyErrorFlag = dateCompanyError(lastDate, input_ID, input_Symbol)

        if idErrorFlag is False and companyErrorFlag is False:
            prevAmount = getPrevAmount(input_ID)
            stockPrice = getStockPrice(input_Symbol, lastDate)
            if prevAmount < stockPrice * input_bQuantity:
                minusErrorFlag = True

            if minusErrorFlag is False and dateCompanyErrorFlag is False:
                insertBuying(lastDate, input_ID, input_Symbol, input_bQuantity)
                Investor.objects.filter(id=input_ID).update(amount=prevAmount - stockPrice * input_bQuantity)

    lastBought = lastTenStocksBuy()

    return render(request, 'Buy_Stocks.html', {'lastBought': lastBought, 'idErrorFlag': idErrorFlag,
                                               'companyErrorFlag': companyErrorFlag,
                                               'minusErrorFlag': minusErrorFlag,
                                               'dateCompanyErrorFlag': dateCompanyErrorFlag})
