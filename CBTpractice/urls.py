from views.computingviews import *
from views.practiceviews import *
from views.subjectviews import *
from views.testtypeviews import *
from views.yearviews import *
from django.urls import path

urlpatterns = [
    path('years/', get_years),
    path('year/<int:year_id>/', get_year),
    path('addyear/', add_year),
    path('updateyear/<int:year_id>/', update_year),
    path('deleteyear/<int:year_id>/', delete_year),

    path('subjects/', get_subjects),
    path('subject/<int:subject_id>/', get_subject),
    path('addsubject/', add_subject),
    path('updatesubject/<int:subject_id>/', update_subject),
    path('deletesubject/<int:subject_id>/', delete_subject),

    path('testtypes/', get_testtypes),
    path('testtype/<int:testtype_id>/', get_testtype),
    path('addtesttype/', add_testtype),
    path('updatetesttype/<int:testtype_id>/', update_testtype),
    path('deletetesttype/<int:testtype_id>/', delete_testtype),

    path('tests/<int:organization_id>/', get_tests),
    path('test/<int:test_id>/', get_test),
    path('addtest/<int:organization_id>/', add_test),
    path('updatetest/<int:test_id>/', update_test),
    path('deletetest/<int:test_id>/', delete_test),
    path('testresult/<int:organization_id>/', get_test_results),

    path('practicetest/<int:organization_id>/', get_student_tests),
    path('submittest/<int:organization_id>/', submit_student_test),
]
