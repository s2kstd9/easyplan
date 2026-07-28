from django.urls import path
from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('home.html', views.home),
    path('about', views.about, name='about'),
    path('about.html', views.about),
    path('login', views.login_view, name='login'),
    path('signup', views.signup_view, name='signup'),
    path('logout', views.logout_view, name='logout'),
    path('select_learning_plan', views.select_learning_plan, name='select_learning_plan'),
    path('subjects', views.subjects_view, name='subjects'),
    path('timetable', views.timetable_view, name='timetable'),
    path('learning_plan', views.learning_plan_view, name='learning_plan'),

    # API endpoints
    path('api/learning_plans', views.get_learning_plans, name='get_learning_plans'),
    path('api/time_table_lists/<int:learning_plan_id>', views.get_time_table_lists, name='get_time_table_lists'),
    path('api/time_tables/<int:time_table_list_id>', views.get_time_tables, name='get_time_tables'),
    path('api/subjects', views.api_subjects, name='api_subjects'),
    path('api/subjects/<int:subject_id>', views.api_subject_detail, name='api_subject_detail'),
    path('api/subjects/<int:subject_id>/check_usage', views.check_subject_usage, name='check_subject_usage'),
    path('api/items', views.api_items, name='api_items'),
    path('api/items/<int:item_id>', views.api_item_detail, name='api_item_detail'),
    path('api/scopes', views.api_scopes, name='api_scopes'),
    path('api/scopes/<int:scope_id>', views.api_scope_detail, name='api_scope_detail'),
    path('api/timetable', views.api_timetable, name='api_timetable'),

    # Catch-all HTML route
    path('<str:path>.html', views.catch_all_html),
]
