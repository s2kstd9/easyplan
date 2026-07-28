import json
import hmac
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from werkzeug.security import check_password_hash, generate_password_hash

from django.db import models
from django.db.models import Q
from .models import User, Subject, Scope, Item, TimeTable, LearningPlanList, TimeTableList


def verify_password(stored_pw, input_pw):
    if not stored_pw or not input_pw:
        return False
    # Legacy 'sha256$salt$hash' format check
    if stored_pw.startswith('sha256$'):
        try:
            parts = stored_pw.split('$', 2)
            if len(parts) == 3:
                _, salt, hashval = parts
                calculated = hmac.new(salt.encode('utf-8'), input_pw.encode('utf-8'), 'sha256').hexdigest()
                return hmac.compare_digest(calculated, hashval)
        except Exception:
            return False
    try:
        return check_password_hash(stored_pw, input_pw)
    except Exception:
        pass
    try:
        return check_password(input_pw, stored_pw)
    except Exception:
        return False


def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Unauthorized'}, status=401)
            messages.error(request, '이 페이지를 보려면 로그인을 해야 합니다.')
            return redirect('login')
        request.current_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


def root(request):
    return redirect('home')


def home(request):
    user = get_current_user(request)
    return render(request, 'home.html', {'current_user': user})


def about(request):
    user = get_current_user(request)
    return render(request, 'about.html', {'current_user': user})


