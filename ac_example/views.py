from django.http import HttpResponse
from django.shortcuts import render_to_response

from ac_example.forms import InsertMessage

def example(request):
    if request.method == 'POST':
        form = InsertMessage(request.POST)
        if form.is_valid():
            return HttpResponse("yo!")
    else:
        form = InsertMessage()

    return render_to_response("autocomplete.html", {'form':form})
