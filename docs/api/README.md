# API Documentation

## Introduction

Cette documentation détaille les endpoints API disponibles dans Content Creator AI.

## Authentication

Toutes les requêtes API doivent inclure un token JWT dans l'en-tête Authorization :

```
Authorization: Bearer <votre-token>
```

## Endpoints

### YouTube

#### GET /api/youtube/analytics
Récupère les analyses pour une chaîne YouTube.

#### POST /api/youtube/download/video
Télécharge une vidéo YouTube avec options avancées.

### TikTok

#### GET /api/tiktok/analytics
Récupère les analyses pour un compte TikTok.

### Instagram

#### GET /api/instagram/analytics
Récupère les analyses pour un compte Instagram.

### Facebook

#### GET /api/facebook/analytics
Récupère les analyses pour une page Facebook.

## Modèles de Données

### Vidéo
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "url": "string",
  "thumbnail": "string",
  "statistics": {
    "views": "number",
    "likes": "number",
    "comments": "number"
  }
}
```

## Codes d'Erreur

- 400: Requête invalide
- 401: Non authentifié
- 403: Non autorisé
- 404: Ressource non trouvée
- 500: Erreur serveur
