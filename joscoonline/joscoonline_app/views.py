import math
import re
from datetime import date, datetime
from os import truncate
from random import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from dateutil.relativedelta import relativedelta
import random
# Create your views here.
from django.db import connection, connections


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
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    branchid = request.user.branchid
    branchname = "Unknown Branch"  # Default value for branch name

    # Fetch branch name
    query_branch = f"SELECT name FROM branches WHERE id={branchid}"
    with connection.cursor() as cursor:
        cursor.execute(query_branch)
        branch_row = cursor.fetchone()
        if branch_row:
            branchname = branch_row[0]

    # Get `report_type` and date inputs
    report_type = request.POST.get('report', '1')  # Default to '1'
    start_date1 = request.POST.get('start_date1', date.today().strftime('%Y-%m-%d'))
    sdate = request.POST.get('start_date1', date.today().strftime('%d-%m-%Y'))
    end_date1 = request.POST.get('end_date1', date.today().strftime('%Y-%m-%d'))
    edate = request.POST.get('end_date1', date.today().strftime('%d-%m-%Y'))

    # Build SQL query based on report type
    search_query="hello"

    search_query = request.POST.get('search_data', '').strip()
    if search_query !='':
        search_query = request.POST.get('search_data', '').strip()
        QQ = "Joining Report"
        query = f"""
                   SELECT gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id,
                          sum(gsd.amount) as amount, sum(gsd.gold_weight) as gold_weight , avg(gsd.gold_rate) as gold_rate , gsm.start_date
                   FROM gold_scheme_masters gsm
                   JOIN gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id
                   JOIN users u ON gsm.user_id = u.id
                   WHERE 
                     gsm.branch_id = {branchid}  and erp_scheme_id ='{ search_query }' group by gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id,gsm.start_date;
               """
    else:
        if report_type == '1':
            QQ = "Joining Report"
            query = f"""
                SELECT gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id,
                       SUM(gsd.amount) AS amount,
                       TRUNCATE(SUM(gsd.gold_weight), 3) AS gold_weight,
                       ROUND(AVG(gsd.gold_rate), 2) AS gold_rate,
                       gsm.start_date
                FROM gold_scheme_masters gsm
                JOIN gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id
                JOIN users u ON gsm.user_id = u.id
                WHERE gsm.start_date BETWEEN '{start_date1}' AND '{end_date1}'
                  AND gsm.branch_id = {branchid}
                GROUP BY gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id, gsm.start_date;
            """
        elif report_type == '2':
            QQ = "Payment Report"
            query = f"""
            SELECT gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id,
                  
                   gsd.amount, gsd.gold_weight, gsd.gold_rate, gsd.current_date
            FROM gold_scheme_masters gsm
            JOIN gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id
            JOIN users u ON gsm.user_id = u.id
            WHERE gsd.current_date BETWEEN '{start_date1}' AND '{end_date1}'
              AND gsm.branch_id = {branchid};
            """
        elif report_type == '3':
                QQ = "Closed Report"
                query = f"""
                   SELECT gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id,
                   
                   sum(gsd.amount) as amount, TRUNCATE(sum(gsd.gold_weight),3) as gold_weight , round(avg(gsd.gold_rate),2) as gold_rate , gsm.closing_date
            FROM gold_scheme_masters gsm
                    JOIN gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id
                    JOIN users u ON gsm.user_id = u.id
                    WHERE gsm.closing_date BETWEEN '{start_date1}' AND '{end_date1}'
                      AND gsm.branch_id = {branchid} group by gsm.id, u.name, u.phone, gsm.scheme_id, gsm.erp_scheme_id , gsm.closing_date; """
        else:
                   pass

    # Execute the query and process results
    with connection.cursor() as cursor:
        print(query)
        cursor.execute(query)
        rows = cursor.fetchall()

    data = [
        {
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'scheme_id': row[3],
            'erp_scheme_id': row[4],
            'payment_method':row[4],
            'amount': row[5],
            'goldweight': row[6],
            'goldrate': row[7],
            'start_date': row[8].strftime('%d/%m/%Y'),
        }
        for row in rows
    ]

    # Calculate totals
    total_amt = sum(int(item['amount']) for item in data)
    total_wt = sum(float(item['goldweight']) for item in data)

    # Prepare context and render
    context = {
        "sdata": data,
        "branchid": branchid,
        "totalamt": total_amt,
        "totalwt": float(f"{total_wt:.3f}"),
        "sdate": sdate,
        "edate": edate,
        "branch": branchname,
        "rtype": QQ,
        "searchquery":search_query,
    }
    return render(request, 'scheme.html', context)


