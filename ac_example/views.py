from django.http import HttpResponse
from django.shortcuts import render_to_response

from ac_example.forms import ExampleForm

def example(request):
    valid = False
    if request.GET:
        form = ExampleForm(request.GET)
        if form.is_valid():
            valid = True
    else:
        form = ExampleForm()

    return render_to_response("autocomplete.html", {'form':form,'valid':valid})