def login_view(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        userPW = request.POST.get('userPW')

        try:
            user = User.objects.get(userName=userName)
            if verify_password(user.userPW, userPW):
                if user.userPW.startswith('sha256$'):
                    user.userPW = generate_password_hash(userPW, method='pbkdf2:sha256')
                    user.save()
                request.session['user_id'] = user.id
                return redirect('select_learning_plan')
            else:
                messages.error(request, 'Invalid username or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        userPW = request.POST.get('userPW')
        userEmail = request.POST.get('userEmail')

        if User.objects.filter(userName=userName).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        if User.objects.filter(userEmail=userEmail).exists():
            messages.error(request, 'Email already registered')
            return redirect('signup')

        hashed_password = generate_password_hash(userPW, method='pbkdf2:sha256')
        user = User.objects.create(userName=userName, userPW=hashed_password, userEmail=userEmail)
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')


@login_required_custom
def select_learning_plan(request):
    user = request.current_user
    learning_plans = list(LearningPlanList.objects.filter(user=user))

    if not learning_plans:
        default_plan = LearningPlanList.objects.create(
            user=user,
            learningPlanName="첫번째 학습계획",
            tag=""
        )
        learning_plans = [default_plan]

    return render(request, 'select_learning_plan.html', {
        'learning_plans': learning_plans,
        'current_user': user
    })


@login_required_custom
def subjects_view(request):
    return render(request, 'subjects.html', {'current_user': request.current_user})


@login_required_custom
def timetable_view(request):
    return render(request, 'timetable.html', {'current_user': request.current_user})


@login_required_custom
def learning_plan_view(request):
    return render(request, 'learning_plan.html', {'current_user': request.current_user})


# REST API endpoints

@login_required_custom
def get_learning_plans(request):
    plans = LearningPlanList.objects.filter(user=request.current_user)
    return JsonResponse([{
        'id': plan.id,
        'learningPlanName': plan.learningPlanName,
        'tag': plan.tag or ''
    } for plan in plans], safe=False)


@login_required_custom
def get_time_table_lists(request, learning_plan_id):
    plan = get_object_or_404(LearningPlanList, id=learning_plan_id, user=request.current_user)
    time_table_lists = list(TimeTableList.objects.filter(Q(user=request.current_user) | Q(learning_plan=plan)))

    if not time_table_lists:
        default_time_table = TimeTableList.objects.create(
            timeTableName="첫번째 기준시간표",
            learning_plan=plan,
            user=request.current_user,
            tag=""
        )
        time_table_lists = [default_time_table]

    return JsonResponse([{
        'id': ttl.id,
        'timeTableName': ttl.timeTableName,
        'tag': ttl.tag or ''
    } for ttl in time_table_lists], safe=False)


@login_required_custom
def get_time_tables(request, time_table_list_id):
    time_table_list = get_object_or_404(TimeTableList, Q(id=time_table_list_id) & (Q(user=request.current_user) | Q(learning_plan__user=request.current_user)))
    time_tables = TimeTable.objects.filter(time_table_list=time_table_list)
    return JsonResponse([{
        'id': tt.id,
        'day': tt.day,
        'itemId': tt.item_id,
        'sTime': tt.sTime,
        'eTime': tt.eTime,
        'tag': tt.tag or ''
    } for tt in time_tables], safe=False)


@csrf_exempt
def api_subjects(request):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        subjects = Subject.objects.filter(Q(user=user) | Q(user__isnull=True))
        return JsonResponse([{'id': s.id, 'subjectName': s.subjectName, 'tag': s.tag or ''} for s in subjects], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject_name = data.get('subjectName')
            if not subject_name:
                return JsonResponse({'error': '과목명이 필요합니다'}, status=400)
            
            existing = Subject.objects.filter(Q(user=user) | Q(user__isnull=True), subjectName=subject_name).first()
            if existing:
                if existing.user is None:
                    existing.user = user
                    existing.save()
                    return JsonResponse({'message': '과목이 추가되었습니다', 'id': existing.id}, status=201)
                return JsonResponse({'error': '이미 존재하는 과목입니다'}, status=400)

            new_subject = Subject.objects.create(subjectName=subject_name, user=user)
            return JsonResponse({'message': '과목이 추가되었습니다', 'id': new_subject.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_subject_detail(request, subject_id):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    subject = get_object_or_404(Subject, Q(id=subject_id) & (Q(user=user) | Q(user__isnull=True)))

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            subject_name = data.get('subjectName')
            if not subject_name:
                return JsonResponse({'error': '과목명이 필요합니다'}, status=400)
            subject.subjectName = subject_name
            if subject.user is None:
                subject.user = user
            subject.save()
            return JsonResponse({'message': '과목이 수정되었습니다'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            items = Item.objects.filter(subject_id=subject_id)
            for item in items:
                TimeTable.objects.filter(item=item).delete()
                Scope.objects.filter(item=item).delete()
            Item.objects.filter(subject_id=subject_id).delete()
            subject.delete()
            return JsonResponse({'message': '과목이 삭제되었습니다'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def check_subject_usage(request, subject_id):
    try:
        items_count = Item.objects.filter(subject_id=subject_id).count()
        return JsonResponse({
            'isUsed': items_count > 0,
            'message': '이 과목은 이미 이전 학습계획에서 사용되고 있습니다. 이 과목을 삭제하면 이전 학습계획에서 해당 과목의 내용이 삭제됩니다. 그래도 삭제하시겠습니까?'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_items(request):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        items = Item.objects.filter(
            Q(subject__user=user) | Q(subject__user__isnull=True)
        ).select_related('subject').prefetch_related('scopes')
        result = []
        for i in items:
            result.append({
                'id': i.id,
                'itemName': i.itemName,
                'subId': i.subject_id,
                'subjectName': i.subject.subjectName,
                'scopes': [{
                    'id': s.id,
                    'begin': s.begin,
                    'end': s.end
                } for s in i.scopes.all()],
                'tag': i.tag or ''
            })
        return JsonResponse(result, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_name = data.get('itemName')
            sub_id = data.get('subId')
            
            if not item_name:
                return JsonResponse({'error': '학습항목명을 입력해주세요.'}, status=400)
            if not sub_id or not Subject.objects.filter(Q(id=sub_id) & (Q(user=user) | Q(user__isnull=True))).exists():
                return JsonResponse({'error': '유효한 과목을 선택해주세요.'}, status=400)

            new_item = Item.objects.create(
                itemName=item_name,
                subject_id=sub_id,
                tag=data.get('tag', '')
            )
            for scope_data in data.get('scopes', []):
                Scope.objects.create(
                    item=new_item,
                    begin=scope_data['begin'],
                    end=scope_data['end']
                )
            return JsonResponse({'success': True, 'id': new_item.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            item_name = data.get('itemName')
            sub_id = data.get('subId')

            if not item_name:
                return JsonResponse({'error': '학습항목명을 입력해주세요.'}, status=400)
            if not sub_id or not Subject.objects.filter(id=sub_id).exists():
                return JsonResponse({'error': '유효한 과목을 선택해주세요.'}, status=400)

            item.itemName = item_name
            item.subject_id = sub_id
            item.tag = data.get('tag', '')
            item.save()

            Scope.objects.filter(item=item).delete()
            for scope_data in data.get('scopes', []):
                Scope.objects.create(
                    item=item,
                    begin=scope_data['begin'],
                    end=scope_data['end']
                )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            TimeTable.objects.filter(item=item).delete()
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_scopes(request):
    if request.method == 'GET':
        scopes = Scope.objects.all()
        return JsonResponse([{
            'id': s.id,
            'begin': s.begin,
            'end': s.end,
            'tag': s.tag or ''
        } for s in scopes], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_scope = Scope.objects.create(
                item_id=data['itemId'],
                begin=int(data['begin']),
                end=int(data['end']),
                tag=data.get('tag', '')
            )
            return JsonResponse({
                'success': True,
                'id': new_scope.id,
                'begin': new_scope.begin,
                'end': new_scope.end,
                'tag': new_scope.tag or ''
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_scope_detail(request, scope_id):
    scope = get_object_or_404(Scope, id=scope_id)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            scope.begin = int(data['begin'])
            scope.end = int(data['end'])
            scope.tag = data.get('tag', '')
            scope.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            scope.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_timetable(request):
    if request.method == 'GET':
        timeTableListId = request.GET.get('timeTableListId')
        if not timeTableListId:
            return JsonResponse({'success': False, 'error': '시간표 ID가 필요합니다'}, status=400)

        user = get_current_user(request)
        if not user:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        time_table_list = get_object_or_404(TimeTableList, Q(id=timeTableListId) & (Q(user=user) | Q(learning_plan__user=user)))
        plans = TimeTable.objects.filter(time_table_list=time_table_list)
        return JsonResponse([{
            'id': p.id,
            'day': p.day,
            'itemId': p.item_id,
            'sTime': p.sTime,
            'eTime': p.eTime,
            'tag': p.tag or ''
        } for p in plans], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            timeTableListId = data[0].get('timeTableListId') if data else None

            if not timeTableListId:
                return JsonResponse({'success': False, 'error': '시간표 ID가 필요합니다'}, status=400)

            user = get_current_user(request)
            if not user:
                return JsonResponse({'error': 'Unauthorized'}, status=401)

            time_table_list = get_object_or_404(TimeTableList, Q(id=timeTableListId) & (Q(user=user) | Q(learning_plan__user=user)))
            TimeTable.objects.filter(time_table_list=time_table_list).delete()

            for plan in data:
                TimeTable.objects.create(
                    day=plan['day'],
                    item_id=plan['itemId'],
                    sTime=plan['sTime'],
                    eTime=plan['eTime'],
                    tag=plan.get('tag', ''),
                    time_table_list=time_table_list
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def catch_all_html(request, path):
    try:
        user = get_current_user(request)
        return render(request, f'{path}.html', {'current_user': user})
    except Exception:
        return render(request, '404.html', status=404)
