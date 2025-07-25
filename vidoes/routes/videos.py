from typing import Optional
from ninja_extra import api_controller, route, paginate
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.pagination import LimitOffsetPagination
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.http import Http404
from collections import Counter

from ..models import Video, Category, SubCategory, Organization
from ..schemas import (
    VideoSchema, VideoListResponseSchema,
    CreateVideoSchema, UpdateVideoSchema, VideoFileUploadSchema,
    SuccessResponseSchema, ErrorResponseSchema,
    VideoUserDetailsSchema, VideoUserListResponseSchema
)
from utils import normalize_img_field, parse_json_fields


class VideoPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'page_size'
    max_limit = 1000


@api_controller('/videos', tags=['Videos'])
class VideosController:
    
    @route.get('/{organization_id}', response=list[VideoSchema])
    @paginate(VideoPagination)
    def get_videos(self, organization_id: int, category: Optional[str] = None):
        """Get all videos for a specific organization, with optional category filtering"""
        queryset = Video.objects.filter(organization=organization_id).select_related(
            'organization', 'category', 'subcategory'
        ).order_by('-updated_at')
        
        if category and category != "All":
            try:
                video_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=video_category)
            except Category.DoesNotExist:
                pass
        
        # Convert to schema using the custom method
        videos = []
        for video in queryset:
            videos.append(VideoSchema.from_django_model(video))
        
        return videos
    
    @route.get('/trending/{organization_id}', response=list[VideoSchema])
    @paginate(VideoPagination)
    def get_trending_videos(self, organization_id: int, category: Optional[str] = None):
        """Get trending videos for a specific organization, sorted by number of watchers"""
        queryset = Video.objects.filter(organization=organization_id).select_related(
            'organization', 'category', 'subcategory'
        ).annotate(
            watchers_count=Count('userIDs_that_bought_this_video')
        ).filter(
            watchers_count__gt=0
        ).order_by('-watchers_count', '-updated_at')
        
        if category and category != "All":
            try:
                video_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=video_category)
            except Category.DoesNotExist:
                pass
        
        # Convert to schema using the custom method
        videos = []
        for video in queryset:
            videos.append(VideoSchema.from_django_model(video))
        
        return videos
    
    @route.get('/user/{organization_id}/{user_id}', response=list[VideoSchema])
    @paginate(VideoPagination)
    def get_user_videos(self, organization_id: int, user_id: int, category: Optional[str] = None):
        """Get videos purchased by a specific user in an organization"""
        queryset = Video.objects.filter(
            organization=organization_id,
            userIDs_that_bought_this_video__id=user_id
        ).select_related('organization', 'category', 'subcategory').order_by('-updated_at')
        
        if category and category != "All":
            try:
                video_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=video_category)
            except Category.DoesNotExist:
                pass
        
        # Convert to schema using the custom method
        videos = []
        for video in queryset:
            videos.append(VideoSchema.from_django_model(video))
        
        return videos
    
    @route.get('/free/{organization_id}', response=list[VideoSchema])
    @paginate(VideoPagination)
    def get_free_videos(self, organization_id: int, category: Optional[str] = None):
        """Get all free videos for a specific organization"""
        queryset = Video.objects.filter(
            organization=organization_id, 
            free=True
        ).select_related('organization', 'category', 'subcategory').order_by('-updated_at')
        
        if category and category != "All":
            try:
                video_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=video_category)
            except Category.DoesNotExist:
                pass
        
        # Convert to schema using the custom method
        videos = []
        for video in queryset:
            videos.append(VideoSchema.from_django_model(video))
        
        return videos
    
    @route.get('/paid/{organization_id}', response=list[VideoSchema])
    @paginate(VideoPagination)
    def get_paid_videos(self, organization_id: int, category: Optional[str] = None):
        """Get all paid videos for a specific organization"""
        queryset = Video.objects.filter(
            organization=organization_id, 
            free=False
        ).select_related('organization', 'category', 'subcategory').order_by('-updated_at')
        
        if category and category != "All":
            try:
                video_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=video_category)
            except Category.DoesNotExist:
                pass
        
        # Convert to schema using the custom method
        videos = []
        for video in queryset:
            videos.append(VideoSchema.from_django_model(video))
        
        return videos
    
    @route.get('/video/{video_id}', response=VideoSchema)
    def get_video(self, video_id: int):
        """Get details of a specific video by ID"""
        video = get_object_or_404(
            Video.objects.select_related('organization', 'category', 'subcategory'),
            id=video_id
        )
        return VideoSchema.from_django_model(video)
    
    @route.get('/token/{video_token}', response=VideoSchema)
    def get_video_by_token(self, video_token: str):
        """Get details of a specific video by token"""
        video = get_object_or_404(
            Video.objects.select_related('organization', 'category', 'subcategory'),
            video_token=video_token
        )
        return VideoSchema.from_django_model(video)
    
    @route.post('/{organization_id}', response=VideoSchema, permissions=[IsAuthenticated])
    def create_video(self, organization_id: int, payload: CreateVideoSchema, file_data: VideoFileUploadSchema):
        """Create a new video for an organization"""
        try:
            # Get organization
            organization = get_object_or_404(Organization, id=organization_id)
            
            # Create video data
            video_data = payload.model_dump()
            video_data['organization'] = organization
            
            # Handle category
            if video_data.get('category'):
                category = get_object_or_404(Category, id=video_data.pop('category'))
                video_data['category'] = category
            
            # Handle subcategory
            if video_data.get('subcategory'):
                subcategory = get_object_or_404(SubCategory, id=video_data.pop('subcategory'))
                video_data['subcategory'] = subcategory
            
            # Remove organization ID from video_data since we're using the object
            video_data.pop('organization', None)
            
            # Create video
            video = Video.objects.create(
                organization=organization,
                **video_data
            )
            
            # Handle file uploads if provided
            if file_data:
                if file_data.thumbnail:
                    video.thumbnail = file_data.thumbnail # type: ignore
                if file_data.video:
                    video.video = file_data.video # type: ignore
                video.save()
            
            return VideoSchema.from_django_model(video)
            
        except Exception as e:
            return {"error": str(e)}
    
    @route.put('/video/{video_id}', response=VideoSchema, permissions=[IsAuthenticated])
    def update_video(self, video_id: int, payload: UpdateVideoSchema, file_data: VideoFileUploadSchema):
        """Update an existing video"""
        video = get_object_or_404(Video, id=video_id)
        
        try:
            # Update video fields
            video_data = payload.model_dump(exclude_unset=True)
            
            # Handle organization
            if 'organization' in video_data:
                organization = get_object_or_404(Organization, id=video_data.pop('organization'))
                video.organization = organization
            
            # Handle category
            if 'category' in video_data:
                if video_data['category']:
                    category = get_object_or_404(Category, id=video_data.pop('category'))
                    video.category = category
                else:
                    video.category = None
                    video_data.pop('category')
            
            # Handle subcategory
            if 'subcategory' in video_data:
                if video_data['subcategory']:
                    subcategory = get_object_or_404(SubCategory, id=video_data.pop('subcategory'))
                    video.subcategory = subcategory
                else:
                    video.subcategory = None
                    video_data.pop('subcategory')
            
            # Update remaining fields
            for attr, value in video_data.items():
                setattr(video, attr, value)
            
            # Handle file uploads if provided
            if file_data:
                if file_data.thumbnail:
                    video.thumbnail = file_data.thumbnail # type: ignore
                if file_data.video:
                    video.video = file_data.video # type: ignore
            
            video.save()
            return VideoSchema.from_django_model(video)
            
        except Exception as e:
            return {"error": str(e)}
    
    @route.delete('/video/{video_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_video(self, video_id: int):
        """Delete a video"""
        video = get_object_or_404(Video, id=video_id)
        video.delete()
        return {"message": "Video deleted successfully"}


@api_controller('/video-users', tags=['Video User Management'])
class VideoUserController:
    
    @route.get('/watchers/{video_id}', response=list[VideoUserDetailsSchema])
    @paginate(VideoPagination)
    def get_users_that_bought_video(self, video_id: int):
        """Get all users that have purchased/watched a specific video"""
        video = get_object_or_404(Video, id=video_id)
        users = video.userIDs_that_bought_this_video.all()
        
        # Prepare user data with count
        user_data = []
        for user, count in Counter(users).items():
            from utils import get_full_image_url
            user_data.append(VideoUserDetailsSchema(
                id=user.id,
                username=user.username,
                email=user.email,
                avatar_url=get_full_image_url(user.avatar),
                user_count=count,
                date_joined=user.date_joined
            ))
        
        return user_data
