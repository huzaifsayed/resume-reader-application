from django.shortcuts import render
from django.views.generic.base import TemplateView
from .forms import ResumeForm
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.http import HttpResponseRedirect
from .models import Resume
import os
from docx import Document

from custom_resume_parser.resume_parser import CustomResumeParser

class ResumeUploadView(TemplateView):
    resume_form = ResumeForm
    template_name = "index.html"

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        resume_form = ResumeForm(post_data, file_data)

        if resume_form.is_valid():
            resume_obj = resume_form.save()

            data = CustomResumeParser.get_extracted_data('media/'+str(resume_obj.document))

            resume_obj.name = data.get('name') or 'Not Found'
            resume_obj.email = data.get('email') or 'Not Found'
            resume_obj.phone_number = data.get('mobile_number') or 'Not Found'
            resume_obj.linkedin_url = data.get('linkedin_url') or 'Not Found'
            resume_obj.skills = data.get('skills') or 'Not Found'
            resume_obj.education = data.get('education') or 'Not Found'
            resume_obj.total_char = data.get('doc_total_characters') or 'File Empty'
            resume_obj.total_lines = data.get('doc_total_lines') or 'File Empty'
            resume_obj.total_words = data.get('doc_total_words') or 'File Empty'
            
            # resume_obj.font_name = font_style
            # resume_obj.font_size = font_size[:2]
            # resume_obj.total_tables = total_tables
            # resume_obj.total_images = total_images

           


            resume_obj.save()
            
            return HttpResponseRedirect(reverse_lazy('resumedetail', kwargs={'pk': resume_obj.id}))

        context = self.get_context_data(
                                        resume_form=resume_form,
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)



class ResumeDetailView(DetailView):
    model = Resume
    template_name = "resumedetail.html"
    context_object_name = 'resume'

class ResumeListView(ListView):
    model = Resume
    template_name = "resumelist.html"
    context_object_name = 'resumes'
