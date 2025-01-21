# Guide de Contribution

## Introduction

Merci de contribuer à Content Creator AI ! Ce guide vous aidera à comprendre notre processus de contribution.

## Prérequis

- Python 3.8+
- Node.js 14+
- Git

## Installation

1. Forker le dépôt
2. Cloner votre fork
3. Exécuter `./scripts/setup.sh`

## Structure du Projet

```
content-creator-ai/
├── backend/           # Backend Python Flask
├── frontend/         # Frontend Vue.js
├── config/           # Fichiers de configuration
├── docs/            # Documentation
├── scripts/         # Scripts utilitaires
└── tests/           # Tests
```

## Guidelines de Code

- Suivre PEP 8 pour Python
- Utiliser ESLint pour JavaScript/Vue
- Écrire des tests pour les nouvelles fonctionnalités
- Documenter les nouvelles fonctionnalités

## Process de Pull Request

1. Créer une branche pour votre fonctionnalité
2. Écrire des tests
3. Mettre à jour la documentation
4. Soumettre une Pull Request

## Tests

```bash
./scripts/test.sh
```

## Documentation

- Mettre à jour la documentation API si nécessaire
- Ajouter des docstrings aux fonctions
- Documenter les changements dans le CHANGELOG
