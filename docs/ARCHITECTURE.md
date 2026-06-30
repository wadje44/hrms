# Architecture

Prabha HRMS is a full-stack HRMS: a React SPA talking to a FastAPI backend over a
JWT-authenticated REST API, backed by PostgreSQL, deployed to AWS with Terraform and
shipped by GitHub Actions.

> **Context:** the original `Prabha_HRMS_Client_Requirements.docx` asked for a single-file
> Firebase app. This project keeps the *domain requirements* from that doc but implements
> them as a proper full stack for end-to-end learning.

---

## 1. System overview

```mermaid
flowchart LR
  user([Employee / Manager / Admin])

  subgraph client[Browser]
    spa["React SPA<br/>(Vite + TypeScript)"]
  end

  subgraph aws[AWS]
    cf[CloudFront]
    s3[(S3 static site)]
    alb[Application Load Balancer]
    subgraph ecs[ECS Fargate]
      api["FastAPI<br/>app.main:app"]
    end
    rds[(PostgreSQL<br/>RDS)]
    sm[[Secrets Manager]]
    logs[(CloudWatch Logs)]
  end

  user --> cf --> s3
  user -->|"REST + JWT"| alb --> api
  api --> rds
  api -. reads at boot .-> sm
  api --> logs
  spa -. static assets .- cf
  spa -->|"/api/v1/*"| alb
```

- The **SPA** is served as static files from S3 via CloudFront.
- The **API** runs as containers on ECS Fargate behind an ALB, in private subnets.
- **Secrets** (DB URL, JWT signing key) are injected from Secrets Manager at task start.
- The browser holds a **JWT** and sends it on every API call.

---

## 2. Request authentication flow

```mermaid
sequenceDiagram
  actor U as User
  participant W as React SPA
  participant A as FastAPI
  participant DB as PostgreSQL

  U->>W: pick name + enter 4-digit PIN
  W->>A: POST /api/v1/auth/login {employee_id, pin}
  A->>DB: load employee
  A->>A: bcrypt.verify(pin, pin_hash)
  A-->>W: { access_token (JWT), role }
  W->>W: store token (localStorage)
  Note over W,A: subsequent requests
  W->>A: GET /api/v1/... (Authorization: Bearer JWT)
  A->>A: decode JWT → employee_id + role
  A->>A: role guard (admin / manager / employee)
  A-->>W: data (or 401/403)
```

Roles come from the employee record, not the token issuer. Guards live in
`apps/api/app/core/deps.py` (`require_admin`, `require_manager`).

---

## 3. GPS punch decision (doc §7, §9)

The category-aware rules are a pure function — `apps/api/app/services/gps.py::evaluate_punch`.

```mermaid
flowchart TD
  start([Punch In]) --> capture[Capture GPS + Haversine distance]
  capture --> free{Free-punch employee?}
  free -- yes --> ok[Allow · field session]
  free -- no --> cat{Category?}
  cat -- Field/Service --> okf[Allow · location captured, not validated]
  cat -- Office/Hybrid --> gps{GPS available?}
  gps -- no --> block[Block: GPS required]
  gps -- yes --> within{Within radius?}
  within -- yes --> oko[Allow · office session]
  within -- no --> hybrid{Hybrid?}
  hybrid -- no --> blockd["Block: show distance<br/>'You are Nm from office'"]
  hybrid -- yes --> wfh{WFH limit reached?}
  wfh -- yes --> blockw[Block: WFH limit reached]
  wfh -- no --> okw[Allow · tagged WFH]
```

---

## 4. Payroll calculation (doc §11)

`apps/api/app/services/payroll.py::compute_payslip` — pure, fully unit-tested.

```mermaid
flowchart LR
  A[Attendance for month] --> agg[Aggregate:<br/>worked hrs, present, late marks,<br/>paid-leave days, UL days, absences]
  agg --> rate{Hourly rate}
  rate -->|override| r1[per-employee-month override]
  rate -->|else| r2[employee hourly_rate]
  rate -->|else| r3[monthly_salary ÷ standard hrs]
  r1 & r2 & r3 --> ph[paid_hours = worked + paid-leave hrs − late deductions]
  ph --> net["Net = rate × paid_hours<br/>+ fixed components − deductions"]
```

Absences and unpaid leave contribute zero worked hours, so they reduce pay pro-rata
naturally; paid leave is credited as a normal working day; late marks beyond the free
allowance deduct one hour each.