def chitdetails(request, id):
    schemeid=0
    if request.user.is_authenticated:
        branchid = request.user.branchid

        # Query for gold scheme details
        query = f"""
            SELECT 
                CASE
                    WHEN gsd.payment_method = 1 THEN 'Cash'
                    WHEN gsd.payment_method = 2 THEN 'UPI'
                    WHEN gsd.payment_method = 3 THEN 'Card'
                    WHEN gsd.payment_method = 4 THEN 'Netbanking'
                    ELSE 'Unknown'
                END AS payment_method,
                gsd.amount,
                gsd.gold_weight,
                gsd.gold_rate,
                gsd.current_date,
                gsm.id
            FROM 
                gold_scheme_masters gsm
            JOIN 
                gold_scheme_details gsd ON gsm.id = gsd.scheme_master_id
            JOIN 
                users u ON gsm.user_id = u.id
            WHERE 
                erp_scheme_id = '{id}' AND gsm.branch_id = {branchid};
        """

        with connection.cursor() as cursor2:
            cursor2.execute(query)
            rows = cursor2.fetchall()
            data = [
                {
                    'transid': row[0],
                    'amount': row[1],
                    'goldweight': row[2],
                    'goldrate': row[3],
                    'start_date': row[4].strftime('%d/%m/%Y') ,
                    'schemeid=': row[5]
                }
                for row in rows
            ]
        if rows:
          schemeid = rows[-1][5]
        # Query for user details and nominee info
        query1 = f"""
            SELECT 
                kyc.name,
                u.phone,
                kyc.address,
                gsm.start_date,
                gsm.scheme_end_date,
                gsm.status,
                gsm.closing_date,
                gsm.invoice_number,
                kyc.type,
                gsm.scheme_peroid
               
            FROM 
                gold_scheme_masters gsm
            JOIN 
                users u ON gsm.user_id = u.id
            LEFT JOIN 
                user_kycs kyc ON u.id = kyc.user_id
            WHERE 
                gsm.erp_scheme_id = '{id}' AND gsm.branch_id = {branchid}
                AND u.name <> ''
                AND (kyc.user_id IS NULL OR kyc.name <> '');
        """

        with connection.cursor() as cursor3:
            cursor3.execute(query1)
            rows1 = cursor3.fetchall()
            data1 = []
            today = datetime.today()

            for row1 in rows1:
                start_date = row1[3]
                months_diff = (
                        (today.year - start_date.year) * 12 + today.month - start_date.month
                ) if start_date else 0


                address_trimmed = row1[2].split('[')[0] if row1[2] and '[' in row1[2] else row1[2] or ""
                if row1[2] and len(row1[2]) > 0:
                    address_trimmed = row1[2].split('[')[0] if '[' in row1[2] else row1[2]
                    match = re.search(r'\[.*?\]', row1[2])
                    nominee_info = match.group(0) if match else "chumma"  # Extract the nominee info
                    print(nominee_info)
                else:
                    address_trimmed = ""
                    nominee_info = ""

                data1.append({
                    'name': row1[0],
                    'phone': row1[1],
                    'address': address_trimmed,
                    'start_date': row1[3],
                    'end_date': row1[4],
                    'status': row1[5],
                    'closingdate': row1[6],
                    'invoice': row1[7],
                    'type': row1[8],
                    'period': row1[9],
                    'monthdif': months_diff,
                    'nomineeinfo': nominee_info,
                })

        # Totals
        total_amt = sum(int(item.get('amount', 0)) for item in data)
        total_wt = sum(float(item['goldweight']) for item in data)

        # Context for rendering
        context = {
            "sdata": data,
            "totalamt": total_amt,
            "totalwt": float(f"{total_wt:.3f}"),
            "mdata": data1,"schemeID":schemeid,
        }

        return render(request, "chitdetails.html", context)

    # If not authenticated, redirect or show an error page
    return HttpResponse("Unauthorized", status=401)

