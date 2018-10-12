import csv
from io import TextIOWrapper

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .permissions import SuperUserMixin
from .forms import ProjectForm
from .models import Document, Project, Label
import pandas as pd
import s3fs, boto3
from django.views.decorators.csrf import csrf_exempt

class IndexView(TemplateView):
    template_name = 'index.html'


class ProjectView(LoginRequiredMixin, TemplateView):

    def get_template_names(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return [project.get_template_name()]


class ProjectsView(LoginRequiredMixin, CreateView):
    form_class = ProjectForm
    template_name = 'projects.html'


class DatasetView(SuperUserMixin, LoginRequiredMixin, ListView):
    template_name = 'admin/dataset.html'
    paginate_by = 5

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return project.documents.all()


class LabelView(SuperUserMixin, LoginRequiredMixin, TemplateView):
    template_name = 'admin/label.html'


class StatsView(SuperUserMixin, LoginRequiredMixin, TemplateView):
    template_name = 'admin/stats.html'


class GuidelineView(SuperUserMixin, LoginRequiredMixin, TemplateView):
    template_name = 'admin/guideline.html'


class DataUpload(SuperUserMixin, LoginRequiredMixin, TemplateView):
    template_name = 'admin/dataset_upload.html'

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs.get('project_id'))
        try:
            #form_data = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            key_name = request.POST['key_name']
            if project.is_type_of(Project.SEQUENCE_LABELING):
                Document.objects.bulk_create([Document(
                    text=line.strip(),
                    project=project) for line in form_data])
            else:
                # get a handle on s3
                s3 = boto3.resource('s3')
                print(s3)

                # get a handle on the bucket that holds your file
                bucket = s3.Bucket('go-mmt-data-science')

                # get a handle on the object you want (i.e. your file)
                obj = bucket.Object(key='chat_bot/tool_data/{0}'.format(key_name))

                # get the object
                response = obj.get()
                # form_data = response['Body'].read().splitlines(True)
                # reader = csv.reader(form_data)
                df = pd.read_csv(response['Body'], header=None)
                print(df.shape)

                # create dataset from S3 file
                for (_, line) in df.iterrows():
                    doc = Document(id=line[0].strip(), text=line[1].strip(), project=project)
                    doc.save()
                    print([doc.doc_labels.create(text=label.strip(), shortcut=chr(ord('a') + idx), project=project) for
                           (idx, label) in enumerate(line[2:])])

                #for line in reader:
                #    doc = Document(id=line[0].strip(), text=line[1].strip(), project=project)
                #    doc.save()
                #    print([doc.doc_labels.create(text=label.strip(), shortcut=chr(ord('a') + idx), project=project) for
                #           (idx, label) in enumerate(line[2:])])

                # for line in reader:
                #     doc = Document(id=line[0].strip(), text=line[1].strip(), project=project)
                #     doc.save()
                #     l = []
                #     for (idx, label) in enumerate(line[2:]):
                #         l.append(Label(text=label.strip(), shortcut=chr(ord('a') + idx), project=project))
                #     doc.doc_labels.add(*l)
                # Document.objects.bulk_create([Document(
                #     text=line[0].strip(),
                #     project=project) for line in reader])
                # docs = []
                # for idx, row in df.iterrows():
                #     docs.append(Document(id=row[0].strip(), text=row[1].strip(), project=project))
                # Document.objects.bulk_create(docs)
                #
                # ThroughModel = Label.documents.through
                # through_models = []
                # for doc, idx, row in zip(docs, df.iterrows()):
                # for roster in TeamRoaster.objects.filter(team_id=team_id):
                #     lineup = Lineup.objects.filter(
                #         game_id=game_id, team_id=team_id, player=roster.player).first()
                #     for position in roster.position.all():
                #         through_models.append(
                #             ThroughModel(lineup_id=lineup.id, position_id=position.id))
                # ThroughModel.objects.bulk_create(through_models)

            return HttpResponseRedirect(reverse('dataset', args=[project.id]))
        except:
            return HttpResponseRedirect(reverse('upload', args=[project.id]))


class DataDownload(SuperUserMixin, LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, pk=project_id)
        docs = project.get_documents(is_null=False).distinct()
        filename = '_'.join(project.name.lower().split())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

        writer = csv.writer(response)
        for d in docs:
            writer.writerows(d.make_dataset())

        return response


class DemoTextClassification(TemplateView):
    template_name = 'demo/demo_text_classification.html'


class DemoNamedEntityRecognition(TemplateView):
    template_name = 'demo/demo_named_entity.html'


class DemoTranslation(TemplateView):
    template_name = 'demo/demo_translation.html'
