# AURA: Automated Real-time Analytics

AURA is a comprehensive, event-driven AI system built to demonstrate a realistic healthcare use case. It simulates a stream of clinical data, processes it through a Kafka pipeline, makes predictions using both a traditional ML model and a generative LLM, and visualizes the results in a monitoring dashboard.

### Key Features

*   **Microservices Architecture:** Decoupled services for data production, API serving, and consumption.
*   **Event-Driven:** Uses Apache Kafka as a resilient message broker.
*   **Dual AI Models:**
    *   **Risk Prediction:** A `scikit-learn` logistic regression model predicts patient risk from vital signs.
    *   **GenAI Summarization:** A `transformers`-based LLM provides summarization for clinical notes.
*   **Full Observability Stack:**
    *   **Prometheus** for metrics collection.
    *   **Grafana** for dashboarding and visualization.
*   **Containerized:** Fully containerized with Docker and orchestrated with Docker Compose.
*   **Tested and Automated:** Includes a full suite of unit tests with `pytest` and a CI pipeline with GitHub Actions.

### Architecture

```
┌─────────────────┐   ┌─────────┐   ┌─────────────────┐   ┌────────────────┐
│   Producer      │──>│  Kafka  │──>│    Consumer     │──>│  Prediction API│
│ (simulated data)│   │ (topic) │   │ (processes data)│   │ (ML & LLM)     │
└─────────────────┘   └─────────┘   └─────────────────┘   └───────┬────────┘
                                                                  │
                                                                  ▼
                                                          ┌─────────────┐
                                                          │ Prometheus  │
                                                          │ (metrics)   │
                                                          └──────┬──────┘
                                                                 │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │   Grafana   │
                                                          │(dashboards) │
                                                          └─────────────┘
```

### Prerequisites

*   Python 3.12+
*   Docker and Docker Compose

### Getting Started (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zhu-weijie/aura-clinical-analytics
    cd aura-clinical-analytics
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install all dependencies:**
    This command installs the requirements for the applications, development, and testing.
    ```bash
    pip install -r requirements.txt -r requirements-api.txt -r requirements-consumer.txt -r requirements-dev.txt -r requirements-test.txt
    ```

4.  **Install local packages in editable mode:**
    This crucial step makes your local source code importable, which is necessary for `pytest`.
    ```bash
    pip install -e .
    pip install -e packages/aura_core
    ```

5.  **Train the ML Model:**
    This script creates the `aura_risk_model.joblib` file needed by the prediction service.
    ```bash
    python notebooks/train_model.py
    ```

### Running the Tests

After setting up the environment, you can run the entire test suite with a single command. The first run will be slow as it downloads the LLM for testing.

```bash
pytest
```

### Running the Full Application

This single command will build all Docker images and start all services.
```bash
docker compose up --build
```

### Accessing Services

Once the application is running, the services are available at:

*   **Prediction API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Prometheus UI:** [http://localhost:9090](http://localhost:9090)
*   **Grafana Dashboard:** [http://localhost:3000](http://localhost:3000) (Login: `admin` / `admin`)

### Design Diagrams

#### Class Diagram

```mermaid
classDiagram
    direction LR

    class Consumer {
      +run_app()
      +process_messages()
      +wait_for_api()
    }
    
    class Producer {
      +run_app()
      +send_to_kafka(data)
    }

    class Simulator {
      +generate_clinical_data()
    }

    class PredictionAPI {
      <<FastAPI>>
      +predict(data: ClinicalData)
      +summarize(note: ClinicalNote)
    }

    class Predictor {
      <<ML Model>>
      -model: LogisticRegression
      +predict_patient_risk(data)
    }

    class Summarizer {
      <<LLM>>
      -pipeline: SummarizationPipeline
      +summarize_note(text)
    }

    class ClinicalData {
      <<Pydantic Model>>
      +patient_id: str
      +heart_rate: int
      +spo2: float
    }

    class ClinicalNote {
      <<Pydantic Model>>
      +patient_id: str
      +note_text: str
    }

    Consumer ..> PredictionAPI : "Makes HTTP Request"
    Producer ..> Simulator : "Uses"
    PredictionAPI --* Predictor : "Composition"
    PredictionAPI --* Summarizer : "Composition"
    PredictionAPI ..> ClinicalData : "Validates"
    PredictionAPI ..> ClinicalNote : "Validates"
```

#### Entity Relationship Diagram

```mermaid
erDiagram

    subgraph "Use Case: Risk Prediction"
        ClinicalDataInput {
            string patient_id
            string timestamp
            int heart_rate
            string blood_pressure
            float spo2
        }
        PredictionResult {
            string patient_id
            string risk_level
            float score
        }
    end

    subgraph "Use Case: Summarization"
        SummarizationInput {
            string patient_id
            string note_text
        }
        SummarizationResult {
            string patient_id
            int original_note_length
            string summary
            int summary_length
        }
    end

    ClinicalDataInput ||--|{ PredictionResult : "yields"
    SummarizationInput ||--|{ SummarizationResult : "yields"
```

#### Real-Time Risk Prediction Flow

```mermaid
sequenceDiagram
    participant Producer
    participant Kafka
    participant Consumer
    participant PredictionAPI
    participant Prometheus

    par Producer Workflow
        loop Every 2 seconds
            Producer->>Kafka: send(clinical_data)
        end
    and Consumer Workflow
        loop Continuously
            Consumer->>Kafka: poll() for new messages
            Consumer->>PredictionAPI: POST /predict (clinical_data)
            activate PredictionAPI
            PredictionAPI->>PredictionAPI: predict_patient_risk()
            PredictionAPI->>PredictionAPI: PREDICTIONS_TOTAL.inc()
            PredictionAPI-->>Consumer: 200 OK (prediction_json)
            deactivate PredictionAPI
            Consumer->>Consumer: Log "HIGH_RISK_ALERT" or "Prediction Received"
        end
    and Monitoring Workflow
        loop Every 15 seconds
            Prometheus->>PredictionAPI: GET /metrics
            activate PredictionAPI
            PredictionAPI-->>Prometheus: 200 OK (metrics payload)
            deactivate PredictionAPI
        end
    end
```

#### LLM Summarization Flow

```mermaid
sequenceDiagram
    participant User/Client
    participant PredictionAPI
    participant Prometheus

    par Synchronous API Call
        User/Client->>PredictionAPI: POST /summarize (clinical_note)
        activate PredictionAPI
        PredictionAPI->>PredictionAPI: summarize_note()
        PredictionAPI->>PredictionAPI: LLM_SUMMARIZATIONS_TOTAL.inc()
        PredictionAPI-->>User/Client: 200 OK (summary_json)
        deactivate PredictionAPI
    and Monitoring Workflow
        loop Every 15 seconds
            Prometheus->>PredictionAPI: GET /metrics
            activate PredictionAPI
            PredictionAPI-->>Prometheus: 200 OK (metrics payload)
            deactivate PredictionAPI
        end
    end
```

### CI Diagram

```mermaid
graph TD
    subgraph Setup Environment
        A["Start: Manual Trigger"] --> B["Checkout Source Code"];
        B --> C["Set up Python 3.12 Environment"];
        C --> D["Install All Python Dependencies"];
        D --> E["Install Local Project Packages"];
    end

    subgraph Validate Code
        F["Train Machine Learning Model"] --> G["Execute Pytest Suite"];
    end

    subgraph Conclude
        H{"All Tests Passed?"} -- Yes --> I["✅ Success"];
        H -- No --> J["❌ Failure"];
    end

    E --> F;
    G --> H;
```
