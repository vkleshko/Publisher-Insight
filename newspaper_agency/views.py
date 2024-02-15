from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from newspaper_agency.forms import (
    TopicSearchForm,
    RedactorSearchForm,
    RedactorCreationForm,
    RedactorYearOfExperienceUpdateForm,
    NewspapersSearchForm,
    NewspaperForm
)

from newspaper_agency.models import Topic, Newspaper, Redactor


def index(request):
    topics = Topic.objects.count()
    newspapers = Newspaper.objects.count()
    redactors = Redactor.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_topics": topics,
        "num_newspapers": newspapers,
        "num_redactors": redactors,
        "num_visits": num_visits + 1,
    }

    return render(request, "newspaper_agency/index.html", context=context)


class TopicListView(generic.ListView):
    model = Topic
    context_object_name = "topic_list"
    template_name = "newspaper_agency/topic_list.html"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["topic_search"] = TopicSearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = Topic.objects.all()
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )
        return queryset


class TopicCreatedView(generic.CreateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper_agency:topic-list")


class TopicUpdateView(generic.UpdateView):
    model = Topic
    fields = "__all__"
    success_url = reverse_lazy("newspaper_agency:topic-list")


class TopicDeleteView(generic.DeleteView):
    model = Topic
    success_url = reverse_lazy("newspaper_agency:topic-list")


class RedactorListView(generic.ListView):
    model = Redactor
    context_object_name = "redactor_list"
    template_name = "newspaper_agency/redactor_list.html"
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RedactorListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["redactor_search_form"] = RedactorSearchForm(
            initial={"username": username}
        )

        return context

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        form = RedactorSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                username__icontains=form.cleaned_data["username"]
            )
        return queryset


class RedactorDetailView(generic.DeleteView):
    model = Redactor
    template_name = "newspaper_agency/redactor_detail.html"


class RedactorCreatedView(generic.CreateView):
    model = Redactor
    form_class = RedactorCreationForm


class RedactorYearOfExperienceUpdateView(generic.UpdateView):
    model = Redactor
    form_class = RedactorYearOfExperienceUpdateForm
    template_name = "newspaper_agency/redactor_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "newspaper_agency:redactor-detail", kwargs={"pk": self.object.id}
        )


class RedactorDeleteUpdateView(generic.DeleteView):
    model = Redactor
    success_url = reverse_lazy("newspaper_agency:redactor-list")


class NewspapersListView(generic.ListView):
    model = Newspaper
    template_name = "newspaper_agency/newspaper_list.html"
    context_object_name = "newspaper_list"
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewspapersListView, self).get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        context["newspapers_search_form"] = NewspapersSearchForm(
            initial={"title": title}
        )

        return context

    def get_queryset(self):
        queryset = Newspaper.objects.select_related("topic")
        form = NewspapersSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                title__icontains=form.cleaned_data["title"]
            )


class NewspapersDetailView(generic.DeleteView):
    model = Newspaper
    template_name = "newspaper_agency/newspapers_detail.html"


class NewspapersCreateView(generic.CreateView):
    model = Newspaper
    form_class = NewspaperForm
    template_name = "newspaper_agency/newspaper_form.html"
