from django.http import HttpResponse

def healthz(_request):
    # Sadece 200 dönen hafif bir cevap; DB'ye, template'e, modele dokunmaz.
    return HttpResponse("ok", content_type="text/plain")
