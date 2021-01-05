from django.shortcuts import redirect, render


def home(request):
    if request.user.is_authenticated:
        if request.user.is_patient:
            return redirect('patient:index')
        elif request.user.is_wellwisher:
            return redirect('wellwisher:index')
        elif request.user.is_receptionist:
            return redirect('receptionist:index')
        elif request.user.is_moderator:
            return redirect('moderator:index')
        else:
            return redirect('doctor:index')
    return render(request, 'dep/index.html')
