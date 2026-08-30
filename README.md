TwinSight
From Hidden Risk to Recommended Action

TwinSight is an industrial digital-twin decision-support platform that helps manufacturing teams understand operational risk, simulate interventions, and make better production decisions before acting on the live system.

Manufacturing failures rarely begin as a complete breakdown.

They begin as a small degradation:

a station's cycle time starts increasing,
equipment health deteriorates,
utilization rises,
a bottleneck begins forming,
sensor coverage is incomplete,
or a local risk begins propagating toward downstream operations.

The challenge is not simply detecting that something is wrong.

The challenge is understanding what that risk means for the production system — and deciding what to do next.

TwinSight addresses that gap.

The Problem

Modern manufacturing environments generate enormous amounts of operational data from machines, sensors, production events, vehicles, quality systems, and maintenance systems.

Yet operational decisions are often still fragmented:

Machine Data
     ↓
Monitoring Dashboard
     ↓
Human Interpretation
     ↓
Manual Investigation
     ↓
Manual Decision

Traditional monitoring can tell an operator what is happening.

Predictive models can estimate what might happen.

But neither necessarily answers the operational question that matters most:

"What should we do about it?"

A useful manufacturing intelligence system needs to connect:

operational state → risk → impact → intervention → expected outcome

The TwinSight Approach

TwinSight creates a digital representation of the production environment and connects operational intelligence with decision support.

The platform is designed around a continuous decision loop:

                 ┌──────────────────────┐
                 │   PRODUCTION DATA    │
                 │ telemetry / events   │
                 │ features / state     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    DIGITAL TWIN      │
                 │ plant → line →       │
                 │ station → equipment  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  RISK INTELLIGENCE   │
                 │ health / prediction  │
                 │ root cause / risk    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  RISK PROPAGATION    │
                 │ upstream → downstream│
                 │ dependencies         │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    SIMULATION        │
                 │      WHAT-IF         │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ INTERVENTION /       │
                 │ RECOMMENDATION       │
                 └──────────┬───────────┘
                            │
                            ▼
                       HUMAN DECISION

The goal is not to replace the operator.

The goal is to give the operator better information before making the decision.

What Makes TwinSight Different?

TwinSight goes beyond a conventional monitoring dashboard.

1. It represents the production system

The platform models the manufacturing hierarchy:

Plant
 └── Production Line
      └── Station
           ├── Equipment
           ├── Sensors
           ├── Telemetry
           ├── Features
           └── Operational State

This provides the structural foundation required for a digital twin rather than treating every machine as an isolated data point.

2. It models operational state

TwinSight maintains station-level operational state including information such as:

health state
health risk
confidence
throughput
utilization
work-in-progress
blocking time
starvation time
cycle time
sensor coverage
data quality
instrumentation status

This allows the system to reason about the current state of the production system, rather than only displaying raw telemetry.

3. It incorporates ML-driven risk intelligence

The project includes an ML layer for:

station risk prediction
prediction outcomes
explanations
root-cause information
risk dashboards

The ML components are integrated into the backend service architecture rather than being isolated from the operational system.

4. It models risk propagation

A problem at one station can affect the stations downstream.

TwinSight explicitly represents station dependencies and propagation weights.

For example:

S1
 │
 │ 0.72
 ▼
S2
 │
 │ 0.76
 ▼
S3
 │
 │ 0.84
 ▼
S4
 │
 │ 0.92
 ▼
S5
 │
 │ 0.81
 ▼
S6

This allows the system to reason about operational risk as a network effect, rather than assuming that every station operates independently.

Digital Twin

The backend contains a domain model spanning the major entities required for an industrial digital twin.

The current model includes:

Production structure
Plant
ProductionLine
Station
Route
Physical/industrial entities
Equipment
DataSource
Sensor
Vehicle
Operational data
Telemetry
ProductionEvent
VehicleStationHistory
ManualObservation
QualityEvent
MaintenanceEvent
Derived intelligence
StationFeature
VehicleFeature
StationState
VehicleState
RiskPrediction
PredictionExplanation
RootCause
PredictionRootCause
PredictionOutcome
System relationships
StationDependency
VehicleExposure
Decision intelligence
SimulationRun
SimulationOutcome
Intervention
Recommendation
InterventionExecution

This gives TwinSight a foundation for connecting physical operations, intelligence, and decision-making within the same domain model.

Risk Intelligence

The Risks experience is designed to answer:

Where is the production system becoming vulnerable?

Rather than requiring an operator to inspect every station manually, TwinSight surfaces operational risk at the station level.

The risk layer incorporates:

Operational State
      +
Features
      +
ML Prediction
      +
Root Cause
      +
Station Dependencies
      ↓
Risk Intelligence

The result can then be consumed by the dashboard and simulation workflow.

Risk Propagation