def addpayment(request):
    if (request.method == "POST"):
        schemeID= request.POST.get('schemeID')
        dt = request.POST.get('date')
        grate=int(request.POST.get('gold_rate'))
        amt=int(request.POST.get('amount'))
        pm=request.POST.get('payment_method')
        wt= amt/grate

        dt_value = datetime.strptime(dt, "%Y-%m-%d")  # Convert string to datetime if needed

        # Add 1 month to the date
        new_date = dt_value + relativedelta(months=1)

        # Format the date to 'yyyy-MM-dd'
        formatted_date = new_date.strftime("%Y-%m-%d")

        query=f""" insert into gold_scheme_details(scheme_master_id,amount,gold_weight,gold_rate,status,payment_status,raz_order_id,transaction_id,next_due,`current_date`,payment_method,payment_mode) values({ schemeID} ,{amt} ,{math.trunc(wt*1000)/1000},{grate} ,1,1,'BANK','BANK','{formatted_date }','{  dt_value}',{pm},1)     """
        with connection.cursor() as cursor:
            cursor.execute(query)
            # Commit the transaction if needed (unnecessary if you have autocommit enabled)
            connection.commit()

        query1=f""" select * from gold_scheme_masters where id={schemeID}"""
        with connection.cursor() as cursor1:
            cursor1.execute(query1)
            result = cursor1.fetchone()  # Get the first row (if there is one)
            amount1=int(result[4])
            gwt1=result[5]
            ERPID=result[3]

            gamt=int(amount1)+int(amt)
            gwt=math.trunc((float(gwt1)+float(wt))*1000)/1000

        query1 = f""" update gold_scheme_masters  set amount_accumulated ={gamt},gold_accumulated={gwt},total_amount_accumulated={gamt},total_gold_weight={gwt} where id={schemeID}"""
        with connection.cursor() as cursor2:
            cursor2.execute(query1)
   # chitdetails(request,  ERPID)

        return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container d-flex align-items-center justify-content-center vh-100">
            <div class="text-center">
                <div class="mb-4">
                    <img src="https://via.placeholder.com/150" alt="Thank You" class="img-fluid rounded-circle">
                </div>
                <h1 class="display-4 text-success">Thank You!</h1>
                <p class="lead">Your payment has been processed successfully.</p>
                <p class="text-muted">We appreciate your trust in our services.</p>
                <a href="/" class="btn btn-primary mt-3" onclick="closeWindow()">Close</a>
            </div>
        </div>

        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    <script>
    function closeWindow() {
        window.open('', '_self'); // Ensure compatibility
        window.close();
    }
