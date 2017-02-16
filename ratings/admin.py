from django.contrib import admin

# class LectureForm(forms.ModelForm):
#     class Meta:
#         model = Lecture
#
#         def clean(self):
#             start_date = self.cleaned_data.get('start_date')
#             end_date = self.cleaned_data.get('end_date')
#             if start_date > end_date:
#                 raise forms.ValidationError("Dates are fucked up")
#         return self.cleaned_data