One of the key concepts in TwinSight is that local degradation can become system-level impact.

A station does not exist in isolation.

If an upstream station becomes constrained, its effects can propagate through downstream dependencies.

TwinSight therefore models:

upstream/downstream relationships
propagation weight
propagation delay
dependency confidence

This provides a mechanism for moving from:

"Station S4 is degraded."

toward:

"Station S4 is degraded, and this condition can influence downstream production."

That distinction is important for operational decision-making.

What-If Simulation

The simulation layer is the heart of the decision-support workflow.

Instead of immediately applying an intervention to the live production system, an operator can ask:

"What happens if I change this?"

The simulation interface allows scenario parameters such as:

production line
target station
capacity modifier
risk reduction
scenario name
simulation horizon
number of simulation runs

The backend then produces simulation outcomes for the affected production system.

Simulation Output

Simulation results include:

simulated throughput
simulated risk
throughput delta
risk delta
bottleneck status
scenario status
intervention information
recommendation information

This enables a direct comparison:

BASELINE
   │
   ▼
┌───────────────┐
│ Current State │
└───────┬───────┘
        │
        │ WHAT-IF
        ▼
┌───────────────┐
│ Intervention  │
└───────┬───────┘
        │
        ▼
┌────────────────┐
│ Simulated State│
└───────┬────────┘
        │
        ▼
  Compare Impact

The operator can therefore evaluate the expected consequences of a scenario before making a real-world change.

Intervention Recommendation

Simulation alone is not enough.

If the system can simulate several possible interventions, the next question is:

Which intervention should we consider?

TwinSight includes a recommendation service that evaluates intervention candidates against simulated outcomes.

Recommendations can contain:

intervention
expected throughput gain
expected risk reduction
cost
confidence
decision score
rationale
recommendation status

This moves the workflow from:

"Here are the numbers."

to:

"Here are the numbers, and here is the intervention the system considers most appropriate."

The final decision remains with the human operator.

Example Decision Flow

Consider a degraded station in an automotive assembly line.

S4 — Final Torque & Inspection
          │
          │
          ▼
     Elevated Risk
          │
          ▼
   Potential Bottleneck
          │
          ▼
  Downstream Production Impact
          │
          ▼
    Generate Scenarios
       /          \
      /            \
     ▼              ▼
Controller      Temporary
Recalibration   Operator
     │              │
     ▼              ▼
 Simulation       Simulation
     │              │
     └──────┬───────┘
            ▼
     Compare Outcomes
            │
            ▼
    Recommendation
            │
            ▼
      Human Decision

This is the central value proposition of TwinSight:

The system does not stop at identifying risk. It connects risk to operational consequence and potential action.

The TwinSight User Journey

The frontend is designed around an operational workflow rather than a collection of disconnected dashboards.

Overview

Provides a high-level view of the manufacturing environment.

Plants

Provides plant-level operational context.

Lines

Allows users to inspect individual production lines.

Stations

Provides station-level operational visibility.

Station Twin

Allows an operator to drill into a station and inspect its digital-twin information.

Risks

Surfaces operational risk and potentially vulnerable stations.

Simulation

Allows users to test hypothetical interventions and evaluate projected outcomes.

Together:

OVERVIEW
   ↓
PLANT
   ↓
LINE
   ↓
STATION
   ↓
RISK
   ↓
SIMULATION
   ↓
RECOMMENDATION
Architecture

TwinSight follows a layered backend architecture.

┌─────────────────────────────────────────────┐
│                  React UI                   │
│      Dashboard / Risk / Simulation          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                  REST API                   │
│      Django REST Framework / Serializers    │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│               Service Layer                 │
│                                             │
│ Master / State / Telemetry / Features       │
│ ML / Risk / Simulation / Decision           │
│ Twin / Intervention / Events                │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              Repository Layer               │
│                                             │
│ Persistence abstraction over domain data    │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 Database                   │
│       PostgreSQL / Django ORM models        │
└─────────────────────────────────────────────┘

The ML and simulation capabilities are integrated into this architecture through dedicated services rather than being implemented directly inside frontend components.

Backend Architecture

The Django backend is organized into several layers.

core/
├── api/
│   ├── serializers/
│   └── views/
│
├── repositories/
│
├── services/
│   ├── master/
│   ├── state/
│   ├── telemetry/
│   ├── features/
│   ├── ml/
│   ├── decision/
│   ├── twin/
│   └── ...
│
├── models.py
├── migrations/
└── management/
    └── commands/
Repository Layer

Encapsulates persistence and database access.

Service Layer

Contains business logic and domain workflows.

API Layer

Exposes the platform capabilities to the frontend through REST endpoints.

This separation makes the prototype easier to extend toward a production architecture.

Frontend

The frontend is built using:

React
TypeScript
Vite
React Router
Axios
Recharts
Lucide icons
Tailwind CSS tooling

