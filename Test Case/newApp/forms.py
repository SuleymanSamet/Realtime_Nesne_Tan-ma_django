from django import forms


class ObjectRecognitionForm(forms.Form):
    language = forms.CharField(label='Dil Seçimi', max_length=100)
    object_translation = forms.CharField(label='Nesnenin Karşılığı', max_length=100)


class CeviriForm(forms.Form):
    METIN = forms.CharField(label='Çevrilecek Metin', max_length=100)
    DIL = forms.ChoiceField(choices=[('en', 'İngilizce'), ('fr', 'Fransızca'), ('de', 'Almanca')])