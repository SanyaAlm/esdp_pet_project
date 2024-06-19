from django.contrib.auth import views, login, get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from accounts.forms import RegisterForm, LoginForm, UserUpdateForm, PasswordChangeForm, AccountRegisterForm
from accounts.models import User, Account
from shop.models import Shop
import redis
from django.http import HttpResponse, HttpResponseRedirect


class LoginView(views.LoginView):
    template_name = 'main.html'
    form_class = LoginForm

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        user = form.get_user()

        self.request.session['user_id'] = user.id
        self.request.session['phone'] = user.phone

        if user.phone_verification and user is not None:
            login(self.request, user)

            return redirect(self.get_success_url())

        return redirect('sms-verification')


class LoginPageView(views.LoginView):
    template_name = 'login.html'
    form_class = LoginForm

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        user = form.get_user()

        self.request.session['user_id'] = user.id
        self.request.session['phone'] = user.phone

        if user.phone_verification and user is not None:
            login(self.request, user)

            return redirect(self.get_success_url())

        return redirect('sms-verification')


class Logout(views.LogoutView):
    def get_next_page(self):
        return self.request.META.get('HTTP_REFERER')


class RegisterView(CreateView):
    template_name = 'register.html'
    model = User
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        user.is_staff = True

        self.request.session['user_id'] = user.id
        self.request.session['phone'] = user.phone

        return redirect('sms-verification')

    def form_invalid(self, form):
        return render(self.request, 'register.html', {'form': form})


class Sms_Verification(TemplateView):
    template_name = 'sms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone_number = self.request.session.get('phone')
        user_id = self.request.session.get('user_id')
        context['user_id'] = user_id
        context['phone_number'] = f'+{phone_number}'
        return context

    def post(self, request, *args, **kwargs):
        code_1 = request.POST.get('code_1')
        code_2 = request.POST.get('code_2')
        code_3 = request.POST.get('code_3')
        code_4 = request.POST.get('code_4')

        input_code = f"{code_1}{code_2}{code_3}{code_4}"
        redis_client = redis.StrictRedis(host='redis', port=6379, db=1)

        phone_number = self.request.session.get('phone')

        if input_code == redis_client.get(phone_number).decode('utf-8'):
            user_id = self.request.session.get('user_id')
            current_user = User.objects.get(id=user_id)

            current_user.phone_verification = True
            current_user.save()

            login(self.request, current_user)

            return redirect('home')

        return HttpResponse(f'Error {phone_number} ')


class UserUpdate(UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'update-user.html'
    pk_url_kwarg = 'id'
    context_object_name = 'user'

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'id': self.request.user.id})


class PasswordChangeView(UpdateView):
    model = get_user_model()
    template_name = 'change-password.html'
    form_class = PasswordChangeForm
    context_object_name = 'user'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse('login_page')


class AccountLoginView(views.LoginView):
    model = Account
    template_name = 'account-login.html'
    authentication_form = LoginForm

    def dispatch(self, request, *args, **kwargs):
        self.shop = Shop.objects.get(id=self.kwargs['shop_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        try:
            account = Account.objects.get(user__email=email, shops__in=[self.shop])
        except Account.DoesNotExist:
            return render(self.request, self.template_name, {'form': form, 'shop': self.shop})
        login(self.request, account.user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('shop_view', kwargs={'shop_id': self.shop.id})


class AccountRegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'account-register.html'

    def dispatch(self, request, *args, **kwargs):
        self.shop = Shop.objects.get(id=self.kwargs['shop_id'])
        self.account_form = AccountRegisterForm()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['account_form'] = self.account_form
        return context

    def post(self, request, *args, **kwargs):
        if self.get_form().is_valid() and AccountRegisterForm(request.POST).is_valid():
            return self.form_valid(self.get_form())

        return render(self.request, self.template_name,
                      {'form': self.get_form(), 'shop': self.shop, 'account_form': self.account_form})

    def form_valid(self, form):
        email = self.request.POST.get('email')

        try:
            Account.objects.get(user__email=email).exists()
            account = Account.objects.get(user__email=email)
            account.shops.add(self.shop)
        except Account.DoesNotExist:
            account = AccountRegisterForm(self.request.POST).save(commit=False)
            user = form.save(commit=False)
            user.save()
            account.user = user
            account.save()
            account.shops.add(self.shop)

            login(self.request, account.user)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('shop_view', kwargs={'shop_id': self.shop.id})
