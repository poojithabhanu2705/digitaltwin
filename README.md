# TwinSight

### Observe → Propagate → Act

TwinSight is a software-based Digital Twin for vehicle assembly operations.

It models the production system as a connected operational state rather than as a purely visual 3D representation. The system combines production structure, telemetry, engineered features, station state, ML predictions, explainability, root-cause reasoning, downstream risk propagation, vehicle exposure tracking, and counterfactual simulation into a single decision pipeline.

The prototype is designed around the DigitalTwin.ai Round 2 problem:

> Build a digital twin prototype of a vehicle assembly line that helps plant teams identify emerging bottlenecks and predict likely defects before they occur.

TwinSight focuses specifically on the technical challenge of doing this with **uneven sensor coverage**, **connected production stations**, and **operationally safe intervention planning**.

---

## 1. What TwinSight Does

TwinSight follows a six-stage operational intelligence pipeline:

```text
Factory Signals
      │
      ▼
┌───────────────┐
│    OBSERVE    │
│ Telemetry     │
│ Events        │
│ Manual Data   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│     INFER     │
│ Station State │
│ Features      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    PREDICT    │
│ Station Risk  │
│ Vehicle Risk  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   EXPLAIN     │
│ SHAP Features │
│ Root Causes   │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  PROPAGATE    │
│ Station Graph │
│ Vehicle       │
│ Exposure      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    SIMULATE   │
│ Counterfactual│
│ Interventions │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│     ACT       │
│ Ranked        │
│ Intervention  │
└───────────────┘

The key design principle is:

A risk prediction is not the final output.

TwinSight converts a local station-level signal into an operational decision:

Station degradation
        ↓
Predicted risk
        ↓
Why is it happening?
        ↓
Where will it propagate?
        ↓
Which vehicles are exposed?
        ↓
What happens if we intervene?
        ↓
Which intervention is preferable?
2. Technical Problem Being Solved

Real assembly lines are heterogeneous systems.

A production line may contain:

modern PLC-connected equipment
legacy machinery
stations with complete instrumentation
stations with partial instrumentation
manual inspection data
different equipment vintages
intermittent failures
upstream/downstream dependencies
defects that only become visible later in the process

The Round 2 problem explicitly calls out uneven sensor coverage, multi-causal bottlenecks and defects, production-system integration constraints, downstream defect propagation, and the need for different operational views.

TwinSight therefore does not treat the factory as a collection of independent machines.

Instead, it represents the production environment as a connected system:

Plant
 └── Production Line
      ├── Station
      │    ├── Equipment
      │    ├── Sensors
      │    ├── Telemetry
      │    ├── Features
      │    └── Current State
      │
      ├── Station Dependencies
      │
      └── Vehicle Flow
           ├── Vehicle State
           ├── Vehicle Features
           └── Station History

This allows the system to reason about both:

local station health
system-level consequences
3. Core Architecture

TwinSight uses a layered backend architecture.

                    React + TypeScript
                           │
                           │ HTTP / JSON
                           ▼
                 Django REST API Layer
                           │
                           ▼
                    Service Layer
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ML / Prediction   Simulation       Decision
       Services         Services        Services
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                   Repository Layer
                           │
                           ▼
                      PostgreSQL

The backend is intentionally separated into:

API layer
Service layer
Repository layer
Persistence/model layer
ML inference layer

The frontend communicates only through API endpoints and does not directly access the database.

4. Technology Stack
Backend
Python
Django 6.1
Django REST Framework
PostgreSQL
psycopg
python-dotenv
Machine Learning
scikit-learn
Random Forest models
joblib model artifacts
NumPy
SHAP for model explanations
Frontend
React
TypeScript
Vite
React Router
Axios
Recharts
Lucide React
Tailwind CSS
Testing
pytest
pytest-django
Django test database
service-level unit tests
service integration tests
ML integration tests
5. Backend Architecture

The backend is organized by responsibility rather than putting business logic directly inside API views.

core/
│
├── api/
│   ├── serializers/
│   ├── views/
│   ├── twin_views.py
│   └── urls.py
│
├── repositories/
│   ├── master_repository.py
│   ├── telemetry_repository.py
│   ├── feature_repository.py
│   ├── state_repository.py
│   ├── prediction_repository.py
│   ├── risk_repository.py
│   ├── riskPropagation_repository.py
│   ├── simulation_repository.py
│   ├── decision_repository.py
│   └── ...
│
├── services/
│   ├── master/
│   ├── telemetry/
│   ├── features/
│   ├── state/
│   ├── twin/
│   ├── ml/
│   ├── decision/
│   ├── simulation_service.py
│   ├── riskPropogation_service.py
│   └── exceptions.py
│
├── models.py
│
└── management/
    └── commands/
        ├── seed_twinsight.py
        └── seed_line_states.py
6. Repository Layer

The Repository Layer isolates database access from business logic.

Services do not need to know how Django ORM queries are constructed.

For example:

PredictionService
       │
       ▼
PredictionRepository
       │
       ▼
RiskPrediction
       │
       ▼
PostgreSQL

This separation provides:

centralized persistence logic
easier testing
lower coupling between services and Django ORM
replaceable data-access implementations
clearer domain boundaries

The repository layer covers the major operational domains:

master data
production structure
telemetry
features
state
predictions
risks
propagation
simulations
decisions
interventions
7. Service Layer

The Service Layer contains the actual business logic.

Important services include:

PlantService
ProductionStructureService
TelemetryService
FeatureService
StateService
TwinService
PredictionService
ExplanationService
RootCauseService
RiskPropagationService
SimulationService
RecommendationService
InterventionService

The services are intentionally composed instead of allowing API views to perform business operations directly.

8. Digital Twin Service

TwinService creates a unified operational representation of a station.

A station twin combines:

Station Master Data
        +
Latest Station State
        +
Latest Features
        +
Latest Telemetry

Conceptually:

{
    "station": station,
    "state": state,
    "features": feature,
    "telemetry": telemetry
}

This means the frontend does not have to independently reconstruct the current station state from multiple database concepts.

The same pattern is used for vehicle-level twin information.

9. Data Model

The prototype uses a relational operational model with approximately 30 domain entities.

Major entities include:

Plant
ProductionLine
Station
Equipment
DataSource
Sensor

Vehicle
Route
VehicleStationHistory

Telemetry
ProductionEvent
ManualObservation
QualityEvent
MaintenanceEvent

StationFeature
VehicleFeature

StationState
VehicleState

RiskPrediction
PredictionExplanation
RootCause
PredictionRootCause
PredictionOutcome

StationDependency
VehicleExposure

SimulationRun
SimulationOutcome

Intervention
Recommendation
InterventionExecution

The model separates:

Static structure
Plant
Line
Station
Equipment
Sensor
Route

from:

Observed data
Telemetry
Events
Manual Observations

from:

Derived state
StationFeature
VehicleFeature
StationState
VehicleState

from:

Intelligence
RiskPrediction
PredictionExplanation
RootCause
VehicleExposure

from:

Decision support
SimulationRun
SimulationOutcome
Intervention
Recommendation
InterventionExecution

This separation is important because a digital twin must distinguish between:

what physically exists
what was observed
what was inferred
what was predicted
what was simulated
10. Handling Uneven Sensor Coverage

One of the main Round 2 challenges is that production lines do not have uniform instrumentation.

TwinSight explicitly models instrumentation quality.

Station state contains fields such as:

sensor_coverage
data_quality
instrumentation_status
confidence

Station features additionally contain:

sensor_coverage_ratio
data_completeness
imputation_ratio
manual_observation_count

The synthetic demonstration deliberately creates a sensor-poor station.

For the primary demonstration line:

S1  Body Framing
S2  Paint Preparation
S3  Powertrain Fitment
S4  Final Torque & Inspection
S5  Wheel & Brake Assembly
S6  Final Assembly

S4 is intentionally configured as:

Instrumentation: PARTIAL
Sensor Coverage: ~78%
Vibration Signal: Missing
Manual Observation: Present

This is deliberate.

The goal is to demonstrate that the twin does not depend on every station having every sensor.

11. Sensor-Poor Inference

The station risk model does not rely on a single physical sensor.

The station risk feature vector includes:

avg_cycle_time
cycle_time_std
cycle_time_trend
throughput
temperature_mean
vibration_mean
utilization
current_cycle_time

Where a signal is unavailable, the broader state/feature representation retains information about:

completeness
coverage
imputation
manual observations
operational state

This creates a path toward a hybrid instrumentation strategy:

Available Sensors
      +
Operational Features
      +
Station State
      +
Manual Observations
      ↓
Station Risk Inference

The prototype uses synthetic data to demonstrate the mechanism rather than claiming production-grade sensor fusion.

12. Machine Learning Layer

TwinSight currently contains two trained model artifacts:

ml/models/
├── station_risk_model.joblib
└── vehicle_defect_model.joblib

The models are loaded through MLModelLoader.

Models are loaded lazily and cached so that repeated API requests do not repeatedly deserialize the model files.

API Request
     ↓
PredictionService
     ↓
MLModelLoader
     ↓
Cached sklearn model
     ↓
Inference
     ↓
RiskPrediction
13. Station Risk Prediction

The Station Risk model predicts the probability/risk of a high-risk station state.

Its input features include:

Average cycle time
Cycle-time variability
Cycle-time trend
Throughput
Temperature
Vibration
Utilization
Current cycle time

The output is persisted as a RiskPrediction.

The prediction contains:

entity_type
entity_id
risk_type
prediction_target
risk_score
confidence
prediction_horizon_minutes
model_name
model_version
timestamp

This makes predictions persistent and traceable instead of being transient values returned directly from an API request.

14. Vehicle Defect Prediction

The second model addresses vehicle-level quality risk.

Its feature vector includes station and vehicle context:

station_avg_cycle_time
station_temperature_mean
station_vibration_mean
station_utilization
station_current_cycle_time

vehicle_avg_cycle_time
vehicle_cycle_time_deviation
vehicle_quality_event_count

The model can therefore incorporate both:

Current station conditions
        +
Vehicle-specific history

instead of treating every vehicle as identical.

15. Prediction Explainability

TwinSight does not treat the ML model as a black box.

ExplanationService uses SHAP TreeExplainer for tree-based model explanations.

The pipeline is:

Prediction
    ↓
Model + Feature Vector
    ↓
SHAP TreeExplainer
    ↓
Feature Contributions
    ↓
PredictionExplanation records

Each explanation stores:

feature_name
contribution
direction
prediction

Contributions are ranked by absolute magnitude so the most influential features appear first.

Example:

cycle_time_trend      +0.34
torque_deviation      +0.27
alarm_rate            +0.18
utilization           +0.11

This gives operators an explanation of what contributed to the risk rather than only showing:

Risk = 86%
16. Root-Cause Reasoning

SHAP explanations are not directly presented as physical root causes.

TwinSight introduces a deterministic root-cause layer.

The RootCauseService combines:

ML explanation evidence
        +
Station state
        +
Operational events

into ranked root causes.

Feature-to-cause mappings include examples such as:

vibration_mean
    → Equipment degradation

temperature_mean
    → Thermal issue

avg_cycle_time
    → Process degradation

cycle_time_trend
    → Process degradation

utilization
    → Process degradation

quality_event_count
    → Quality issue

current_cycle_time
    → Process degradation

Additional evidence can come from:

Maintenance events
Quality events
DEGRADED station state

This creates a separation between:

Model evidence

and:

Operational interpretation

The model predicts risk.

The reasoning layer explains the likely operational cause.

17. Risk Propagation

A production line is not a set of independent stations.

TwinSight represents station relationships using StationDependency.

Example:

S1 ──0.72──> S2
S2 ──0.76──> S3
S3 ──0.84──> S4
S4 ──0.92──> S5
S5 ──0.81──> S6

Each dependency has:

upstream station
downstream station
dependency type
propagation weight
propagation delay
confidence

Risk is propagated using:

downstream_risk
    =
upstream_risk × propagation_weight

Only risks above the configured propagation threshold continue through the graph.

18. Propagation Algorithm

RiskPropagationService uses a queue-based graph traversal.

Conceptually:

Initial Risk
     │
     ▼
Source Station
     │
     ├── downstream station
     │        │
     │        ▼
     │   attenuated risk
     │        │
     │        ▼
     │   next station
     │
     └── ...

The implementation includes:

Thresholding

Small propagated risks are discarded.

Maximum depth

Propagation is bounded to prevent unbounded traversal.

Cycle protection

Previously visited stations are tracked.

Multiple-path handling

If multiple paths reach the same station, the higher-risk path is retained.

Idempotency

Existing exposures for a prediction are checked before creating new exposure records.

This prevents repeated propagation of the same prediction from producing duplicate exposure records.

19. Vehicle Exposure

Station risk is not necessarily the final business/operational impact.

A vehicle can already have passed through an affected station.

TwinSight therefore stores VehicleExposure.

The relationship is:

RiskPrediction
      ↓
StationDependency
      ↓
Downstream Station
      ↓
Vehicle currently/exposed at station
      ↓
VehicleExposure

This allows the system to move from:

"The station is risky."

to:

"These vehicles have been exposed to the risky station."

That is a key part of making the twin operationally relevant.

20. Counterfactual Simulation

TwinSight includes a scenario simulation engine so that an intervention can be evaluated before being applied to the live production system.

This directly addresses the operational constraint that modifying PLCs or live production logic can carry significant production risk.

The workflow is:

Current State
     │
     ▼
Copy State
     │
     ▼
Apply Hypothetical Intervention
     │
     ▼
Recalculate Risk
     │
     ▼
Recalculate Throughput
     │
     ▼
Generate Station Outcomes
     │
     ▼
Rank Intervention

The actual persisted production state is not modified during simulation.

21. Simulation Inputs

A simulation scenario can specify:

line_id
target_station_id
capacity_modifier
risk_reduction_pct
scenario_name
scenario_type
horizon_minutes
number_of_runs

For example:

{
  "line_id": "L1-01",
  "target_station_id": "L1-01-S4",
  "capacity_modifier": 1.2,
  "risk_reduction_pct": 50,
  "scenario_name": "S4 intervention scenario"
}
22. Simulation Calculation

For each station, the simulation derives an effective risk from:

Model prediction
        +
Station health risk
        +
Propagated exposure

The target station then receives the scenario modification.

Risk reduction is applied as:

simulated_risk =
effective_risk × (1 - risk_reduction_pct / 100)

Capacity is modified using:

modified_capacity =
capacity_modifier

The resulting throughput is calculated deterministically:

simulated_throughput =
base_throughput
× capacity_modifier
× (1 - simulated_risk)

The simulation stores:

simulated_throughput
simulated_risk
throughput_delta
risk_delta
is_bottleneck

This creates an auditable counterfactual result.

23. Why the Simulation Is Deterministic

The prototype deliberately uses deterministic simulation mathematics rather than presenting a black-box "AI prediction" of the future.

This is important because the simulation represents:

"What would happen if this intervention changed these parameters?"

rather than:

"What does an LLM think might happen?"

The LLM is not used as the quantitative source of truth.

Quantitative computation is performed through:

stored production state
ML risk predictions
graph propagation
deterministic simulation formulas
deterministic intervention scoring
24. Intervention Recommendation

After simulation, candidate interventions can be evaluated by RecommendationService.

The scoring logic considers:

Expected throughput gain
        +
Expected risk reduction
        -
Intervention cost
        -
Operational disruption

Conceptually:

Decision Score =
throughput_gain
+
(risk_reduction × 100)
-
cost
-
(disruption × 50)

Candidates are ranked deterministically.

Tie-breaking considers:

lower cost
lower disruption
lower intervention ID

This provides reproducible decisions.

The prototype currently demonstrates interventions such as:

Recalibrate S4 Torque Controller

Add Temporary S4 Operator

The architecture is designed so additional intervention types can be added without changing the prediction pipeline.

25. End-to-End Technical Workflow

A complete TwinSight decision flow looks like this:

1. Telemetry / operational data arrives
             │
             ▼
2. Features are generated
             │
             ▼
3. Current station state is maintained
             │
             ▼
4. ML model predicts station risk
             │
             ▼
5. SHAP explains influential features
             │
             ▼
6. Root-cause service ranks operational causes
             │
             ▼
7. Risk propagation traverses station dependencies
             │
             ▼
8. Vehicle exposure is calculated
             │
             ▼
9. Candidate interventions are simulated
             │
             ▼
10. Simulation outcomes are compared
             │
             ▼
11. Intervention recommendation is generated
             │
             ▼
12. Frontend presents the decision context

This is the central technical mechanism of TwinSight.

26. Frontend Architecture

The frontend is a React + TypeScript application.

frontend/src/
│
├── api/
│   ├── cache.ts
│   ├── client.ts
│   ├── lines.ts
│   ├── plant.ts
│   ├── plants.ts
│   ├── risks.ts
│   ├── simulation.ts
│   └── stations.ts
│
├── components/
│   └── layout/
│       ├── AppShell.tsx
│       ├── Sidebar.tsx
│       └── TopBar.tsx
│
├── pages/
│   ├── OverviewPage.tsx
│   ├── Plants.tsx
│   ├── Lines.tsx
│   ├── Stations.tsx
│   ├── StationDetail.tsx
│   ├── Risks.tsx
│   └── Simulation.tsx
│
├── types/
│   └── api.ts
│
├── App.tsx
├── App.css
└── index.css
27. Frontend Routes

The application exposes the following main views:

/
    Overview

/plants
    Plant network

/lines
    Production lines

/stations
    Production stations

/stations/:stationId
    Station digital twin

/risks
    Risk intelligence

/simulation
    Counterfactual simulation

The UI consumes the Django REST API through Axios.

28. API Architecture

The Django API is mounted under:

/api/

Important endpoints include:

Plants
GET /api/plants/
GET /api/plants/{plant_id}/
Production Lines
GET /api/lines/
GET /api/lines/{line_id}/
Stations
GET /api/stations/
GET /api/stations/{station_id}/
Station Telemetry
GET /api/stations/{station_id}/telemetry/latest/
Station Features
GET /api/stations/{station_id}/features/latest/
Station State
GET /api/stations/{station_id}/state/latest/
Vehicle Telemetry
GET /api/vehicles/{vehicle_id}/telemetry/latest/
Vehicle State
GET /api/vehicles/{vehicle_id}/state/latest/
Station Vehicles
GET /api/stations/{station_id}/vehicles/
Station Twin
GET /api/twin/stations/{station_id}/
Station Twin With Vehicles
GET /api/twin/stations/{station_id}/vehicles/
Vehicle Twin
GET /api/twin/vehicles/{vehicle_id}/
Risks
GET /api/risks/
Simulations
GET  /api/simulation/
POST /api/simulation/
GET  /api/simulation/{simulation_id}/
29. Example Simulation Request
POST /api/simulation/
Content-Type: application/json
{
  "line_id": "L1-01",
  "target_station_id": "L1-01-S4",
  "capacity_modifier": 1.2,
  "risk_reduction_pct": 50,
  "scenario_name": "S4 intervention scenario"
}

A completed simulation returns:

{
  "simulation_id": 1,
  "status": "COMPLETED",
  "line_id": "L1-01",
  "scenario_name": "S4 intervention scenario",
  "outcomes": [
    {
      "station_id": "L1-01-S4",
      "simulated_throughput": 65.0,
      "simulated_risk": 0.31,
      "throughput_delta": 11.0,
      "risk_delta": -0.55,
      "is_bottleneck": true
    }
  ]
}
30. Synthetic Prototype Dataset

The prototype intentionally uses synthetic automotive production data.

This is consistent with the Round 2 specification, which explicitly allows illustrative or simulated production data and does not require access to proprietary enterprise data.

The seed environment contains:

2 Plants
3 Production Lines
18 Stations
30 Vehicles

The primary demonstration line is:

L1-01
Pune Vehicle Assembly / Assembly Line 1

It contains:

S1  Body Framing
S2  Paint Preparation
S3  Powertrain Fitment
S4  Final Torque & Inspection
S5  Wheel & Brake Assembly
S6  Final Assembly

The demonstration deliberately makes S4 degraded.

This creates a reproducible scenario in which:

S4 degradation
       ↓
High station risk
       ↓
Root-cause evidence
       ↓
Downstream propagation
       ↓
Vehicle exposure
       ↓
Intervention simulation
31. Seed Commands

The project provides two Django management commands.

Full Demo Seed
python manage.py seed_twinsight

This command:

clears existing TwinSight demo data
recreates plants
recreates production lines
recreates stations
creates routes
creates station dependencies
creates equipment
creates data sources
creates sensors
creates vehicles
creates telemetry
creates events
creates station features
creates vehicle features
creates station state
creates vehicle state
creates risk predictions
creates explanations
creates root causes
creates vehicle exposure
creates simulation data
creates interventions
creates recommendations

This produces a coherent end-to-end demonstration state.

Secondary Line State Seed
python manage.py seed_line_states

This command adds current StationState records to the secondary production lines.

It is idempotent:

Existing state → skipped
Missing state  → created

It does not delete or modify existing state records.

32. Local Setup
Prerequisites

Install:

Python 3.12+
Node.js
npm
PostgreSQL
32.1 Clone the Repository
git clone <repository-url>
cd twinsight
33. Backend Setup

Create a virtual environment:

python3 -m venv .venv

Activate it:

Linux / macOS
source .venv/bin/activate
Windows
.venv\Scripts\activate

Install the repository requirements:

pip install -r requirements.txt

The prototype also requires the runtime packages used by the REST and ML layers:

pip install djangorestframework django-cors-headers numpy scikit-learn joblib shap

For testing:

pip install pytest pytest-django
34. Database Configuration

TwinSight uses PostgreSQL for application data.

Create a .env file in the project root.

Example:

SECRET_KEY=replace-with-a-development-secret

DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

The Django configuration reads the following database variables:

DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
35. Apply Migrations

Run:

python manage.py migrate

Verify Django configuration:

python manage.py check
36. Seed Demo Data

Run:

python manage.py seed_twinsight

Then:

python manage.py seed_line_states

The second command is useful if simulation scenarios need to be demonstrated on all seeded production lines.

37. Start the Backend
python manage.py runserver 8000

The backend will be available at:

http://127.0.0.1:8000/

API root:

http://127.0.0.1:8000/api/
38. Frontend Setup

Open another terminal.

cd frontend

Install dependencies:

npm install

Start Vite:

npm run dev

The frontend will normally be available at:

http://localhost:5173/
39. Recommended Demo Flow

For the complete technical demonstration:

Step 1 — Overview

Open:

http://localhost:5173/

This provides the high-level operational view.

Step 2 — Stations

Open:

http://localhost:5173/stations

Select a station to inspect its twin.

Step 3 — Station Twin

Open a station detail page.

The twin combines:

Structure
State
Features
Telemetry
Risk
Step 4 — Risk View

Open:

http://localhost:5173/risks

Inspect the predicted station risk and supporting intelligence.

Step 5 — Simulation

Open:

http://localhost:5173/simulation

Select:

Production Line
Target Station
Capacity Modifier
Risk Reduction

Then run the scenario.

Step 6 — Compare Outcomes

The simulation evaluates:

Baseline
vs.
Counterfactual state

for the production line.

Step 7 — Intervention

Use the resulting intervention/recommendation information to understand which corrective action produces the best deterministic decision score.

40. Testing

TwinSight has a large service-level test suite.

Run all tests with:

pytest

The project is configured through:

pytest.ini

Tests use:

config.test_settings

which uses an in-memory SQLite database rather than the production PostgreSQL database.

This keeps the test suite isolated from production/demo data.

41. Test Coverage Structure

Tests are organized around the service architecture.

core/services/tests/

├── test_event_service.py
├── test_feature_service.py
├── test_intervention_service.py
├── test_plantservice.py
├── test_production_structure_service.py
├── test_recommendation_service.py
├── test_risk_propogation_service.py
├── test_simulation_service.py
├── test_state_service.py
├── test_telemetry_service.py
├── test_twin_service.py
│
└── ml/
    ├── test_prediction_service.py
    ├── test_explanation_service.py
    ├── test_outcome_service.py
    ├── test_rootcause_service.py
    └── integration tests

The suite covers:

validation
repository interactions
service orchestration
ML inference
explainability
root-cause reasoning
propagation
simulation
recommendation
integration behaviour
42. Verification Snapshot

The prototype was verified using the project test environment.

At the latest verification point:

403 tests passed
82 warnings
3.40 seconds

The warnings were primarily related to a NumPy/joblib deprecation warning and did not cause test failures.

43. Error Handling

The backend uses explicit service-layer exceptions.

Common categories include:

ServiceError
NotFoundError
ValidationError
ConflictError
InvalidStateTransitionError

This prevents business validation from being embedded directly inside API code.

For example:

Invalid station
       ↓
Service validation
       ↓
NotFoundError
       ↓
API response

Similarly, invalid simulation parameters are rejected before simulation execution.

44. Simulation Safety

Simulation operates on copies of the retrieved state.

The service explicitly deep-copies:

station states
predictions
exposures

before applying scenario changes.

Therefore:

Production State
      │
      ├───────────────┐
      │               │
      ▼               ▼
Current System    Simulation Copy
                      │
                      ▼
                Scenario Changes
                      │
                      ▼
                   Outcomes

The simulation cannot directly mutate the baseline objects used to represent the current operational state.

45. Data Lineage

TwinSight preserves a relationship between:

Input
  ↓
Feature
  ↓
Prediction
  ↓
Explanation
  ↓
Root Cause
  ↓
Propagation
  ↓
Exposure
  ↓
Simulation
  ↓
Recommendation

This is important for operational trust.

A recommendation should not appear as an unexplained final number.

Instead, the system can trace the decision backward to:

Which station?
Which prediction?
Which features?
Which root cause?
Which dependencies?
Which vehicles?
Which scenario?
Which intervention?
46. Separation of Quantitative and Interpretive Logic

TwinSight deliberately separates quantitative computation from interpretation.

Quantitative layer

Uses:

ML models
Feature vectors
Risk scores
Graph propagation
Simulation formulas
Decision scoring
Interpretive layer

Uses:

SHAP explanations
Root-cause mappings
Evidence aggregation
Operational labels

This prevents an LLM or natural-language layer from becoming the source of quantitative truth.

47. Why This Architecture Matters

A simpler prototype could have implemented:

CSV
 ↓
ML model
 ↓
Risk score
 ↓
Dashboard

That would demonstrate prediction but would not represent a production digital twin.

TwinSight instead models:

Factory structure
       +
Operational state
       +
Telemetry
       +
ML inference
       +
Explainability
       +
Causal/graph relationships
       +
Vehicle exposure
       +
Counterfactual simulation
       +
Intervention ranking

The result is a decision-oriented digital twin, not simply an ML dashboard.

48. Technical Alignment With DigitalTwin.ai Round 2

The Round 2 DigitalTwin.ai brief highlights:

uneven sensor coverage
multi-causal/intermittent causes
operational risk of modifying live systems
downstream defect propagation
different operational views
variation across plants
validation of predictive claims
explicit vs inferred production variables
predictive techniques
data gaps
legacy/OT integration
scalability and ROI considerations

TwinSight addresses these technically as follows.

Round 2 Challenge	TwinSight Implementation
Uneven sensor coverage	sensor_coverage, data_quality, instrumentation_status, data_completeness, imputation_ratio
Sensor-poor stations	S4 is intentionally partially instrumented with missing vibration
Multi-causal risk	ML explanations + state evidence + event evidence
Bottleneck prediction	Station Risk model
Defect prediction	Vehicle Defect model
Explainability	SHAP-based PredictionExplanation
Root-cause reasoning	RootCauseService
Downstream impact	StationDependency graph
Vehicle impact	VehicleExposure
Live-system intervention risk	Counterfactual SimulationService
Intervention comparison	Deterministic RecommendationService
Production state	StationState / VehicleState
Operational history	Telemetry, events and station history
Multiple plants/lines	Plant → Line → Station hierarchy
Prototype validation	Extensive automated service and integration tests
Scalability	Layered API/service/repository architecture

The Round 2 specification explicitly allows reasonable assumptions and simulated/sample data for the working prototype.

49. Prototype Assumptions

This repository is a prototype rather than a production OT deployment.

The following assumptions are intentionally made:

Production data is synthetic.

Sensor streams are represented through seeded telemetry/state/feature
records rather than direct PLC connections.

ML models are pre-trained artifacts included in the repository.

Simulation uses deterministic scenario mathematics.

Station dependencies are represented explicitly as a directed graph.

Intervention costs and disruption values are illustrative.

Production-scale deployment would require additional OT integration,
security, observability, model governance and infrastructure.

The Round 2 brief explicitly states that the reference parameters are directional rather than a fixed dataset and encourages teams to state assumptions clearly.

50. Production Extension Path

The current prototype can be extended without changing the core decision pipeline.

A production deployment could replace the synthetic input layer with:

PLC / SCADA
    │
    ▼
OPC-UA / MQTT / Industrial Gateway
    │
    ▼
Streaming ingestion
    │
    ▼
Telemetry / Feature pipelines
    │
    ▼
TwinSight state layer

The downstream architecture remains:

State
 ↓
Prediction
 ↓
Explanation
 ↓
Propagation
 ↓
Simulation
 ↓
Recommendation

This separation allows OT integration to evolve independently from the decision-support logic.

51. Scalability Model

TwinSight uses hierarchical identifiers:

Plant
  └── Line
       └── Station
            └── Equipment
                 └── Sensor

and relational identifiers for:

Vehicle
Vehicle ↔ Station
Station ↔ Station
Prediction ↔ Station
Prediction ↔ Vehicle Exposure
Simulation ↔ Intervention

Therefore, scaling from:

1 line

to:

multiple lines
multiple plants
multiple station configurations

does not require rewriting the underlying intelligence pipeline.

The plant and production structure are data-driven.

52. Current Prototype Boundaries

The prototype intentionally does not attempt to solve every production deployment concern.

It does not currently provide:

Direct PLC control
Real-time industrial protocol ingestion
Production-grade streaming infrastructure
Production authentication/authorization
Cloud deployment infrastructure
Model retraining pipelines
Full MLOps monitoring
Production-scale event streaming
Automated maintenance scheduling

Those are deployment-layer extensions rather than requirements for demonstrating the core Digital Twin mechanism.

53. Important Design Principle

TwinSight is designed around:

Observe before acting.

The system does not jump directly from:

Risk detected

to:

Change the factory.

Instead:

Observe
   ↓
Infer
   ↓
Predict
   ↓
Explain
   ↓
Propagate
   ↓
Simulate
   ↓
Recommend
   ↓
Human decision

The simulation layer provides a safety boundary between prediction and intervention.

54. Repository Structure
twinsight/
│
├── config/
│   ├── settings.py
│   ├── test_settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── api/
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── twin_views.py
│   │   └── urls.py
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── seed_twinsight.py
│   │       └── seed_line_states.py
│   │
│   ├── migrations/
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │   ├── decision/
│   │   ├── features/
│   │   ├── master/
│   │   ├── ml/
│   │   ├── state/
│   │   ├── telemetry/
│   │   └── twin/
│   │
│   └── models.py
│
├── ml/
│   └── models/
│       ├── station_risk_model.joblib
│       └── vehicle_defect_model.joblib
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
│
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
55. Quick Start

For a clean local setup:

git clone <repository-url>
cd twinsight

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install djangorestframework django-cors-headers numpy scikit-learn joblib shap
pip install pytest pytest-django

python manage.py migrate
python manage.py check

python manage.py seed_twinsight
python manage.py seed_line_states

Start the backend:

python manage.py runserver 8000

In another terminal:

cd frontend
npm install
npm run dev

Then open:

http://localhost:5173/
56. Summary

TwinSight implements a decision-oriented Digital Twin pipeline:

OBSERVE
Factory signals and operational state

        ↓

INFER
Station and vehicle state

        ↓

PREDICT
Station bottleneck and vehicle defect risk

        ↓

EXPLAIN
SHAP feature contributions

        ↓

REASON
Evidence-based root causes

        ↓

PROPAGATE
Risk through production dependencies

        ↓

EXPOSE
Identify affected vehicles

        ↓

SIMULATE
Test interventions without changing live state

        ↓

DECIDE
Rank corrective actions deterministically

The prototype demonstrates the core mechanism requested for DigitalTwin.ai Round 2: a working digital representation of an automotive production system that goes beyond monitoring and prediction to connect risk → cause → propagation → intervention → simulated outcome.