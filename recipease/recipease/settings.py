"""
Django settings for recipease project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Setup environment variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()


# Put the .env file in the same folder location as this file

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")

DATABASE_URL = env("DATABASE_URL")
DATABASE_NAME = env("DATABASE_NAME")
USER_NAME = env("USER_NAME")
USER_PASSWORD = env("USER_PASSWORD")

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'engine',
    'bootstrap5',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'recipease.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'recipease.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Unused, but left in for future reference if local databases ever wanted to be used

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------- SQL ------------------------------- #

# SQL statements for creating database tables

CREATE_TABLES = (
    "CREATE TABLE User (email VARCHAR(32), first_name VARCHAR(32), last_name VARCHAR(32), "
    "PRIMARY KEY (email));"

    "CREATE TABLE Recipe (recipeID INT AUTO_INCREMENT, email VARCHAR(32), title VARCHAR(32), description VARCHAR(64), "
    "cook_time INT, instructions VARCHAR(512), date_created TIMESTAMP NOT NULL DEFAULT NOW(), "
    "PRIMARY KEY (recipeID), FOREIGN KEY (email) REFERENCES User(email));"

    "CREATE TABLE Ingredient (ingredientID INT AUTO_INCREMENT, name VARCHAR(32), food_type VARCHAR(32), "
    "PRIMARY KEY (ingredientID));"

    "CREATE TABLE Recipe_Ingredients (recipeID INT, ingredientID INT, amount INT, "
    "PRIMARY KEY (recipeID, ingredientID), FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID), "
    "FOREIGN KEY (ingredientID) REFERENCES Ingredient(ingredientID));"

    "CREATE TABLE Rates (recipeID INT, email VARCHAR(32), value INT, "
    "PRIMARY KEY (email, recipeID), FOREIGN KEY (email) REFERENCES User(email), "
    "FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID));"

    "CREATE TABLE Comment (recipeID INT, commentID INT, content VARCHAR(128), email VARCHAR(32), "
    "PRIMARY KEY (recipeID, commentID), FOREIGN KEY (email) REFERENCES User(email), "
    "FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID));"

    "CREATE TABLE Category (categoryID INT AUTO_INCREMENT, name VARCHAR(32), "
    "PRIMARY KEY (categoryID));"

    "CREATE TABLE Belongs_To (recipeID INT, categoryID INT, "
    "PRIMARY KEY (recipeID, categoryID), FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID), "
    "FOREIGN KEY (categoryID) REFERENCES Category(categoryID));"

    "CREATE TABLE Favorite (email VARCHAR(32), recipeID INT, "
    "PRIMARY KEY (email, recipeID), FOREIGN KEY (email) REFERENCES User(email), "
    "FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID));"

    "CREATE TABLE Nutrition (recipeID INT, "
    "calories INT, fat INT, satfat INT, carbs INT, fiber INT, sugar INT, protein INT, "
    "PRIMARY KEY(recipeID), FOREIGN KEY (recipeID) REFERENCES Recipe(recipeID));"
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

SITE_ID = 2

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'