Current major application areas include:

Overview
Plants
Lines
Stations
Station Detail
Risks
Simulation

The UI uses an industrial operations aesthetic intended to communicate:

production systems
technical state
risk
system dependencies
intervention
decision-making
API Surface

TwinSight exposes REST endpoints for the major domain areas.

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
Digital Twin
GET /api/twin/stations/{station_id}/
GET /api/twin/stations/{station_id}/vehicles/
GET /api/twin/vehicles/{vehicle_id}/
Risk
GET /api/risks/
Simulation
GET /api/simulation/
POST /api/simulation/
GET /api/simulation/{simulation_id}/

The simulation endpoint is particularly important because it connects the frontend scenario builder to the backend simulation and recommendation services.

Technology Stack
Layer	Technology
Frontend	React + TypeScript
Build Tool	Vite
Routing	React Router
HTTP Client	Axios
Visualization	Recharts
Icons	Lucide React
Styling	Tailwind CSS + custom CSS
Backend	Django
API	Django REST Framework
ORM	Django ORM
Database	PostgreSQL
ML	Python / joblib models
Testing	pytest / Django test infrastructure
Architecture	Repository + Service + API layers
Project Structure
twinsight/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── api/
│   │   ├── serializers/
│   │   └── views/
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
│   ├── management/
│   │   └── commands/
│   │
│   └── models.py
│
├── ml/
│   ├── models/
│   ├── scripts/
│   └── data/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── types/
│   ├── public/
│   └── package.json
│
├── manage.py
├── requirements.txt
└── README.md
Demo Dataset

The prototype includes deterministic synthetic manufacturing data designed to demonstrate the TwinSight workflow.

The primary demonstration environment models an automotive vehicle assembly line.

The seeded production structure includes:

Plant
 └── Vehicle Assembly
      └── Assembly Line
           ├── Body Framing
           ├── Paint Preparation
           ├── Powertrain Fitment
           ├── Final Torque & Inspection
           ├── Wheel & Brake Assembly
           └── Final Assembly

The primary demonstration scenario intentionally includes a degraded Final Torque & Inspection station with partial instrumentation.

This creates a meaningful scenario for:

risk analysis
bottleneck identification
propagation
simulation
intervention recommendation

Additional line-state seed support is included through:

python manage.py seed_line_states

The command is designed to be idempotent and provides state records for additional demonstration lines.

Running the Prototype
Prerequisites

Recommended environment:

Python 3.12+
PostgreSQL
Node.js
npm
Backend Setup

Clone the repository:

git clone <repository-url>
cd twinsight

Create and activate a Python virtual environment:

python -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure the database/environment variables according to your local setup.

Run migrations:

python manage.py migrate

Seed the TwinSight demonstration environment using the project's seed command:

python manage.py seed_twinsight

If additional line state data is required:

python manage.py seed_line_states

Run the Django server:

python manage.py runserver

The API will then be available at:

http://127.0.0.1:8000/
Frontend Setup

Open a second terminal:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

For a production build:

npm run build
Testing

Backend checks:

python manage.py check

Run the test suite:

pytest

Frontend production build:

cd frontend
npm run build
Demonstration Walkthrough

For the strongest demonstration, follow this sequence.

01 — Start at Overview

Establish the production environment.

Show that TwinSight represents the manufacturing system rather than a single isolated machine.

02 — Navigate to Stations

Select a station and open its detailed twin.

This demonstrates the transition from:

system-level visibility → station-level intelligence

03 — Examine Risk

Navigate to the Risks view.

Identify the degraded/high-risk area.

Explain that the system is not simply reporting a sensor value — it is representing an operational state and its associated risk.

04 — Inspect the Station Twin

Open the affected station.

Show its operational information and digital-twin context.

This establishes the relationship between:

Station
+
Equipment
+
Operational State
+
Risk
05 — Move to Simulation

Open the Simulation page.

Select the affected production line and station.

Modify the scenario parameters.

06 — Run the Scenario

Run the simulation.

TwinSight evaluates the hypothetical intervention and returns projected outcomes.

The important comparison is:

Baseline
   vs.
Simulated State

Look for:

risk change
throughput change
bottleneck status
scenario status
07 — Review the Recommendation

Review the intervention recommendation.

The system can surface:

intervention
expected risk reduction
expected throughput effect
cost
confidence
decision score
rationale

This is where the prototype demonstrates its most important transition:

From operational intelligence to decision support.

Why This Matters

The value of TwinSight is not any single model, dashboard, or simulation.

It is the connection between them.

A conventional system might provide:

Risk = HIGH

TwinSight aims to provide a richer decision chain:

Risk = HIGH
      ↓
Where?
      ↓
Station S4
      ↓
Why?
      ↓
Degraded operational condition
      ↓
