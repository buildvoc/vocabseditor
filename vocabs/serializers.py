from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class SkosLabelSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = SkosLabel
        fields = '__all__'


class SkosConceptSchemeSerializer(serializers.HyperlinkedModelSerializer):
    has_concepts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    created_by = serializers.CharField(read_only=True)
    curator = serializers.StringRelatedField(many=True)

    class Meta:
        model = SkosConceptScheme
        fields = '__all__'


class SkosCollectionSerializer(serializers.HyperlinkedModelSerializer):
    has_members = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = SkosCollection
        fields = '__all__'


class SkosConceptSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = SkosConcept
        fields = (
            'id', 'url',
            'pref_label', 'pref_label_lang',
            'collection',
            'scheme',
            'definition', 'definition_lang',
            'other_label',
            'notation', 'top_concept',
            'broader_concept', 'narrower_concepts',
            'same_as_external',
            'source_description',
            'skos_broader', 'broader', 'skos_narrower', 'narrower',
            'skos_related', 'related',
            'skos_broadmatch', 'narrowmatch', 'skos_narrowmatch', 'broadmatch',
            'skos_exactmatch', 'exactmatch', 'skos_closematch', 'closematch',
            'legacy_id',
            'skos_note', 'skos_note_lang', 'skos_scopenote', 'skos_scopenote_lang',
            'skos_changenote', 'skos_editorialnote', 'skos_example',
            'skos_historynote', 'dc_creator',
            'date_created', 'date_modified',
            'created_by',
        )
