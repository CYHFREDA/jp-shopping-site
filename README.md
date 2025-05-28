<pre> 
jp-shopping-site/
├── README.md
├── backend
│   ├── Dockerfile
│   ├── app              ← FastAPI 程式碼
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── body.json
│   ├── deploy_backend.sh
│   └── k8s
│       ├── deployment.yaml
│       ├── ingress.yaml     ← 指向 api.wvwwcw.xyz
│       └── service.yaml
├── clean_dockerhub_old_images.sh
├── cloudflared-deployment.yaml
├── frontend
│   ├── Dockerfile
│   ├── deploy_frontend.sh
│   ├── html
│   ├── k8s
│   │   ├── deployment.yaml
│   │   ├── ingress.yaml     ← 指向 shop.wvwwcw.xyz
│   │   └── service.yaml
│   └── nginx
└── postgres
    ├── init.sql   ← 資料表建立語法
    └── k8s
        ├── deployment.yaml
        ├── pvc.yaml
        ├── secret.yaml
        └── service.yaml ← 密碼儲存
</pre>