What happens next?
      ↓
Potential production impact
      ↓
What could we do?
      ↓
Candidate interventions
      ↓
What if we do it?
      ↓
Simulation
      ↓
Which option looks best?
      ↓
Recommendation

That is the difference between monitoring and decision intelligence.

Key Innovations
1. Digital Twin + Risk Intelligence

TwinSight combines a structured representation of the manufacturing environment with operational risk intelligence.

2. Risk Propagation

Risk is treated as something that can move through a production dependency network.

3. What-If Decision Support

Interventions can be evaluated through simulation before being applied to the live operation.

4. Recommendation Layer

Simulation results are connected to intervention candidates, allowing the platform to surface actionable options rather than leaving the operator with raw numbers.

5. Human-in-the-Loop

TwinSight is designed as a decision-support system.

The platform informs the operator.

The operator remains responsible for the final action.

Business Value

TwinSight is intended to help manufacturing organizations move from reactive operations toward proactive decision-making.

Potential business outcomes include:

Reduced unplanned disruption

Identify operational degradation before it becomes a larger production problem.

Improved production continuity

Understand how local issues can affect downstream operations.

Better intervention selection

Compare potential responses rather than acting on the first available option.

Reduced decision latency

Bring operational state, risk, simulation, and recommendation into one workflow.

Improved explainability

Provide the operator with the reasoning and expected impact behind a recommended intervention.

Target Users

TwinSight is designed for users such as:

Manufacturing Operations Managers
Plant Managers
Production Engineers
Reliability Engineers
Maintenance Teams
Industrial Data Scientists
Operational Excellence Teams
Prototype Scope

This project is a functional innovation prototype / proof of concept.

It demonstrates the architecture and decision workflow using synthetic demonstration data.

The prototype is not intended to claim production deployment readiness.

In particular:

production integrations would require plant-specific connectors
real industrial telemetry would need secure ingestion pipelines
ML models would require validation against production data
simulation models would require calibration against actual process behavior
intervention execution would require integration with appropriate operational systems and human approval workflows
security, authentication, observability, scalability, and deployment infrastructure would need to be hardened for production

These are deliberate boundaries of the prototype rather than hidden assumptions.

Future Roadmap

The current prototype establishes the core decision loop.

Future versions could extend it with:

Real-time industrial connectivity

Integrate live sources such as:

PLCs
SCADA
MES
historians
IoT platforms
Higher-fidelity digital twins

Incorporate:

process constraints
machine physics
material flow
resource availability
shift schedules
maintenance windows
Advanced simulation

Expand from deterministic what-if scenarios toward:

Monte Carlo simulation
uncertainty modeling
multi-variable scenarios
optimization
reinforcement-learning-assisted intervention selection
Closed-loop operations

With appropriate authorization:

Detect
  ↓
Predict
  ↓
Simulate
  ↓
Recommend
  ↓
Approve
  ↓
Execute
  ↓
Observe
  ↓
Learn
Continuous learning

Use historical outcomes to compare:

Predicted Outcome
       vs.
Actual Outcome

and continuously improve the models and recommendation quality.

Engineering Principles

TwinSight follows several principles throughout the implementation.

Separation of concerns

Persistence, business logic, API representation, and frontend presentation are separated.

Backend-owned intelligence

Simulation and business logic remain in backend services rather than being reproduced in the frontend.

Human-in-the-loop decisions

Recommendations support operators rather than silently executing operational changes.

Explainability

Where possible, recommendations expose the factors behind the proposed intervention.

Extensibility

The layered architecture provides a foundation for adding additional production domains, ML models, simulation capabilities, and integrations.

The Core Idea

Manufacturing systems are interconnected.

A small degradation can become a production problem.

A production problem can become a business problem.

The earlier an organization understands that chain, the more options it has to respond.

TwinSight is built around one simple idea:

Don't wait for the production system to fail before deciding what to do.

Instead:

          OBSERVE
             ↓
           DETECT
             ↓
         UNDERSTAND
             ↓
          PROPAGATE
             ↓
          SIMULATE
             ↓
        RECOMMEND
             ↓
            ACT

TwinSight turns manufacturing data into a decision loop.

Project Status

Innovation Challenge Prototype

The current implementation demonstrates the end-to-end concept across:

Digital Twin modeling
Production structure
Operational state
ML/risk intelligence
Risk propagation
What-if simulation
Intervention evaluation
Recommendation generation
React-based operational interface
Built With

<<<<<<< HEAD
Django · Django REST Framework · PostgreSQL · Python · React · TypeScript · Vite · Recharts · Axios · Tailwind CSS# digitaltwin
=======
Django · Django REST Framework · PostgreSQL · Python · React · TypeScript · Vite · Recharts · Axios · Tailwind CSS
>>>>>>> ebeb11a (updated readme)