---

## 5. Data model

```mermaid
erDiagram
  EMPLOYEE ||--o{ ATTENDANCE_DAY : has
  ATTENDANCE_DAY ||--o{ ATTENDANCE_SESSION : contains
  EMPLOYEE ||--o{ LEAVE_REQUEST : submits
  EMPLOYEE ||--o{ LEAVE_BALANCE : has
  EMPLOYEE ||--o{ PAYROLL_RECORD : earns
  EMPLOYEE ||--o{ HOURLY_RATE_OVERRIDE : may_have

  EMPLOYEE {
    string id PK "EMP008"
    string full_name
    string category "office|hybrid|field|service"
    string role "admin|manager|employee"
    numeric monthly_salary
    int wfh_limit
    bool free_punch
    string pin_hash
  }
  ATTENDANCE_DAY {
    int id PK
    string employee_id FK
    date date
    string status "present|absent|leave|holiday|half_day"
    string leave_type
    numeric total_hours
    bool is_wfh
    bool is_late
  }
  ATTENDANCE_SESSION {
    int id PK
    int day_id FK
    datetime punch_in
    datetime punch_out
    float lat
    float lng
    string type
  }
  LEAVE_REQUEST {
    int id PK
    string employee_id FK
    date date_from
    date date_to
    string leave_type
    string status "pending|approved|rejected"
  }
  LEAVE_BALANCE {
    int id PK
    string employee_id FK
    string leave_type
    int balance
  }
  PAYROLL_RECORD {
    int id PK
    string month "YYYY-MM"
    string employee_id FK
    numeric net
    json breakdown
  }
  HOURLY_RATE_OVERRIDE {
    int id PK
    string month
    string employee_id FK
    numeric hourly_rate
  }
```

App-level settings (office coords, radius, late cutoff, working hours, holidays) live in a
singleton `app_settings` row.

---

## 6. AWS infrastructure (Terraform)

```mermaid
flowchart TB
  subgraph vpc[VPC 10.0.0.0/16]
    subgraph public[Public subnets · 2 AZ]
      albn[ALB]
      nat[NAT Gateway]
    end
    subgraph private[Private subnets · 2 AZ]
      task[ECS Fargate tasks]
      db[(RDS PostgreSQL)]
    end
  end
  igw[Internet Gateway]
  ecr[(ECR)]
  sm[[Secrets Manager]]
  cw[(CloudWatch Logs)]
  cfn[CloudFront] --> s3[(S3 SPA bucket)]

  internet([Internet]) --> igw --> albn --> task
  task --> db
  task -->|pull image| ecr
  task -->|egress| nat --> igw
  task -. secrets .-> sm
  task -. logs .-> cw
  internet --> cfn
```

Modules in `infra/modules/`: `network`, `ecr`, `rds`, `alb`, `ecs`, `secrets`, `frontend`,
`iam_oidc`. Composed per environment in `infra/envs/{dev,prod}`. The app security group is
created in the composition (not the ECS module) to break the ECS↔RDS dependency cycle.

---

## 7. CI/CD pipeline (GitHub Actions)

```mermaid
flowchart LR
  pr([Pull Request]) --> ci[CI: lint · test · build · tf-validate]
  merge([Merge to main]) --> deploy
  subgraph deploy[Deploy · OIDC to AWS]
    direction TB
    img[Build & push image → ECR] --> taskdef[Register task def]
    taskdef --> mig[Run migrations<br/>one-off Fargate task]
    mig --> roll[Update ECS service → wait stable]
    web[Build SPA → S3 sync] --> inval[CloudFront invalidation]
  end
  merge --> tf[Terraform plan → gated apply]
```

CI authenticates to AWS via **GitHub OIDC** (no long-lived keys). See
[`DEPLOYMENT.md`](DEPLOYMENT.md) for the required repository variables.

---

## 8. Monorepo layout

```mermaid
flowchart TD
  root["hrms/"] --> apps
  root --> infra
  root --> gha[".github/workflows/"]
  root --> docs
  apps --> api["apps/api · FastAPI"]
  apps --> web["apps/web · React+Vite"]
  api --> svc["app/services · domain rules (pure, tested)"]
  api --> rtr["app/api/v1 · routers"]
  api --> mdl["app/models · SQLAlchemy + Alembic"]
  infra --> mods["modules/ · reusable TF"]
  infra --> envs["envs/{dev,prod}"]
```
