from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.db import connection
def home(request):
    q = f"select * from gold_scheme_masters "

    # query = f'''
    # SELECT 1 as Bid,branchname,branchpic, SUM(TotalAmount) as Amt,sum(discount) as discount, sum(tax) as tax,sum(packingcharge) as pk,sum(netamount) as netamt,count(*) as BillCount FROM [TONICOKTM].[TONICOUNIKTM20242025].[dbo].[billmaster] as Ktm,[JSGSRV].[tonicoweb].[dbo].[tonico_erp_branch] as srv where srv.id=1 and Division <>'CHAI' and billdate='{formatted_date} ' group by branchname,branchpic union all SELECT 2 as Bid,branchname,branchpic, SUM(TotalAmount) as Amt ,sum(discount) as discount, sum(tax) as tax,sum(packingcharge) as pk,sum(netamount) as netamt,count(*) as BillCount FROM [TONICOKKD].[TONICOUNIEKM20242025].[dbo].[billmaster] as Ktm,[JSGSRV].[tonicoweb].[dbo].[tonico_erp_branch] as srv where srv.id=2 and billdate='{formatted_date} ' group by branchname,branchpic union all SELECT 3 as Bid,branchname,branchpic, SUM(TotalAmount) as Amt  ,sum(discount) as discount, sum(tax) as tax,sum(packingcharge) as pk,sum(netamount) as netamt,count(*) as BillCount FROM [TONICO-NH].[TONICOUNICKDY20242025].[dbo].[billmaster] as Ktm,[JSGSRV].[tonicoweb].[dbo].[tonico_erp_branch] as srv where srv.id=3 and billdate='{formatted_date} ' group by branchname,branchpic union all SELECT 4 as Bid,branchname,branchpic, SUM(TotalAmount) as Amt  ,sum(discount) as discount, sum(tax) as tax,sum(packingcharge) as pk,sum(netamount) as netamt,count(*) as BillCount FROM [TONICOKTM].[TONICOUNIKTM20242025].[dbo].[billmaster] as Ktm,[JSGSRV].[tonicoweb].[dbo].[tonico_erp_branch] as srv where srv.id=4 and Division ='CHAI' and billdate='{formatted_date} ' group by branchname,branchpic
    # '''
    with connection.cursor() as cursor:
        cursor.execute(q)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                'billdate': row[0],
                # 'billno': row[1],
                # 'tableid': row[2],
                # 'totalqty': row[3],
                # 'totalamount': row[4],
                # 'discount': row[5],
                # 'SGST': (row[6]) / 2,
                # 'CGST': (row[6]) / 2,
                # 'packingcharge': row[7],
                # 'roundoff': row[8],
                # 'netamount': row[9],
                # 'packs': row[10],
                # 'Packagemode': row[11],
                # 'remarks': row[12],
            })
            context={'sdata': data}

    return render(request,"home.html",context)


