from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http.response import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from leads.models import Category, Lead, Agent
from .forms import CategoryForm, LeadForm, AgentForm
from utils.pagination import make_pagination_range
import pandas


class LeadView(LoginRequiredMixin, generic.View):
    login_url = "accounts:login"
    form = LeadForm
    template_name = 'dashboard/pages/leads.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        leads = Lead.objects.all().order_by('-id')
        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(leads, per_page=10)
        page_obj = paginator.get_page(current_page)
        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )
        context = {
            'form': form,
            'leads': page_obj,
            'pagination_range': pagination_range
        }

        return render(request, self.template_name, context=context)

    def post(self, request):
        form = self.form(request.POST)
        url = reverse_lazy('dashboard:leads')

        if form.is_valid():
            form.save()
            messages.success(request, 'Lead created successfully')
            return redirect(url)
        else:
            messages.error(request, 'Lead not created successfully')
            return redirect(url)


class LeadSearchView(LeadView):
    login_url = "accounts:login"
    form = LeadForm
    template_name = 'dashboard/pages/leads.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        search_term = self.request.GET.get('q', '').strip()
        leads = Lead.objects.filter(
            Q(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(age__icontains=search_term) |
                Q(category__name__icontains=search_term) |
                Q(agent__first_name__icontains=search_term),
            )
        ).order_by('-id')

        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(leads, per_page=10)
        page_obj = paginator.get_page(current_page)

        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )

        if not search_term:
            raise Http404()

        context = {
            'form': form,
            'leads': page_obj,
            'pagination_range': pagination_range,
            'search_term': search_term,
            'additional_url_query': f'&q={search_term}',
        }

        return render(request, self.template_name, context=context)


class LeadUpdateView(LoginRequiredMixin, generic.UpdateView):  # noqa
    login_url = "accounts:login"
    model = Lead
    form = LeadForm
    fields = [
        "first_name",
        "last_name",
        "email",
        "age",
        "category",
        "agent",
    ]
    template_name = 'dashboard/partials/lead/lead_table_update_modal.html'  # noqa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, pk):
        lead = Lead.objects.get(id=pk)
        form = LeadForm(instance=lead)
        form = self.form(request.POST, instance=lead)
        url = reverse_lazy('dashboard:leads')

        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully')
            return redirect(url)

        messages.error(request, 'Lead not updated successfully')
        return redirect(url)


class LeadDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):  # noqa
    login_url = "accounts:login"
    template_name = 'dashboard/partials/lead/lead_table_delete_modal.html'  # noqa
    success_message = 'Lead deleted successfully'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        _id = int(self.kwargs.get('pk'))
        lead = get_object_or_404(Lead, pk=_id)
        return lead

    def get_success_url(self):
        return reverse_lazy('dashboard:leads')


class LeadExportView(LoginRequiredMixin, SuccessMessageMixin, generic.View):  # noqa
    login_url = "accounts:login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        leads = Lead.objects.all().order_by('-id')
        data = []

        for lead in leads:
            data.append({
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "age": lead.age,
                "category": lead.category,
                "agent": lead.agent
            })

        response = HttpResponse(content_type='application/xlsx')
        response['Content-Disposition'] = f'attachment; filename="Leads.xlsx"'
        
        with pandas.ExcelWriter(response) as writer:
            pandas.DataFrame(data).to_excel(writer, sheet_name='Leads')    
            
        messages.success(request, 'Leads export successfully')

        return response


class CategoryView(LoginRequiredMixin, generic.View):
    login_url = "accounts:login"
    form = CategoryForm
    template_name = 'dashboard/pages/leads_category.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        categories = Category.objects.all().order_by('-id')
        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(categories, per_page=10)
        page_obj = paginator.get_page(current_page)
        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )
        context = {
            'form': form,
            'categories': page_obj,
            'pagination_range': pagination_range
        }

        return render(request, self.template_name, context=context)

    def post(self, request):
        form = self.form(request.POST)
        url = reverse_lazy('dashboard:leads_category')

        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully')
            return redirect(url)
        else:
            messages.error(request, 'Category not created successfully')
            return redirect(url)


class CategorySearchView(CategoryView):
    login_url = "accounts:login"
    form = CategoryForm
    template_name = 'dashboard/pages/leads_category.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        search_term = self.request.GET.get('q', '').strip()
        categories = Category.objects.filter(
            Q(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term),
            )
        ).order_by('-id')

        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(categories, per_page=10)
        page_obj = paginator.get_page(current_page)

        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )

        if not search_term:
            raise Http404()

        context = {
            'form': form,
            'categories': page_obj,
            'pagination_range': pagination_range,
            'search_term': search_term,
            'additional_url_query': f'&q={search_term}',
        }

        return render(request, self.template_name, context=context)


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):  # noqa
    login_url = "accounts:login"
    model = Category
    form = CategoryForm
    fields = ["name", "description"]
    template_name = 'dashboard/partials/category/category_table_update_modal.html'  # noqa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, pk):
        category = Category.objects.get(id=pk)
        form = CategoryForm(instance=category)
        form = self.form(request.POST, instance=category)
        url = reverse_lazy('dashboard:leads_category')

        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully')
            return redirect(url)

        messages.error(request, 'Category not updated successfully')
        return redirect(url)


