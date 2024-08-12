from django.contrib import admin
from django.urls import path
from users.views import userRegistration, userAuthTokenLogin, userLogout, passwordResetRequest, passwordResetCodeCheck, passwordResetConfirm, myDetails
from category.views import create_category, update_category, delete_category, list_categories
from equipment.views import create_equipment, update_equipment, delete_equipment, list_equipment
from wallets.views import myTransactionLog, viewWallet, addFunds
from events.views import list_all_events, list_my_events, create_event, update_event, cancel_event


urlpatterns = [
    path('admin/', admin.site.urls),

    #User Management APIs:
    path('api/register/', userRegistration, name='register'),
    path('api/login/', userAuthTokenLogin, name='login'),
    path('api/logout/', userLogout, name='logout'),
    path('api/password-reset-request/', passwordResetRequest, name='password_reset_request'),
    path('api/password-reset-code-check/', passwordResetCodeCheck, name='password_reset_code_check'),
    path('api/password-reset-confirm/', passwordResetConfirm, name='password_reset_confirm'),
    path('api/my-profile/', myDetails, name='my_profile'),

    #Category Management APIs:
    path('api/categories/create/', create_category, name='create_category'),
    path('api/categories/update/<int:pk>/', update_category, name='update_category'),
    path('api/categories/delete/<int:pk>/', delete_category, name='delete_category'),
    path('api/categories/list/', list_categories, name='list_categories'),

    #Equipment Management APIs:
    path('api/equipment/create/', create_equipment, name='create_equipment'),
    path('api/equipment/update/<int:pk>/', update_equipment, name='update_equipment'),
    path('api/equipment/delete/<int:pk>/', delete_equipment, name='delete_equipment'),
    path('api/equipment/list/', list_equipment, name='list_equipment'),    

    #Events APIs:
    path('api/events/create/', create_event, name='create_event'),
    path('api/events/update/<int:pk>/', update_event, name='update_event'),
    path('api/events/cancel/<int:pk>/', cancel_event, name='cancel_event'),
    path('api/events/list/', list_all_events, name='list_all_events'),
    path('api/events/my-events/', list_my_events, name='list_my_events'),

    #Wallet APIs:
    path('api/wallets/my-wallet/', viewWallet, name='viewWallet'),
    path('api/wallets/add-funds/', addFunds, name='addFunds'),
    path('api/wallets/my-transactions/', myTransactionLog, name='myTransactions'),


]