def login_user(request):
    if(request.method=="POST"):
        uname=request.POST['u']
        pwd=request.POST['p']

        print(uname + pwd)
        user=authenticate(request,username=uname,password=pwd)
        print (user)
        if (user):
            login(request,user)
            return redirect('scheme')
        else:
            return HttpResponse("Invalid User")

    return render(request,'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def scheme(request):
    if request.user.is_authenticated:
        branchid = request.user.branchid
        q=f"select * from branches where id={branchid}"

        with connection.cursor() as cursor1:
            cursor1.execute(q)
            rows1 = cursor1.fetchall()

            branchname=rows1[0][1]

            report_type = request.POST.get('report')

        try:
            start_date1 = request.POST.get('start_date1', date.today().strftime('%Y-%m-%d'))
            sdate= request.POST.get('start_date1', date.today().strftime('%d-%m-%Y'))
            end_date1 = request.POST.get('end_date1', date.today().strftime('%Y-%m-%d'))
            edate = request.POST.get('end_date1', date.today().strftime('%d-%m-%Y'))
        except ValueError:
            # Handle invalid date format
            start_date1 = date.today()
            end_date1 = date.today()

    if report_type == 'None':
        report_type = '1'

    if report_type == '1':
        query = f"SELECT     gsm.id,    u.name,    u.phone,    gsm.scheme_id,    gsm.erp_scheme_id,    CASE        WHEN gsd.payment_method = 1 THEN 'Cash'        WHEN gsd.payment_method = 2 THEN 'UPI'        WHEN gsd.payment_method = 3 THEN 'Card'        WHEN gsd.payment_method = 4 THEN 'Netbanking'        ELSE 'Unknown'    END AS payment_method,    gsd.amount,    gsd.gold_weight,    gsd.gold_rate,    gsm.start_date FROM     gold_scheme_masters gsm JOIN     gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id JOIN  users u ON gsm.user_id = u.id WHERE    gsm.start_date between '{start_date1}'  and '{end_date1}'  AND gsm.branch_id = {branchid};"

        print("Report type 1 selected.")
    elif report_type == '2':
        query = f"SELECT     gsm.id,    u.name,    u.phone,    gsm.scheme_id,    gsm.erp_scheme_id,    CASE        WHEN gsd.payment_method = 1 THEN 'Cash'        WHEN gsd.payment_method = 2 THEN 'UPI'        WHEN gsd.payment_method = 3 THEN 'Card'        WHEN gsd.payment_method = 4 THEN 'Netbanking'        ELSE 'Unknown'    END AS payment_method,    gsd.amount,    gsd.gold_weight,    gsd.gold_rate,    gsd.`current_date` FROM     gold_scheme_masters gsm JOIN     gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id JOIN  users u ON gsm.user_id = u.id WHERE    gsd.`current_date` between '{start_date1}'  and '{end_date1}'  AND gsm.branch_id = {branchid};"

        print("Report type 2 selected.")
    else:
        query = f"SELECT     gsm.id,    u.name,    u.phone,    gsm.scheme_id,    gsm.erp_scheme_id,    CASE        WHEN gsd.payment_method = 1 THEN 'Cash'        WHEN gsd.payment_method = 2 THEN 'UPI'        WHEN gsd.payment_method = 3 THEN 'Card'        WHEN gsd.payment_method = 4 THEN 'Netbanking'        ELSE 'Unknown'    END AS payment_method,    gsd.amount,    gsd.gold_weight,    gsd.gold_rate,    gsm.start_date FROM     gold_scheme_masters gsm JOIN     gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id JOIN  users u ON gsm.user_id = u.id WHERE    gsm.start_date between '{start_date1}'  and '{end_date1}'  AND gsm.branch_id = {branchid};"




    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'scheme_id': row[3],
                'erp_scheme_id': row[4],
                'payment_method': row[5],
                'amount': row[6],
                'goldweight': row[7],
                'goldrate': row[8],
                'start_date': row[9].strftime('%d/%m/%Y'),
                # Safely format date
            })

            total_amt = sum(int(item['amount'] )for item in data)
            total_wt = sum(float(item['goldweight']) for item in data)
            if report_type == '1':
                k="Joining Report"
            elif report_type == '2':
                k = "Payment Report"
            else:
                k=""

        context={"sdata":data,"branchid":branchid,"totalamt":total_amt,"totalwt":total_wt,"sdate":sdate,"edate":edate,"branch":branchname,"rtype":k,}


    return render(request, 'scheme.html', context)


def chitdetails(request ,id):

    if request.user.is_authenticated:
        branchid = request.user.branchid
        query = f"SELECT      CASE        WHEN gsd.payment_method = 1 THEN 'Cash'        WHEN gsd.payment_method = 2 THEN 'UPI'        WHEN gsd.payment_method = 3 THEN 'Card'        WHEN gsd.payment_method = 4 THEN 'Netbanking'        ELSE 'Unknown'    END AS payment_method,    gsd.amount,    gsd.gold_weight,    gsd.gold_rate,    gsd.`current_date` FROM     gold_scheme_masters gsm JOIN     gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id JOIN  users u ON gsm.user_id = u.id WHERE    erp_scheme_id='{id}'  AND gsm.branch_id = {branchid};"

        with connection.cursor() as cursor2:
            cursor2.execute(query)
            rows = cursor2.fetchall()
            data = []
            for row in rows:
                data.append({
                    'transid': row[0],
                    'amount': row[1],
                    'goldweight': row[2],
                    'goldrate': row[3],
                    'start_date': row[4].strftime('%d/%m/%Y'),
                    # Safely format date
                })
                context={"sdata":data}

    return render(request,"chitdetails.html",context)


