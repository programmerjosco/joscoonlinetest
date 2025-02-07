"""
URL configuration for joscoonline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from joscoonline_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path ('',views.home,name="home"),
    path('login',views.login_user,name="login"),
    path('logout', views.user_logout, name="logout"),
    path('closechit', views.closechit, name="closechit"),
    path('scheme',views.scheme,name="scheme"),
    path('chitdetails/<str:id>/',views.chitdetails,name="chitdetails"),
    path('addpayment', views.addpayment, name="addpayment"),
    path('addnewscheme', views.addnewscheme, name="addnewscheme"),
    path('addnewschemedetails', views.addnewschemedetails, name="addnewschemedetails"),
    path('indsoftintegration', views.indsoftintegration, name='indsoftintegration'),
    path('webupdate/<str:cust_code>/<int:chit_key>/', views.webupdate, name='webupdate'),
    path('webupdateall', views.webupdateall, name='webupdateall'),
    path('adduser', views.adduser, name="adduser"),
    path('chitsummary', views.chitsummary, name="chitsummary"),
    path('chitreconf', views.chitreconf, name="chitreconf"),
    path('reconsil', views.reconsil, name="reconsil"),
    path('indsoftdownload/', views.indsoftdownload, name='indsoftdownload'),
    path('updatemismatch', views.updatemismatch, name="updatemismatch"),
    path('razorpayreport', views.razorpayreport, name="razorpayreport"),
    # path('ewaybill', views.ewaybill, name="ewaybill"),
    path('updateid/<str:id>/', views.updateid, name="updateid"),
    # re_path(
    #     r'^indsoftintegration(?:/(?P<cust_code>[^/]*)/(?P<chit_key>[0-9]*)/)?$',
    #     views.indsoftintegration,
    #     name='indsoftintegration',
    # ),


    # path('get-gold-rate/', views.get_gold_rate, name='get_gold_rate'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)