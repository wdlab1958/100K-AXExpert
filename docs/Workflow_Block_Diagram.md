# AI Consulting Assistant Platform - 워크플로우 블록 다이어그램
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

**문서 버전**: 1.1  
**작성일**: 2025년 12월 11일  
**Update Date**: Dec. 16, 2025
**Editor**: Brian Lee / WDLAB AI/ML/AX Group

---

## 목차

1. [전체 시스템 아키텍처](#1-전체-시스템-아키텍처)
2. [메인 컨설팅 워크플로우](#2-메인-컨설팅-워크플로우)
3. [5단계 컨설팅 프레임워크 상세](#3-5단계-컨설팅-프레임워크-상세)
4. [에이전트 오케스트레이션 플로우](#4-에이전트-오케스트레이션-플로우)
5. [데이터 처리 및 분석 플로우](#5-데이터-처리-및-분석-플로우)
6. [시나리오 분석 워크플로우](#6-시나리오-분석-워크플로우)
7. [인간-AI 협업 워크플로우](#7-인간-ai-협업-워크플로우)
8. [보고서 생성 플로우](#8-보고서-생성-플로우)
9. [API 요청 흐름](#9-api-요청-흐름)

---

## 1. 전체 시스템 아키텍처

```mermaid
flowchart TB
    subgraph Client["🖥️ 클라이언트 계층"]
        UI[웹 대시보드<br/>HTML5/JS/CSS]
        API_DOC[API 문서<br/>Swagger/ReDoc]
    end

    subgraph Server["⚙️ 서버 계층"]
        FastAPI[FastAPI Server<br/>:8000]
        Router[API Router]
        Middleware[Middleware<br/>CORS/Audit]
    end

    subgraph Agents["🤖 멀티 에이전트 계층"]
        Orchestrator[Agent Orchestrator<br/>LangGraph]
        Strategy[Strategy Analyst<br/>Agent]
        Designer[Use Case Designer<br/>Agent]
        ROI[ROI Analyst<br/>Agent]
        Risk[Risk Assessor<br/>Agent]
        Report[Report Generator<br/>Agent]
    end

    subgraph LLM["🧠 LLM 계층"]
        Provider[LLM Provider]
        Ollama[Ollama Local<br/>llama3.1:8b]
        Online[Online LLM<br/>Claude/GPT]
    end

    subgraph Data["💾 데이터 계층"]
        Projects[(프로젝트 데이터)]
        AuditLogs[(감사 로그)]
        Reports_DB[(보고서 저장소)]
    end

    UI --> FastAPI
    API_DOC --> FastAPI
    FastAPI --> Middleware
    Middleware --> Router
    Router --> Orchestrator
    
    Orchestrator --> Strategy
    Orchestrator --> Designer
    Orchestrator --> ROI
    Orchestrator --> Risk
    Orchestrator --> Report
    
    Strategy --> Provider
    Designer --> Provider
    ROI --> Provider
    Risk --> Provider
    Report --> Provider
    
    Provider --> Ollama
    Provider -.-> Online
    
    Orchestrator --> Projects
    Middleware --> AuditLogs
    Report --> Reports_DB

    style Client fill:#e1f5fe
    style Server fill:#fff3e0
    style Agents fill:#f3e5f5
    style LLM fill:#e8f5e9
    style Data fill:#fce4ec
```

---

## 2. 메인 컨설팅 워크플로우

```mermaid
flowchart TD
    Start([🚀 컨설팅 시작])
    
    subgraph Init["1️⃣ 프로젝트 초기화"]
        Create[프로젝트 생성]
        Input[기업 정보 입력<br/>35개 필드]
        Validate[데이터 검증]
    end
    
    subgraph Stage1["2️⃣ Stage 1: AI 전략 수립"]
        Maturity[AI 성숙도 진단]
        Opportunity[기회 발굴]
        Roadmap[로드맵 수립]
    end
    
    subgraph Stage2["3️⃣ Stage 2: Use Case 설계"]
        Requirements[요건 정의]
        Architecture[아키텍처 설계]
        Governance[거버넌스 수립]
    end
    
    subgraph Analysis["4️⃣ 시나리오 분석"]
        Generate[3가지 시나리오 생성<br/>보수적/균형/적극적]
        ROI_Calc[ROI 분석]
        Risk_Assess[리스크 평가]
        Score[종합 점수 계산]
    end
    
    subgraph Review["5️⃣ 검토 및 승인"]
        Present[시나리오 제시]
        Feedback{피드백<br/>수신?}
        Modify[시나리오 수정]
        Approve{승인?}
    end
    
    subgraph Output["6️⃣ 산출물 생성"]
        ExecSummary[Executive Summary]
        FullReport[전체 컨설팅 보고서]
        Artifacts[산출물 패키지]
    end
    
    End([✅ 컨설팅 완료])
    
    Start --> Create
    Create --> Input
    Input --> Validate
    Validate --> Maturity
    
    Maturity --> Opportunity
    Opportunity --> Roadmap
    Roadmap --> Requirements
    
    Requirements --> Architecture
    Architecture --> Governance
    Governance --> Generate
    
    Generate --> ROI_Calc
    ROI_Calc --> Risk_Assess
    Risk_Assess --> Score
    Score --> Present
    
    Present --> Feedback
    Feedback -->|Yes| Modify
    Modify --> Generate
    Feedback -->|No| Approve
    
    Approve -->|Yes| ExecSummary
    Approve -->|No| Modify
    
    ExecSummary --> FullReport
    FullReport --> Artifacts
    Artifacts --> End

    style Init fill:#bbdefb
    style Stage1 fill:#c8e6c9
    style Stage2 fill:#fff9c4
    style Analysis fill:#ffccbc
    style Review fill:#d1c4e9
    style Output fill:#b2dfdb
```

---

## 3. 5단계 컨설팅 프레임워크 상세

```mermaid
flowchart LR
    subgraph S1["🎯 Stage 1<br/>AI 비전 및 전략 수립"]
        S1_1[AI 성숙도 진단]
        S1_2[기회 발굴]
        S1_3[전략/로드맵 수립]
        S1_OUT[산출물:<br/>• AI 비전 선언문<br/>• 성숙도 진단서<br/>• Use Case 후보<br/>• 전략 로드맵]
    end
    
    subgraph S2["📐 Stage 2<br/>Use Case 및 설계 정의"]
        S2_1[상세 요건 정의]
        S2_2[기술 아키텍처 설계]
        S2_3[거버넌스/윤리 수립]
        S2_OUT[산출물:<br/>• 요건 정의서<br/>• 아키텍처 설계서<br/>• 거버넌스 프레임워크]
    end
    
    subgraph S3["🔧 Stage 3<br/>플랫폼 및 솔루션 구축"]
        S3_1[PoC 수행]
        S3_2[AI 플랫폼 구축]
        S3_3[솔루션 개발/통합]
        S3_OUT[산출물:<br/>• PoC 결과 보고서<br/>• 플랫폼 구축 완료<br/>• 통합 솔루션]
    end
    
    subgraph S4["🚀 Stage 4<br/>파일럿 및 확산"]
        S4_1[파일럿 운영]
        S4_2[변화 관리]
        S4_3[전사 확산]
        S4_OUT[산출물:<br/>• 파일럿 결과<br/>• 변화 관리 보고서<br/>• 확산 계획서]
    end
    
    subgraph S5["⚡ Stage 5<br/>운영/모니터링/개선"]
        S5_1[운영 및 모니터링]
        S5_2[피드백 루프]
        S5_3[지속적 개선]
        S5_OUT[산출물:<br/>• 운영 대시보드<br/>• 성과 보고서<br/>• 개선 로드맵]
    end
    
    S1_1 --> S1_2 --> S1_3 --> S1_OUT
    S2_1 --> S2_2 --> S2_3 --> S2_OUT
    S3_1 --> S3_2 --> S3_3 --> S3_OUT
    S4_1 --> S4_2 --> S4_3 --> S4_OUT
    S5_1 --> S5_2 --> S5_3 --> S5_OUT
    
    S1_OUT ==> S2_1
    S2_OUT ==> S3_1
    S3_OUT ==> S4_1
    S4_OUT ==> S5_1

    style S1 fill:#e3f2fd
    style S2 fill:#f3e5f5
    style S3 fill:#fff8e1
    style S4 fill:#e8f5e9
    style S5 fill:#fce4ec
```

---

## 4. 에이전트 오케스트레이션 플로우

```mermaid
flowchart TB
    subgraph Orchestrator["🎭 ConsultingOrchestrator"]
        Init[에이전트 초기화]
        Connect[에이전트 연결<br/>Mesh Network]
        State[WorkflowState<br/>상태 관리]
        Event[이벤트 발생]
    end
    
    subgraph Agents["🤖 전문 에이전트"]
        subgraph Strategy_Agent["Strategy Analyst"]
            SA_1[성숙도 진단]
            SA_2[기회 발굴]
            SA_3[로드맵 수립]
        end
        
        subgraph Designer_Agent["Use Case Designer"]
            DA_1[요건 정의]
            DA_2[아키텍처 설계]
            DA_3[거버넌스 설정]
        end
        
        subgraph ROI_Agent["ROI Analyst"]
            RA_1[ROI 계산]
            RA_2[TCO 분석]
            RA_3[시나리오 비교]
        end
        
        subgraph Risk_Agent["Risk Assessor"]
            RK_1[기술 리스크]
            RK_2[조직 리스크]
            RK_3[운영 리스크]
        end
        
        subgraph Report_Agent["Report Generator"]
            RG_1[Executive Summary]
            RG_2[Full Report]
            RG_3[Strategy Proposal]
        end
    end
    
    subgraph Messages["📨 메시지 프로토콜"]
        Msg_Task[task: 태스크 요청]
        Msg_Result[result: 결과 반환]
        Msg_Feedback[feedback: 피드백]
        Msg_Approval[approval: 승인 요청]
    end
    
    Init --> Connect
    Connect --> State
    State --> Event
    
    Event --> Msg_Task
    Msg_Task --> Strategy_Agent
    Msg_Task --> Designer_Agent
    Msg_Task --> ROI_Agent
    Msg_Task --> Risk_Agent
    Msg_Task --> Report_Agent
    
    Strategy_Agent --> Msg_Result
    Designer_Agent --> Msg_Result
    ROI_Agent --> Msg_Result
    Risk_Agent --> Msg_Result
    Report_Agent --> Msg_Result
    
    Msg_Result --> State
    Msg_Feedback --> State
    Msg_Approval --> State

    style Orchestrator fill:#e1f5fe
    style Strategy_Agent fill:#c8e6c9
    style Designer_Agent fill:#fff9c4
    style ROI_Agent fill:#ffccbc
    style Risk_Agent fill:#f8bbd9
    style Report_Agent fill:#d1c4e9
    style Messages fill:#f5f5f5
```

---

## 5. 데이터 처리 및 분석 플로우

```mermaid
flowchart TD
    subgraph Input["📥 입력 데이터"]
        Basic[기업 기본 정보<br/>name, industry, size]
        IT[IT 인프라<br/>cloud, gpu, server]
        Data[데이터 자산<br/>volume, quality, sources]
        HR[인적 자원<br/>DS, ML Engineer]
        Finance[재무 자원<br/>budget, ROI 기대]
        Org[조직 준비도<br/>경영진 지원, 문화]
    end
    
    subgraph Process["⚙️ 가중치 계산 엔진"]
        direction TB
        Calc_Maturity[성숙도 점수 계산<br/>4대 영역 × 가중치]
        Calc_Fit[적합도 점수 계산<br/>기본 50점 + 보너스]
        Calc_Risk[리스크 점수 계산<br/>확률 × 영향도]
        Calc_Score[종합 점수 계산<br/>ROI×0.6 + Risk×0.4]
    end
    
    subgraph Output["📊 분석 결과"]
        Mat_Result[성숙도 진단 결과<br/>Level 1~5]
        Opp_Result[발굴된 기회<br/>우선순위 정렬]
        Scenario_Result[시나리오 비교<br/>종합 점수]
        Risk_Result[리스크 매트릭스<br/>완화 전략]
    end
    
    Basic --> Calc_Maturity
    IT --> Calc_Maturity
    IT --> Calc_Fit
    Data --> Calc_Maturity
    Data --> Calc_Fit
    HR --> Calc_Maturity
    HR --> Calc_Fit
    Finance --> Calc_Score
    Org --> Calc_Maturity
    Org --> Calc_Risk
    
    Calc_Maturity --> Mat_Result
    Calc_Fit --> Opp_Result
    Calc_Risk --> Risk_Result
    Calc_Score --> Scenario_Result

    style Input fill:#e3f2fd
    style Process fill:#fff8e1
    style Output fill:#e8f5e9
```

### 가중치 계산 상세

```mermaid
flowchart LR
    subgraph Strategy_Score["전략 및 비전 점수"]
        S_Base[기본: 2.0점]
        S_Exec[경영진 지원 ≥4: +1.0]
        S_Budget[AI 예산 >0: +0.5]
    end
    
    subgraph Org_Score["조직 및 역량 점수"]
        O_Base[기본: 1.0점]
        O_DS[데이터 사이언티스트 >0: +1.0]
        O_ML[ML 엔지니어 >0: +1.0]
        O_Exp[AI 프로젝트 경험 >0: +0.5]
        O_Train[교육 예산 >0: +0.5]
    end
    
    subgraph Tech_Score["데이터/기술 점수"]
        T_Base[기본: 1.0점]
        T_Vol[데이터량 >1TB: +0.5]
        T_Qual[데이터 품질 ≥3: +0.5]
        T_Gov[데이터 거버넌스: +1.0]
        T_Cloud[클라우드: +0.5]
        T_GPU[GPU: +0.5]
        T_DW[DW/DL: +1.0]
    end
    
    subgraph Total["종합 레벨"]
        Sum[평균 점수 계산]
        Level[Level 1~5 결정]
    end
    
    S_Base --> Sum
    S_Exec --> Sum
    S_Budget --> Sum
    O_Base --> Sum
    O_DS --> Sum
    O_ML --> Sum
    O_Exp --> Sum
    O_Train --> Sum
    T_Base --> Sum
    T_Vol --> Sum
    T_Qual --> Sum
    T_Gov --> Sum
    T_Cloud --> Sum
    T_GPU --> Sum
    T_DW --> Sum
    
    Sum --> Level

    style Strategy_Score fill:#bbdefb
    style Org_Score fill:#c8e6c9
    style Tech_Score fill:#fff9c4
    style Total fill:#f8bbd9
```

---

## 6. 시나리오 분석 워크플로우

```mermaid
flowchart TD
    Start([시나리오 생성 시작])
    
    subgraph Params["📋 시나리오 파라미터"]
        Conservative[🟢 보수적<br/>예산 60%<br/>리스크 낮음<br/>18개월]
        Balanced[🟡 균형<br/>예산 100%<br/>리스크 중간<br/>24개월]
        Aggressive[🔴 적극적<br/>예산 150%<br/>리스크 높음<br/>36개월]
    end
    
    subgraph Selection["🎯 Use Case 선택"]
        Select_Con[높은 적합도 +<br/>낮은 복잡성<br/>상위 2개]
        Select_Bal[상위 50%]
        Select_Agg[전체 Use Case]
    end
    
    subgraph Analysis["📊 분석 수행"]
        ROI[ROI Analyst<br/>ROI 계산<br/>TCO 분석<br/>NPV/IRR]
        Risk[Risk Assessor<br/>기술 리스크<br/>조직 리스크<br/>운영 리스크]
    end
    
    subgraph Scoring["🏆 점수 계산"]
        ROI_Score[ROI 점수<br/>ROI% ÷ 10<br/>최대 10점]
        Risk_Score[리스크 점수<br/>10 - 총점]
        Total[종합 점수<br/>ROI×0.6 + Risk×0.4]
    end
    
    subgraph Output["📤 결과"]
        Compare[시나리오 비교표]
        Recommend[최적 시나리오 추천]
        Wait[승인 대기<br/>pending_approval=true]
    end
    
    Start --> Conservative
    Start --> Balanced
    Start --> Aggressive
    
    Conservative --> Select_Con
    Balanced --> Select_Bal
    Aggressive --> Select_Agg
    
    Select_Con --> ROI
    Select_Bal --> ROI
    Select_Agg --> ROI
    
    Select_Con --> Risk
    Select_Bal --> Risk
    Select_Agg --> Risk
    
    ROI --> ROI_Score
    Risk --> Risk_Score
    ROI_Score --> Total
    Risk_Score --> Total
    
    Total --> Compare
    Compare --> Recommend
    Recommend --> Wait

    style Params fill:#e3f2fd
    style Selection fill:#fff8e1
    style Analysis fill:#f3e5f5
    style Scoring fill:#c8e6c9
    style Output fill:#ffccbc
```

---

## 7. 인간-AI 협업 워크플로우

```mermaid
flowchart TD
    subgraph AI_Work["🤖 AI 작업"]
        Analysis[분석 수행]
        Generate[결과 생성]
        Present[결과 제시]
    end
    
    subgraph Human_Review["👤 인간 검토"]
        Review[결과 검토]
        Decision{의사결정}
    end
    
    subgraph Feedback_Types["💬 피드백 유형"]
        Approval[✅ 승인<br/>approval]
        Rejection[❌ 반려<br/>rejection]
        Modification[📝 수정 요청<br/>modification]
        Question[❓ 질문<br/>question]
    end
    
    subgraph AI_Response["🤖 AI 응답"]
        Proceed[다음 단계 진행]
        Revise[수정 후 재제출]
        Apply[변경사항 적용]
        Answer[LLM 응답 생성]
    end
    
    subgraph Actions["🎬 액션"]
        Next_Stage[proceed_to_next_stage]
        Resubmit[revise_and_resubmit]
        Apply_Changes[apply_changes]
        Info[provide_information]
    end
    
    Analysis --> Generate
    Generate --> Present
    Present --> Review
    Review --> Decision
    
    Decision -->|승인| Approval
    Decision -->|반려| Rejection
    Decision -->|수정 필요| Modification
    Decision -->|질문 있음| Question
    
    Approval --> Proceed
    Rejection --> Revise
    Modification --> Apply
    Question --> Answer
    
    Proceed --> Next_Stage
    Revise --> Resubmit
    Apply --> Apply_Changes
    Answer --> Info
    
    Resubmit --> Analysis
    Apply_Changes --> Analysis

    style AI_Work fill:#e3f2fd
    style Human_Review fill:#fff8e1
    style Feedback_Types fill:#f3e5f5
    style AI_Response fill:#c8e6c9
    style Actions fill:#ffccbc
```

### 시나리오 승인 프로세스

```mermaid
sequenceDiagram
    participant C as 컨설턴트
    participant O as Orchestrator
    participant A as Agents
    participant LLM as LLM Provider
    
    Note over C,LLM: 시나리오 생성 및 승인 프로세스
    
    C->>O: 시나리오 생성 요청
    O->>A: ROI 분석 요청
    A->>LLM: LLM 분석
    LLM-->>A: 분석 결과
    A-->>O: ROI 결과
    
    O->>A: 리스크 평가 요청
    A->>LLM: LLM 분석
    LLM-->>A: 분석 결과
    A-->>O: 리스크 결과
    
    O->>O: 종합 점수 계산
    O-->>C: 3개 시나리오 제시<br/>(pending_approval=true)
    
    rect rgb(255, 245, 230)
        Note over C: 검토 단계
        C->>C: 시나리오 검토
        
        alt 피드백 있음
            C->>O: 피드백 제출
            O->>LLM: 피드백 처리
            LLM-->>O: AI 응답
            O-->>C: 응답 및 수정 결과
        end
        
        C->>O: 시나리오 승인<br/>(scenario_id, approver)
    end
    
    O->>O: selected_scenario 설정
    O->>O: pending_approval=false
    O->>O: 다음 Stage로 전환
    O-->>C: 승인 완료 응답
```

---

## 8. 보고서 생성 플로우

```mermaid
flowchart TD
    subgraph Collect["📥 데이터 수집"]
        Overview[프로젝트 개요<br/>기업명, 산업, ID]
        Assessment[성숙도 진단 결과<br/>4대 영역 점수]
        UseCases[Use Case 목록<br/>적합도, 우선순위]
        Scenarios[시나리오 분석<br/>ROI, 리스크]
        Selected[선택된 시나리오]
    end
    
    subgraph Compile["⚙️ 데이터 종합"]
        Recommendations[권고사항 종합<br/>_compile_recommendations]
        Benefits[기대효과 종합<br/>_compile_benefits]
        Roadmap[로드맵 종합<br/>_compile_roadmap]
    end
    
    subgraph Generate["📝 보고서 생성"]
        Report_Agent[Report Generator Agent]
        
        subgraph Types["보고서 유형"]
            Exec[Executive Summary<br/>4개 섹션]
            Full[Full Report<br/>6개 챕터]
            Strategy[Strategy Proposal<br/>7개 섹션]
        end
    end
    
    subgraph Output["📤 산출물"]
        Report_ID[보고서 ID 부여]
        Store[보고서 저장]
        Event[이벤트 발생<br/>report_generated]
    end
    
    Overview --> Report_Agent
    Assessment --> Report_Agent
    UseCases --> Report_Agent
    Scenarios --> Report_Agent
    Selected --> Report_Agent
    
    Assessment --> Recommendations
    Scenarios --> Recommendations
    Selected --> Benefits
    Scenarios --> Roadmap
    
    Recommendations --> Report_Agent
    Benefits --> Report_Agent
    Roadmap --> Report_Agent
    
    Report_Agent --> Exec
    Report_Agent --> Full
    Report_Agent --> Strategy
    
    Exec --> Report_ID
    Full --> Report_ID
    Strategy --> Report_ID
    
    Report_ID --> Store
    Store --> Event

    style Collect fill:#e3f2fd
    style Compile fill:#fff8e1
    style Generate fill:#f3e5f5
    style Types fill:#c8e6c9
    style Output fill:#ffccbc
```

### Executive Summary 구조

```mermaid
flowchart LR
    subgraph ES["📋 Executive Summary"]
        S1[1. 프로젝트 개요<br/>배경, 목적, 범위]
        S2[2. 현황 진단 결과<br/>AI 성숙도 Level]
        S3[3. 핵심 제안<br/>권고사항 목록]
        S4[4. 예상 효과<br/>ROI, 정량적 효과]
        S5[5. 실행 로드맵<br/>단기/중기/장기]
    end
    
    S1 --> S2 --> S3 --> S4 --> S5

    style ES fill:#e8f5e9
```

### Full Report 구조

```mermaid
flowchart TB
    subgraph FR["📚 전체 컨설팅 보고서"]
        C1[1장: 개요<br/>배경, 목적, 범위, 추진 경과]
        C2[2장: 현황 분석<br/>성숙도, IT 인프라, 조직 역량, 데이터]
        C3[3장: AI 전략 수립<br/>AI 비전, 핵심 Use Case, 우선순위]
        C4[4장: 실행 계획<br/>로드맵, 투자 계획, 조직/인력]
        C5[5장: 기대 효과<br/>정량적/정성적 효과, ROI 분석]
        C6[6장: 리스크 관리<br/>리스크 식별, 완화 전략]
        APP[부록<br/>용어 정의, 템플릿, 참고자료]
    end
    
    C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> APP

    style FR fill:#f3e5f5
```

---

## 9. API 요청 흐름

```mermaid
sequenceDiagram
    participant Client as 클라이언트
    participant FastAPI as FastAPI Server
    participant Router as API Router
    participant Orch as Orchestrator
    participant Agent as Agents
    participant LLM as LLM Provider
    participant DB as 데이터 저장소
    
    Note over Client,DB: 전체 컨설팅 실행 API 흐름
    
    Client->>FastAPI: POST /api/v1/projects
    FastAPI->>Router: 라우팅
    Router->>Orch: create_project()
    Orch->>DB: 프로젝트 저장
    Orch-->>Router: project_id
    Router-->>Client: 201 Created
    
    Client->>FastAPI: POST /api/v1/projects/{id}/run-full-consultation
    FastAPI->>Orch: run_full_consultation()
    
    rect rgb(230, 243, 255)
        Note over Orch,Agent: Stage 1: 전략 수립
        Orch->>Agent: Strategy Analyst
        Agent->>LLM: 성숙도 진단
        LLM-->>Agent: 결과
        Agent-->>Orch: maturity_assessment
        
        Orch->>Agent: Strategy Analyst
        Agent->>LLM: 기회 발굴
        LLM-->>Agent: 결과
        Agent-->>Orch: opportunities
        
        Orch->>Agent: Strategy Analyst
        Agent->>LLM: 로드맵 수립
        LLM-->>Agent: 결과
        Agent-->>Orch: roadmap
    end
    
    rect rgb(255, 243, 230)
        Note over Orch,Agent: Stage 2: Use Case 설계
        loop 상위 3개 Use Case
            Orch->>Agent: Use Case Designer
            Agent->>LLM: 요건/아키텍처/거버넌스
            LLM-->>Agent: 결과
            Agent-->>Orch: design
        end
    end
    
    rect rgb(243, 230, 255)
        Note over Orch,Agent: 시나리오 분석
        Orch->>Agent: ROI Analyst + Risk Assessor
        Agent->>LLM: 분석
        LLM-->>Agent: 결과
        Agent-->>Orch: scenarios (3개)
    end
    
    rect rgb(230, 255, 230)
        Note over Orch,Agent: 보고서 생성
        Orch->>Agent: Report Generator
        Agent->>LLM: 보고서 작성
        LLM-->>Agent: 결과
        Agent-->>Orch: report
    end
    
    Orch->>DB: 전체 결과 저장
    Orch-->>FastAPI: 완료 응답
    FastAPI-->>Client: 200 OK (results)
```

---

## 부록: 상태 전이 다이어그램

### 프로젝트 Stage 전이

```mermaid
stateDiagram-v2
    [*] --> STRATEGY: 프로젝트 생성
    
    STRATEGY --> DESIGN: 전략 수립 완료
    DESIGN --> BUILD: Use Case 설계 완료
    BUILD --> SCALE: 솔루션 구축 완료
    SCALE --> OPERATE: 파일럿/확산 완료
    OPERATE --> [*]: 프로젝트 종료
    
    note right of STRATEGY: Stage 1<br/>AI 비전 및 전략 수립
    note right of DESIGN: Stage 2<br/>Use Case 및 설계 정의
    note right of BUILD: Stage 3<br/>플랫폼 및 솔루션 구축
    note right of SCALE: Stage 4<br/>파일럿 및 확산
    note right of OPERATE: Stage 5<br/>운영/모니터링/개선
```

### 에이전트 상태 전이

```mermaid
stateDiagram-v2
    [*] --> idle
    
    idle --> working: task received
    working --> completed: success
    working --> error: failure
    working --> waiting: need human input
    
    waiting --> working: feedback received
    completed --> idle: ready for next
    error --> idle: error handled
    
    note right of idle: 대기 중
    note right of working: 작업 수행 중
    note right of waiting: 인간 입력 대기
    note right of completed: 완료
    note right of error: 오류 발생
```

---

## 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2025-12-11 | Brian Lee | 초기 문서 작성 |
| 1.1 | 2025-12-16 | Brian Lee | 문서 업데이트 및 편집자 정보 갱신 |

---

**Copyright © 2025 WDLAB AI/ML/AX Group. All rights reserved.**

