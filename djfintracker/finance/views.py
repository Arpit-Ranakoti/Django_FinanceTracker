from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from finance.forms import RegisterForm,GoalForm,TransationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction,Goal
from django.db.models import Sum
from .admin import TransactionResource
# Create your views here.


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'finance/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm({
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password1': request.POST.get('password'),  
            'password2': request.POST.get('password2') 
        })

        if form.is_valid():
            user = form.save()  
            login(request, user)
            return redirect('dashboard')

        return render(request, 'finance/register.html', {'form': form})

class DashboardView(LoginRequiredMixin,View): 
    def get(self,request ,*args,**kwargs):
        transactions = Transaction.objects.filter(user = request.user)
        goals = Goal.objects.filter(user=request.user)

        total_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='Income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='Expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        net_savings= total_income - total_expense
        reamining_savings=net_savings
        goal_progress = []
        for goal in goals :
            if reamining_savings >= goal.target_amount :
                goal_progress.append({'goal':goal , 'progress':100})
                reamining_savings -= goal.target_amount
            elif reamining_savings >0:
                progress = (reamining_savings / goal.target_amount)*100
                goal_progress.append({'goal':goal, 'progress':progress})
                reamining_savings = 0
            else : 
                goal_progress.append({'goal':goal, 'progress':0})

        context = {
            'transactions':transactions,
            'total_income':total_income,
            'total_expense':total_expense,
            'net_savings':net_savings,
            'goal_progress':goal_progress,
        }
        return render(request,'finance/dashboard.html',context)
    
class TransactionCreateView(LoginRequiredMixin,View):
    #when load form
    def get(self,request,*args,**kwargs):
        form=TransationForm()
        return render(request,'finance/transaction_form.html',{'form':form})
    # we get form with data after submit
    def post(self,request ,*args,**kwargs):
        form = TransationForm(request.POST)
        if form.is_valid():
            transaction=form.save(commit=False)
            transaction.user= request.user
            transaction.save()
            return redirect('dashboard')
        return render(request,'finance/transaction_form.html',{'form':form})


class TransactionListView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        transactions=Transaction.objects.filter(user=request.user)
        return render(request,'finance/transaction_list.html',{'transactions':transactions})

class GoalCreateView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        form=GoalForm()
        return render(request,'finance/goal_form.html',{'form':form})
    # on submit post call
    def post(self,request ,*args,**kwargs):
        form = GoalForm(request.POST)
        if form.is_valid():
            goal=form.save(commit=False)
            goal.user= request.user
            goal.save()
            return redirect('dashboard')
        return render(request,'finance/goal_form.html',{'form':form})

def export_transactions(request):
    user_transactions= Transaction.objects.filter(user=request.user)
    transaction_resource = TransactionResource()
    dataset = transaction_resource.export(queryset=user_transactions)
    excel_data = dataset.export('xls')

    response = HttpResponse(excel_data,content_type='application/vnd.openxmlformats-officiedocument.spreadsheetml.sheet')

    response['Content-Disposition']='attachment; filename=transactions_report.xlsx'