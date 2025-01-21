# Guide de Déploiement

## Prérequis

- Serveur Linux (Ubuntu 20.04+ recommandé)
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Redis
- Nginx

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/your-username/content-creator-ai.git
cd content-creator-ai
```

2. Configurer l'environnement :
```bash
./scripts/setup.sh
```

3. Configurer Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. Configurer les services systemd :
```bash
sudo cp deployment/content-creator-ai.service /etc/systemd/system/
sudo cp deployment/celery.service /etc/systemd/system/
sudo systemctl daemon-reload
```

5. Démarrer les services :
```bash
sudo systemctl start content-creator-ai
sudo systemctl start celery
sudo systemctl start nginx
```

## Mise à jour

Pour mettre à jour l'application :
```bash
./scripts/deploy.sh
```

## Surveillance

- Utiliser Prometheus pour la surveillance
- Configurer Grafana pour les tableaux de bord
- Mettre en place des alertes avec AlertManager

## Sauvegarde

Les sauvegardes sont automatiquement créées dans `/var/www/backups`

## Dépannage

1. Vérifier les logs :
```bash
journalctl -u content-creator-ai
journalctl -u celery
```

2. Vérifier l'état des services :
```bash
systemctl status content-creator-ai
systemctl status celery
systemctl status nginx
```
