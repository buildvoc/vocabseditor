import csv, time, codecs
from django import forms
from django.contrib import admin
from django.forms.widgets import ClearableFileInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from .models import *
from guardian.admin import GuardedModelAdmin
from reversion.admin import VersionAdmin
from mptt.admin import MPTTModelAdmin

class TSVImportForm(forms.Form):
    tsv_files = forms.FileField(widget=ClearableFileInput(attrs={
		'multiple': True
	}))

# With object permissions support
@admin.register(SkosConcept)
class SkosConceptAdmin(MPTTModelAdmin, GuardedModelAdmin, VersionAdmin):
	list_filter = ('is_trained',)
	change_list_template = "vocabs/skosconcept_changelist.html"


class SkosCollectionAdmin(GuardedModelAdmin, VersionAdmin):
	pass


class SkosConceptSchemeAdmin(GuardedModelAdmin, VersionAdmin):
	pass

class ConceptNoteAdmin(GuardedModelAdmin, VersionAdmin):
	search_fields = ('name',)
	list_filter = ('concept__scheme', 'concept__needs_review', 'concept__collection')
	change_list_template = "vocabs/conceptnotes_changelist.html"
	def get_urls(self):
		urls = super().get_urls()
		new_urls = [
			path('import-tsv/', self.import_as_tsv),
		]
		return new_urls + urls

	def export_as_tsv(self, request, queryset):
		response = HttpResponse(content_type='text/csv')
		response ['Content-Disposition'] = f'attachment; filename=export-{time.time()}.tsv'
		writer = csv.writer(response, delimiter='\t')

		for obj in queryset:
			writer.writerow([obj.name, f'<{obj.concept.related}>'])
		return response
		
	def import_as_tsv(self, request):	
		if request.method == 'POST':
			tsv_files = request.FILES.getlist('tsv_files')
			for tsv_file in tsv_files:
				pref_label = tsv_file.name
				reader = csv.reader(codecs.iterdecode(tsv_file, 'utf-8'), delimiter='\t')
				for row in reader:
					name = row[0]
					root_user = User.objects.get(username='root')
					scheme_35 = SkosConceptScheme.objects.get(id=35)
					concept = SkosConcept(pref_label=pref_label, scheme=scheme_35, created_by=root_user)
					concept.save()
					concept_note = ConceptNote(concept_id=concept.id, name=name, language='en')
					concept_note.save()
			self.message_user(request, "TSV file has been imported")
			return redirect('/admin/vocabs/conceptnote')
		form = TSVImportForm()
		payload = {
			"form": form
		}
		return render(request, "vocabs/tsv_form.html", payload)
	
	
	actions = ['export_as_tsv']


#admin.site.register(SkosConcept, SkosConceptAdmin)
admin.site.register(SkosCollection, SkosCollectionAdmin)
admin.site.register(SkosConceptScheme, SkosConceptSchemeAdmin)
admin.site.register(ConceptSchemeTitle)
admin.site.register(ConceptSchemeDescription)
admin.site.register(ConceptSchemeSource)
admin.site.register(CollectionLabel)
admin.site.register(CollectionNote)
admin.site.register(CollectionSource)
admin.site.register(ConceptLabel)
admin.site.register(ConceptNote, ConceptNoteAdmin)
admin.site.register(ConceptSource)