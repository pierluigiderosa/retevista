from django import forms

CHARACTER_ENCODINGS = [("ascii", "ASCII"),
                       ("latin1", "Latin-1"),
                       ("utf8",
                        "UTF-8")]
EPSG_LIST = [
    ("3004","Gauss Boaga Est"),
             ("4326","Gradi WGS84"),
             ]
tipologia_choices = [
        ('vincoli', 'vincoli'),
        ('catastale', 'catastale'),
    ]

class ImportShapefileForm(forms.Form):
    import_file = forms.FileField(label="Seleziona uno Shapefile zippato")
    character_encoding = forms.ChoiceField(choices=CHARACTER_ENCODINGS, initial="utf8")
    epsg = forms.ChoiceField(choices=EPSG_LIST,initial="4326",label='Sistema di riferimento')
    tipologia = forms.ChoiceField(choices=tipologia_choices,initial="vincoli",label='Tipologia del dato vettoriale')