</script>
    """)

# def get_gold_rate(request):
#         print(request.GET.get('todate') + "  test     ")
#         selected_date = request.GET.get('todate')
#         try:
#             query=f""" select rate from gold_rate_logs where `current_date`='{selected_date}' and gold_purity=4     """
#             with connection.cursor() as cursor3:
#                 cursor3.execute(query1)
#                 rows1 = cursor3.fetchone()
#                 gold_rate = rows1[0]
#                 print(gold_rate + "      Sucess")
#                 return JsonResponse({'success': True, 'gold_rate': str(gold_rate)})
#         except:
#                 print("     Error")
#                 return JsonResponse({'success': False, 'gold_rate': str(0)})
def addnewscheme(request):
    context = {}
    if request.method == 'POST':
        today = datetime.today()
        formatted_date = today .strftime("%Y-%m-%d")
        query = f""" SELECT rate FROM gold_rate_logs WHERE `current_date`='{formatted_date}' and gold_purity=4 """ # Use parameterized query to prevent SQL injection

        with connection.cursor() as cursor:
            cursor.execute(query)
            result2 = cursor.fetchone()  # Get the first matching row
            if result2:
                context['gold_rate'] = result2[0]
            else:
                context['gold_rate'] = 0

        phone = request.POST.get('phone')
        name = request.POST.get('name')
        email = request.POST.get('email')
        context['name'] =name
        context['phone'] =phone
        context['email'] = email

        query = "SELECT * FROM users WHERE phone = %s"  # Use parameterized query to prevent SQL injection

        with connection.cursor() as cursor:
            cursor.execute(query, [phone])
            result = cursor.fetchone()  # Get the first matching row
        print("Upto hear OK")
        if result:
            context['ID'] = result[0]  # Assuming the address is in the first column

            query3 = "SELECT erp_scheme_id FROM gold_scheme_masters WHERE user_id = %s"

            with connection.cursor() as cursor5:
                cursor5.execute(query3, [result[0]])  # Pass the parameter as a list
                result5 = cursor5.fetchall() # Get the first matching row
                data = [
                    {
                        'schemes': row[0]

                    }
                    for row in result5
                ]
                context['schemes'] = data

            query = f"""  SELECT * FROM user_kycs WHERE User_id ={result[0]} """  # Use parameterized query to prevent SQL injection

            with connection.cursor() as cursor:
                cursor.execute(query)
                result1 = cursor.fetchone()  # Get the first matching row
                if result1:
                       context['address'] = result1[3]
                else:
                    context['address'] = "None"
            context['exists'] = True
        else:

            query = f"""  insert into users (name,email,country_code,phone,status,is_complete) values('{name}','{email}','91','{phone}',1,1) """  # Use parameterized query to prevent SQL injection
            print(query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            query = "SELECT * FROM users WHERE phone = %s"  # Use parameterized query to prevent SQL injection

            with connection.cursor() as cursor:
                cursor.execute(query, [phone])
                result = cursor.fetchone()  # Get the first matching row
            context['ID'] = result[0]
            context['phone'] = phone  # Keep the phone number in the form for user reference

    return render(request, 'addnewscheme.html', context)


def addnewschemedetails(request):
    if request.method == 'POST':
        try:
            # Get data from POST request
            user_id = request.POST.get('user_id')
            address = request.POST.get('address')
            document = request.POST.get('document')  # Not used, remove if unnecessary
            relation = request.POST.get('relation')  # Not used, remove if unnecessary
            types = request.POST.get('type')
            dates = request.POST.get('date')
            gold_rate = request.POST.get('gold_rate')
            amount = request.POST.get('amount')
            name = request.POST.get('name1')
            payment_method = request.POST.get('payment_method')
            branchid = request.user.branchid

            # Validate required fields
            if not (user_id and address and types and dates and gold_rate and amount and name and payment_method):
                return HttpResponse("Missing required fields.", status=400)

            # Calculate derived values
            grate = int(gold_rate)
            amt = int(amount)
            gtt = math.trunc((amt / grate) * 1000) / 1000
            wt = gtt

            # Generate scheme_id and transaction_id
            scheme_id = generate_unique_scheme_id()
            tid = f"{payment_method}_{random.randint(1, 100000)}"

            # Calculate dates
            start_date = datetime.strptime(dates, "%Y-%m-%d")
            next_due = start_date + relativedelta(months=1)
            scheme_end_date = start_date + relativedelta(months=10)

            # Format dates for SQL
            start_date_str = start_date.strftime('%Y-%m-%d')
            next_due_str = next_due.strftime('%Y-%m-%d')
            scheme_end_date_str = scheme_end_date.strftime('%Y-%m-%d')

            # Insert into user_kycs
            if not searchrecord(user_id):

                user_kyc_query = """
                INSERT INTO user_kycs (user_id, name, address, type, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(user_kyc_query, [user_id, name, address, types, 0])

            # Insert into gold_scheme_masters
            gold_scheme_master_query = """
                INSERT INTO gold_scheme_masters 
                (user_id, scheme_id, amount_accumulated, gold_accumulated, last_reduced, total_gold_weight, 
                 order_id, total_amount_accumulated, purchased_amount, branch_id, refund, discount_percentage, 
                 status, scheme_peroid, start_date, next_due, scheme_end_date, erp_scheme_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(gold_scheme_master_query, [
                    user_id, scheme_id, amt, wt, 0, wt, 0, amt, 0, branchid, 0, 3.5, 1, 10,
                    start_date_str, next_due_str, scheme_end_date_str, ''
                ])

            # Get the newly inserted gold_scheme_masters ID
            get_scheme_id_query = """
                SELECT id FROM gold_scheme_masters WHERE user_id=%s AND scheme_id=%s
            """
            with connection.cursor() as cursor:
                cursor.execute(get_scheme_id_query, [user_id, scheme_id])
                result = cursor.fetchone()
                if not result:
                    return HttpResponse("Failed to retrieve scheme ID.", status=500)

                scheme_master_id = result[0]

            # Insert into gold_scheme_details
            gold_scheme_details_query = """
                INSERT INTO gold_scheme_details 
                (scheme_master_id, amount, gold_weight, gold_rate, status, payment_status, 
                 raz_order_id, transaction_id, next_due, `current_date`, payment_mode, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(gold_scheme_details_query, [
                    scheme_master_id, amt, wt, grate, 1, 1, payment_method, tid,
                    next_due_str, start_date_str, 1, payment_method
                ])

            # Return success page
            return HttpResponse("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Thank You</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container d-flex align-items-center justify-content-center vh-100">
                        <div class="text-center">
                            <div class="mb-4">
                                <img src="https://via.placeholder.com/150" alt="Thank You" class="img-fluid rounded-circle">
                            </div>
                            <h1 class="display-4 text-success">Thank You!</h1>
                            <p class="lead">New Scheme processed successfully.</p>
                            <p class="text-muted">We appreciate your trust in our services.</p>
                            <a href="/" class="btn btn-primary mt-3">Close</a>
                        </div>
                    </div>
                </body>
                </html>
            """)

        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

def generate_unique_scheme_id():
    scheme_id = ""
    is_unique = False

    while not is_unique:
        # Generate a random scheme ID in the format "JS_O_XXXXXXXX" where X is a random 8-digit number
        scheme_id = f"JS_O_{random.randint(0, 99999999):08d}"

        # Check if the generated scheme ID already exists in the database
        query = "SELECT COUNT(*) FROM gold_scheme_masters WHERE scheme_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [scheme_id])
            count = cursor.fetchone()[0]

        # If count is 0, the scheme ID is unique
        if count == 0:
            is_unique = True

    return scheme_id



def searchrecord(table,condition):
    query = f"""SELECT COUNT(*) FROM {table} WHERE {condition}"""
    with connection.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
    if count == 0:
        is_unique = True
    else:
        is_unique = False
    return(is_unique)


def findrecord(table,condition,value):
    query = f"""SELECT {value} FROM {table} WHERE {condition}"""
    print(query)
    with connection.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        return(count)





def indsoftintegration(request):
    context = {}



    start_date1 = request.POST.get('start_date1', date.today().strftime('%m-%d-%Y'))
    sdate = request.POST.get('start_date1', date.today().strftime('%d-%m-%Y'))
    end_date1 = request.POST.get('end_date1', date.today().strftime('%m-%d-%Y'))
    edate = request.POST.get('end_date1', date.today().strftime('%d-%m-%Y'))

    for alias in connections.databases:
        print(f"Connection Alias: {alias}")
        print(f"Configuration: {connections.databases[alias]}")

    try:
        cn = '46'  # Assuming 'ekm' is the connection alias
        with connections[cn].cursor() as cursor:
            print("Connection successful!")

            # Create the table if it doesn't exist
            query = """ 
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'CHITRCPTID')
                CREATE TABLE CHITRCPTID (
                    id INT 
                );
                """
            cursor.execute(query)

            # Fetch data from the database
            query = f"""
                SELECT DISTINCT cm.chit_key, chit_no, cm.cust_name, 
                    ccm.Address + ', ' + ccm.Address1 + ', ' + ccm.Address2 + 
                    ' [ Nominee : ' + cm.Nominee + '( ' + cm.Nrelation + ' )]' AS Address, 
                    CASE 
                        WHEN cm.Mobile = '' THEN ccm.phone_no 
                        ELSE cm.Mobile 
                    END AS Phone_no,
                    cm.Cust_Code
                FROM chitmast cm 
                JOIN CHITCUSTMAST ccm ON cm.ccust_key = ccm.CCust_key
                JOIN chitrcpt crp ON crp.chit_key = cm.chit_key
                WHERE cm.close_flag = 'N' 
                AND CONVERT(DATETIME, vch_date, 103) BETWEEN '{start_date1}' AND '{end_date1}'
                ORDER BY cm.chit_key
                """
            cursor.execute(query)
            result = cursor.fetchall()

            data = [
                {
                    'chit_key': row[0],
                    'chit_no': row[1],
                    'cust_name': row[2],
                    'address': row[3],
                    'phone': row[4],
                    'cust_code': row[5]
                }
                for row in result
            ]

            context = {'sdata': data}


    except Exception as e:
        print(f"Connection failed: {e}")

    return render(request, 'indsoftintegration.html', context)


def webupdate(request,cust_code=None, chit_key=None):
    if request.POST:
        branchid = request.user.branchid
        cn = str(branchid)  # Assuming 'ekm' is the connection alias
        with connections[cn].cursor() as cursor1:
            query=f""" SELECT    cm.chit_key,chit_no,cm.cust_name,cm.email,ccm.Address+', ' + ccm.Address1 + ', ' + ccm.Address2 + ' [ Nominee :' + cm.Nominee + '( ' + cm.Nrelation +' )]' as Address, case when cm.Mobile='' then ccm.phone_no else cm.Mobile End as Phone_no,cm.Cust_Code,cm.inst_no,cm.doj  FROM chitmast cm , CHITCUSTMAST ccm where  cm.ccust_key = ccm.CCust_key and  cm.cust_code='{cust_code}' """
            cursor1.execute(query)
            result=cursor1.fetchone()
            start_date = datetime.strptime(result[8], "%Y-%m-%d")
            next_due = start_date + relativedelta(months=1)
            scheme_end_date = start_date + relativedelta(months=10)

            # Format dates for SQL
            start_date_str = start_date.strftime('%Y-%m-%d')
            next_due_str = next_due.strftime('%Y-%m-%d')
            scheme_end_date_str = scheme_end_date.strftime('%Y-%m-%d')



        if result:
            scheme_id = f"JS_O_{random.randint(0, 99999999):08d}"

            if not searchrecord("gold_scheme_masters", "erp_scheme_id='" + cust_code + "' and branch_id=" + branchid):
                query=f"""INSERT INTO users (name, email, country_code, phone, status, is_complete) VALUES ('{result[2]}','{result[3]}','91','{result[5]}',1,1 """
                with connection.cursor() as cursor:
                 cursor.execute(query)
                user_id=findrecord("users","phone='" + result[5] +"' and name='" + result[2] +"'","id")
                query=f""" INSERT INTO user_kycs (user_id, name, address, type, status) VALUES ({user_id},'{result[2]}','{result[4]}','Aadhar Card',1"""
                cursor.execute(query)
                query=f""" INSERT INTO gold_scheme_masters (user_id, scheme_id, amount_accumulated, gold_accumulated, last_reduced, total_gold_weight, order_id, total_amount_accumulated, purchased_amount, branch_id, refund, discount_percentage, status, scheme_peroid, start_date, next_due, scheme_end_date, erp_scheme_id) VALUES({user_id},'{scheme_id}',0, 0, 0, 0, 0, 0, 0, {branchid}, 0, 3.5, 1,{result[7]},'{result[8]}','{next_due_str}','{scheme_end_date_str}','{cust_code}'"""
                cursor.execute(query)
                scheme_masterid=findrecord("gold_scheme_masters","erp_scheme_id='" + cust_code +"' and branchid=" +branchid,"id")

                query=f"""select vch_no,vch_date,Amount,conv_rate,gold_wt,rcpt_no,case when trx_type='C' then 1 else case when trx_type='A' then case when cheque_no=''  then 2 else 4 end  else case when trx_type='B'then 4 else 5  end end end as Trx from chitrcpt  where chit_key={chit_key}"""
                cursor1.executequery(query)
                rows=cursor1.fetchall()
                amt=0
                gwt=0
                for row1 in rows:
                    next_due = row1[1] + relativedelta(months=1)
                    next_due_str = next_due.strftime('%Y-%m-%d')
                    query=f"""INSERT INTO gold_scheme_details (scheme_master_id, amount, gold_weight, gold_rate, status, payment_status, raz_order_id, transaction_id, next_due, `current_date`, payment_mode, payment_method) VALUES( { scheme_masterid},{row1[2]},{row1[4]},{row1[3]},1,1,'BANK',{row1[5]},'{ next_due_str}','{row1[1]}',1,{row1[6]}"""
                    cursor.execute(query)
                    amt=amt +row1[2]
                    gwt=gwt+row1[4]
                query=f""" update gold_scheme_masters set amount_accumulated={amt},gold_accumulated={gwt} ,total_gold_weight={gwt},total_amount_accumulated={amt} where erp_scheme_id='{cust_code}' and branch_id={branchid} """
                cursor.execute(query)
            else:
                scheme_masterid = findrecord("gold_scheme_masters",
                                             "erp_scheme_id='" + cust_code + "' and branchid=" + branchid, "id")

                query = f"""select vch_no,vch_date,Amount,conv_rate,gold_wt,rcpt_no,case when trx_type='C' then 1 else case when trx_type='A' then case when cheque_no=''  then 2 else 4 end  else case when trx_type='B'then 4 else 5  end end end as Trx from chitrcpt  where chit_key={chit_key}"""
                cursor1.executequery(query)
                rows = cursor1.fetchall()
                amt = 0
                gwt = 0
                for row1 in rows:
                    next_due = row1[1] + relativedelta(months=1)
                    next_due_str = next_due.strftime('%Y-%m-%d')
                    query = f"""INSERT INTO gold_scheme_details (scheme_master_id, amount, gold_weight, gold_rate, status, payment_status, raz_order_id, transaction_id, next_due, `current_date`, payment_mode, payment_method) VALUES( {scheme_masterid},{row1[2]},{row1[4]},{row1[3]},1,1,'BANK',{row1[5]},'{next_due_str}','{row1[1]}',1,{row1[6]}"""
                    with connection.cursor() as cursor:
                        cursor.execute(query)
                    amt = amt + row1[2]
                    gwt = gwt + row1[4]
                query = f""" update gold_scheme_masters set amount_accumulated={amt},gold_accumulated={gwt} ,total_gold_weight={gwt},total_amount_accumulated={amt} where erp_scheme_id='{cust_code}' and branch_id={branchid} """
                cursor.execute(query)

    return HttpResponse("Updated")
