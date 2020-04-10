from django.shortcuts import render
from django.views.generic.base import TemplateView
from .forms import ResumeForm
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.http import HttpResponseRedirect
from .models import Resume
import os

from custom_resume_parser.resume_parser import CustomResumeParser
from custom_resume_parser.resume_docx import get_font_table_shape_from_docx
from custom_resume_parser.resume_pdf import get_font_table_shape_from_pdf

class ResumeUploadView(TemplateView):
    resume_form = ResumeForm
    template_name = "index.html"

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        resume_form = ResumeForm(post_data, file_data)

        if resume_form.is_valid():
            resume_obj = resume_form.save()

            file_path = 'media/'+str(resume_obj.document)

            data = CustomResumeParser.get_extracted_data(file_path)

            resume_obj.name = data.get('name') or 'Not Found'
            resume_obj.email = data.get('email') or 'Not Found'
            resume_obj.phone_number = data.get('mobile_number') or 'Not Found'
            resume_obj.linkedin_url = data.get('linkedin_url') or 'Not Found'
            resume_obj.skills = data.get('skills') or 'Not Found'
            resume_obj.education = data.get('education') or 'Not Found'
            resume_obj.total_char = data.get('doc_total_characters') or 'File Empty'
            resume_obj.total_lines = data.get('doc_total_lines') or 'File Empty'
            resume_obj.total_words = data.get('doc_total_words') or 'File Empty'

            file_name, file_extension = os.path.splitext(file_path)

            if file_extension == '.docx':

                docx_data = get_font_table_shape_from_docx(file_path)
            
                resume_obj.font_name = docx_data.get('font_style') or 'File Empty'
                resume_obj.font_size = docx_data.get('font_size')[:2] 
                resume_obj.total_tables = docx_data.get('doc_table') 
                resume_obj.total_images = docx_data.get('doc_shapes') 
            
            elif file_extension == '.pdf':
                pdf_data = get_font_table_shape_from_pdf(file_path)

                resume_obj.font_name = pdf_data.get('font_style') or 'File Empty'
                resume_obj.font_size = '12, 24, 30'
                resume_obj.total_tables = 0
                resume_obj.total_images = pdf_data.get('doc_shapes') 
            
            resume_obj.save()
            
            return HttpResponseRedirect(reverse_lazy('resumedetail', kwargs={'pk': resume_obj.id}))

        context = self.get_context_data(resume_form=resume_form,)

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






