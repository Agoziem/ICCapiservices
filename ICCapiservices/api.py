from ninja_extra import NinjaExtraAPI

from blog.routes.blogsroutes import BlogsController
from blog.routes.categoriesroutes import CategoriesController
from blog.routes.commentsroutes import CommentsController
from blog.routes.likesroutes import LikesController
from authentication.routes import (
    AuthenticationController,
    PasswordResetController,
    EmailVerificationController,
)
from CBTpractice.routes.tests import (
    YearsController,
    TestTypesController,
    TestsController,
)
from CBTpractice.routes.subjects import (
    SubjectsController,
    QuestionsController,
    AnswersController,
)
from CBTpractice.routes.practice import PracticeController, ComputingController
from customers.routes.customers import CustomersController
from emails.routes.emails import (
    EmailsController,
    EmailResponsesController,
    EmailMessagesController,
)
from ICCapp.routes.organizations import OrganizationsController
from ICCapp.routes.staff import StaffController
from ICCapp.routes.testimonials import TestimonialsController
from ICCapp.routes.subscriptions import SubscriptionsController
from ICCapp.routes.departments import (
    DepartmentsController,
    DepartmentServicesController,
)
from notifications.routes.notifications import NotificationsController
from payments.routes.payments import PaymentsController
from products.routes.products import ProductsController
from products.routes.categories import (
    CategoriesController as ProductCategoriesController,
    SubCategoriesController,
)
from services.routes.services import ServicesController, ServiceUserController
from services.routes.categories import (
    ServiceCategoriesController,
    ServiceSubCategoriesController,
)
from vidoes.routes.videos import VideosController, VideoUserController
from vidoes.routes.categories import (
    VideoCategoriesController,
    VideoSubCategoriesController,
)
from whatsappAPI.routes.whatsapp import (
    WhatsAppController,
    WhatsAppTemplateController,
    WhatsAppMediaController,
    WhatsAppWebhookController as WhatsAppWebhookEventsController,
)
from whatsappAPI.routes.webhook import WhatsAppWebhookController
from ninja_jwt.controller import NinjaJWTDefaultController


# Create the ninja API instance for authentication
ninja_api = NinjaExtraAPI(
    title="ICC API", version="1.0.0", description="ICC APP API endpoints"
)

# Register the controllers
ninja_api.register_controllers(
    # Authentication
    AuthenticationController,
    PasswordResetController,
    EmailVerificationController,
    # Blog
    BlogsController,
    CategoriesController,
    CommentsController,
    LikesController,
    # CBT Practice
    YearsController,
    TestTypesController,
    TestsController,
    SubjectsController,
    QuestionsController,
    AnswersController,
    PracticeController,
    ComputingController,
    # Customers
    CustomersController,
    # Emails
    EmailsController,
    EmailResponsesController,
    EmailMessagesController,
    # ICCapp (Core Organization)
    OrganizationsController,
    StaffController,
    TestimonialsController,
    SubscriptionsController,
    DepartmentsController,
    DepartmentServicesController,
    # Notifications
    NotificationsController,
    # Payments
    PaymentsController,
    # Products
    ProductsController,
    ProductCategoriesController,
    SubCategoriesController,
    # Services
    ServicesController,
    ServiceUserController,
    ServiceCategoriesController,
    ServiceSubCategoriesController,
    # Videos
    VideosController,
    VideoUserController,
    VideoCategoriesController,
    VideoSubCategoriesController,
    # WhatsApp API
    WhatsAppController,
    WhatsAppTemplateController,
    WhatsAppMediaController,
    WhatsAppWebhookEventsController,
    WhatsAppWebhookController,
    # AuthTokens
    NinjaJWTDefaultController,
)
