from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.http import HttpResponse


@login_required
def image_create(request):
    # if request.method == 'POST':
    #     form = ImageCreateForm(data=request.POST)
    #     if form.is_valid():
    #         cd = form.cleaned_data
    #         new_item = form.save(commit=False)
    #         new_item.user = request.user
    #         new_item.save()
    #         messages.success(request, 'Image added')
    #         return redirect(new_item.get_absolute_url())
    # else:
    #     form = ImageCreateForm(data=request.GET)
    # return render(request, 'images/image/create.html', {'section': 'images', 'form': form})
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные формы действительны
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # назначить текущего пользователя элементу
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')
            # перенаправить на внов созданны объект детального представления
            return redirect(new_item.get_absolute_url())
    else:
        # создать форму с данными, предоставленными букмарклетом через GET
        form = ImageCreateForm(data=request.GET)
    return render(request,
                  'images/image/create.html',
                  {'section': 'images', 'form': form})


def detail(request):
    return HttpResponse('Added!')