class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):  # noqa
    login_url = "accounts:login"
    template_name = 'dashboard/partials/category/category_table_delete_modal.html'  # noqa
    success_message = 'Category deleted successfully'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        _id = int(self.kwargs.get('pk'))
        category = get_object_or_404(Category, pk=_id)
        return category

    def get_success_url(self):
        return reverse_lazy('dashboard:leads_category')


class CategoryExportView(LoginRequiredMixin, SuccessMessageMixin, generic.View):  # noqa
    login_url = "accounts:login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        categories = Category.objects.all().order_by('-id')
        data = []

        for category in categories:
            data.append({
                'name': category.name,
                'description': category.description
            })

        response = HttpResponse(content_type='application/xlsx')
        response['Content-Disposition'] = f'attachment; filename="Categories.xlsx"'
        
        with pandas.ExcelWriter(response) as writer:
            pandas.DataFrame(data).to_excel(writer, sheet_name='Categories')    
            
        messages.success(request, 'Categories export successfully')

        return response


class AgentView(LoginRequiredMixin, generic.View):
    login_url = "accounts:login"
    form = AgentForm
    template_name = 'dashboard/pages/leads_agent.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        agents = Agent.objects.all().order_by('-id')
        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(agents, per_page=10)
        page_obj = paginator.get_page(current_page)
        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )
        context = {
            'form': form,
            'agents': page_obj,
            'pagination_range': pagination_range
        }

        return render(request, self.template_name, context=context)

    def post(self, request):
        form = self.form(request.POST)
        url = reverse_lazy('dashboard:leads_agent')

        if form.is_valid():
            form.save()
            messages.success(request, 'Agent created successfully')
            return redirect(url)
        else:
            messages.error(request, 'Agent not created successfully')
            return redirect(url)


class AgentSearchView(AgentView):
    login_url = "accounts:login"
    form = AgentForm
    template_name = 'dashboard/pages/leads_agent.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = self.form()
        search_term = self.request.GET.get('q', '').strip()
        categories = Agent.objects.filter(
            Q(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone_number__icontains=search_term),
            )
        ).order_by('-id')

        current_page = int(request.GET.get('page', 1))
        paginator = Paginator(categories, per_page=10)
        page_obj = paginator.get_page(current_page)

        pagination_range = make_pagination_range(
            page_range=paginator.page_range,
            qty_pages=4,
            current_page=current_page,
        )

        if not search_term:
            raise Http404()

        context = {
            'form': form,
            'agents': page_obj,
            'pagination_range': pagination_range,
            'search_term': search_term,
            'additional_url_query': f'&q={search_term}',
        }

        return render(request, self.template_name, context=context)


class AgentDeleteView(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):  # noqa
    login_url = "accounts:login"
    template_name = 'dashboard/partials/agent/agent_table_delete_modal.html'  # noqa
    success_message = 'Agent deleted successfully'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        _id = int(self.kwargs.get('pk'))
        agent = get_object_or_404(Agent, pk=_id)
        return agent

    def get_success_url(self):
        return reverse_lazy('dashboard:leads_agent')


class AgentUpdateView(LoginRequiredMixin, generic.UpdateView):  # noqa
    login_url = "accounts:login"
    model = Agent
    form = AgentForm
    fields = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
    ]
    template_name = 'dashboard/partials/agent/agent_table_update_modal.html'  # noqa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, pk):
        agent = Agent.objects.get(id=pk)
        base_form = AgentForm(instance=agent)
        update_form = self.form(request.POST)
        url = reverse_lazy('dashboard:leads_agent')

        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Agent updated successfully')
            return redirect(url)

        messages.error(request, 'Agent not updated successfully')
        return redirect(url)


class AgentExportView(LoginRequiredMixin, SuccessMessageMixin, generic.View):  # noqa
    login_url = "accounts:login"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        return super().setup(*args, **kwargs)

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        agents = Agent.objects.all().order_by('-id')
        data = []

        for agent in agents:
            data.append({
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "email": agent.email,
                "phone_number": agent.phone_number,
            })

        response = HttpResponse(content_type='application/xlsx')
        response['Content-Disposition'] = f'attachment; filename="Agents.xlsx"'
        
        with pandas.ExcelWriter(response) as writer:
            pandas.DataFrame(data).to_excel(writer, sheet_name='Agents')    
            
        messages.success(request, 'Agents export successfully')

        return response
