<pre> 
jp-shopping-site/
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   └── k8s/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml  ← 指向 shop.wvwwcw.xyz
│
├── backend/
│   ├── app/              ← Flask + FastAPI 程式碼
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── Dockerfile
│   └── k8s/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml  ← api.wvwwcw.xyz
│
├── postgres/
│   ├── init.sql          ← 資料表建立語法
│   └── k8s/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── pvc.yaml
│       └── secret.yaml   ← 密碼儲存
│
└── README.md
</pre>
