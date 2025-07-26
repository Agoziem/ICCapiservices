from typing import List, Optional
from ninja import Query
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from ninja_jwt.authentication import JWTAuth

from ..models import Year, TestType, Test, Subject, Question, TestResult
from ..schemas import (
    YearSchema,
    YearListResponseSchema,
    CreateYearSchema,
    UpdateYearSchema,
    TestTypeSchema,
    TestTypeListResponseSchema,
    CreateTestTypeSchema,
    UpdateTestTypeSchema,
    TestSchema,
    TestListResponseSchema,
    TestSummarySchema,
    CreateTestSchema,
    UpdateTestSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)

User = get_user_model()


@api_controller("/years", tags=["CBT Years"])
class YearsController:

    @route.get("/", response=List[YearSchema])
    def list_years(self):
        """Get all available years"""
        years = Year.objects.all()
        return years

    @route.post("/", response=YearSchema, auth=JWTAuth())
    def create_year(self, payload: CreateYearSchema):
        """Create a new year"""
        year = Year.objects.create(**payload.dict())
        return year

    @route.get("/{year_id}", response=YearSchema)
    def get_year(self, year_id: int):
        """Get a specific year"""
        year = get_object_or_404(Year, id=year_id)
        return year

    @route.put("/{year_id}", response=YearSchema, auth=JWTAuth())
    def update_year(self, year_id: int, payload: UpdateYearSchema):
        """Update a year"""
        year = get_object_or_404(Year, id=year_id)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(year, attr, value)
        year.save()
        return year

    @route.delete(
        "/{year_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_year(self, year_id: int):
        """Delete a year"""
        year = get_object_or_404(Year, id=year_id)
        year.delete()
        return {"message": "Year deleted successfully"}


@api_controller("/test-types", tags=["CBT Test Types"])
class TestTypesController:

    @route.get("/", response=List[TestTypeSchema])
    def list_test_types(self):
        """Get all test types"""
        test_types = TestType.objects.all()
        return test_types

    @route.post("/", response=TestTypeSchema, auth=JWTAuth())
    def create_test_type(self, payload: CreateTestTypeSchema):
        """Create a new test type"""
        test_type = TestType.objects.create(**payload.dict())
        return test_type

    @route.get("/{test_type_id}", response=TestTypeSchema)
    def get_test_type(self, test_type_id: int):
        """Get a specific test type"""
        test_type = get_object_or_404(TestType, id=test_type_id)
        return test_type

    @route.put(
        "/{test_type_id}", response=TestTypeSchema, auth=JWTAuth()
    )
    def update_test_type(self, test_type_id: int, payload: UpdateTestTypeSchema):
        """Update a test type"""
        test_type = get_object_or_404(TestType, id=test_type_id)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(test_type, attr, value)
        test_type.save()
        return test_type

    @route.delete(
        "/{test_type_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_test_type(self, test_type_id: int):
        """Delete a test type"""
        test_type = get_object_or_404(TestType, id=test_type_id)
        test_type.delete()
        return {"message": "Test type deleted successfully"}


@api_controller("/tests", tags=["CBT Tests"])
class TestsController:

    @route.get("/", response=List[TestSchema])
    def list_tests(
        self, year_id: Optional[int] = None, test_type_id: Optional[int] = None
    ):
        """Get all tests with optional filtering"""
        tests = Test.objects.select_related("testYear", "texttype").prefetch_related(
            "testSubject"
        )

        if year_id:
            tests = tests.filter(testYear_id=year_id)
        if test_type_id:
            tests = tests.filter(texttype_id=test_type_id)

        return tests

    @route.post("/", response=TestSchema, auth=JWTAuth())
    def create_test(self, payload: CreateTestSchema):
        """Create a new test"""
        test_data = payload.dict()
        subjects = test_data.pop("testSubject", [])

        test = Test.objects.create(**test_data)
        if subjects:
            test.testSubject.set(subjects)

        return test

    @route.get("/{test_id}", response=TestSchema)
    def get_test(self, test_id: int):
        """Get a specific test with all details"""
        test = get_object_or_404(
            Test.objects.select_related("testYear", "texttype").prefetch_related(
                "testSubject__questions__answers"
            ),
            id=test_id,
        )
        return test

    @route.put("/{test_id}", response=TestSchema, auth=JWTAuth())
    def update_test(self, test_id: int, payload: UpdateTestSchema):
        """Update a test"""
        test = get_object_or_404(Test, id=test_id)
        test_data = payload.dict(exclude_unset=True)

        if "testSubject" in test_data:
            subjects = test_data.pop("testSubject")
            test.testSubject.set(subjects)

        for attr, value in test_data.items():
            setattr(test, attr, value)
        test.save()

        return test

    @route.delete(
        "/{test_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_test(self, test_id: int):
        """Delete a test"""
        test = get_object_or_404(Test, id=test_id)
        test.delete()
        return {"message": "Test deleted successfully"}

    @route.get("/{test_id}/summary", response=TestSummarySchema)
    def get_test_summary(self, test_id: int):
        """Get test summary without full details"""
        test = get_object_or_404(
            Test.objects.select_related("testYear", "texttype").annotate(
                subjects_count=Count("testSubject")
            ),
            id=test_id,
        )
        return test
