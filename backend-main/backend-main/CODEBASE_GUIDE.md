# Railway AI Project - Codebase Navigation Guide

This guide will help you navigate the major components of your railway AI optimization system. The project is organized into three main parts: **Algorithms**, **Backend API**, and **Frontend**.

## 📁 Project Structure Overview

```
railway_ai-main/
├── algorithms/           # Core optimization algorithms
├── backend/             # FastAPI backend server
├── alogorail-frontend/  # React frontend
├── data/               # CSV data files
├── visualization/      # Data visualization tools
└── tests/             # Unit tests
```

---

## 🧠 Algorithms Directory (`algorithms/`)

The heart of your optimization system. Contains multiple AI/ML algorithms for train scheduling.

### Core Files to Know:

#### 1. **`train_optimizer.py`** - Main Algorithm Hub
- **Purpose**: Central orchestrator that runs all optimization algorithms
- **Key Classes**:
  - `TrainOptimizer` (Lines 274-322): Main class that runs all algorithms and compares results
  - `GeneticAlgorithmOptimizer` (Lines 85-235): GA implementation with population-based evolution
  - `SimpleHeuristicOptimizer` (Lines 24-84): Fast heuristic-based scheduling
  - `HybridOptimizer` (Lines 235-272): Combines multiple approaches
- **Entry Point**: `run_all_optimizations()` method (Lines 284-315)
- **Key Method**: `get_best_result()` (Lines 317-321) - Returns the best performing algorithm
- **Output**: `OptimizationResult` objects with performance metrics

#### 2. **`priority_engine.py`** - Train Priority System
- **Purpose**: Determines train precedence based on Indian Railways standards
- **Key Features**:
  - Train type classification (Lines 13-26): Rajdhani, Express, Passenger, etc.
  - Time-based priority adjustments (Lines 55-70): Peak hours, night hours
  - Delay penalty calculations (Lines 48-49): Delayed trains get lower priority
  - Conflict resolution logic (Lines 72-91): Decides which train gets priority
- **Main Methods**: 
  - `get_train_priority()` (Lines 35-53): Calculates final priority score
  - `resolve_conflict()` (Lines 72-91): Resolves conflicts between two trains
- **Priority Matrix**: `train_type_priority` dictionary (Lines 13-26) defines train rankings

#### 3. **Individual Algorithm Implementations**:
- **`ga_optimizer.py`**: Genetic Algorithm with selection, crossover, mutation
  - Main method: `optimize()` (Lines 11-35)
  - Key functions: `_evaluate()`, `_selection()`, `_crossover()`
- **`aco_optimizer.py`**: Ant Colony Optimization with pheromone trails
  - Main method: `optimize()` (Lines 25-46)
  - Pheromone initialization: `_initialize_pheromones()` (Lines 14-20)
- **`milp_optimizer.py`**: Mixed Integer Linear Programming
- **`rl_optimizer.py`**: Reinforcement Learning with Q-learning
  - Classes: `TrainEnv` (Lines 4-20), `RLAgent` (Lines 22-62)
- **`realtime_optimizer.py`**: Real-time disruption handling

### How to Use:
```python
from algorithms import TrainOptimizer
optimizer = TrainOptimizer()
results = optimizer.run_all_optimizations(trains_df, sections_df, train_sections_df)
best_result = optimizer.get_best_result(results)
```

---

## 🔧 Backend Directory (`backend/app/`)

FastAPI-based REST API server with database integration.

### Core Files to Know:

#### 1. **`main.py`** - API Server Entry Point
- **Purpose**: Main FastAPI application with all route definitions
- **Key Endpoints**:
  - `/stations/` (Lines 38-45): Station CRUD operations
  - `/trains/` (Lines 68-78): Train management
  - `/sections/` (Lines 48-55): Railway section management
  - `/disruptions/` (Lines 58-65): Disruption tracking
  - `/train_sections/` (Lines 81-88): Train-route associations
  - `/import-data/` (Lines 91-94): Trigger CSV data import
- **Database**: SQLAlchemy with async support
- **Route Registration**: Lines 16-26 include all route modules

#### 2. **`models.py`** - Database Schema
- **Purpose**: SQLAlchemy ORM models defining database structure
- **Key Models**:
  - `Train` (Lines 43-60): Train information (ID, type, priority, delays, etc.)
  - `Station` (Lines 11-19): Railway stations with GPS coordinates
  - `Section` (Lines 20-31): Railway track sections between stations
  - `TrainSection` (Lines 62-74): Junction table linking trains to sections
  - `Disruption` (Lines 33-41): Track disruptions and maintenance
- **Enums**: `TrainStatusEnum` (Lines 6-10): on-time, delayed, early
- **Relationships**: Train-TrainSection relationship (Lines 59-60, 73-74)

#### 3. **`ai_decision_engine.py`** - AI Decision Making
- **Purpose**: Real-time conflict resolution using AI
- **Key Classes**:
  - `Train` (Lines 4-21): Train object with priority, delay, efficiency metrics
  - `SectionConflict` (Lines 24-39): Conflict scenarios with competing trains
- **Main Function**: `ai_decision()` (Lines 42-105) - Returns priority recommendations
- **Key Logic**: 
  - Weather delay mapping (Line 52): Clear=0, Rain=2, Fog=5, Storm=10 minutes
  - Train scoring function (Lines 66-83): Combines priority, delay, weather, efficiency
  - Decision logic (Lines 85-103): Sorts trains and assigns proceed/hold decisions
- **Factors Considered**: Priority, delays, weather, platform availability, energy efficiency

#### 4. **Routes Directory (`routes/`)**:
- **`optimization.py`**: Algorithm execution endpoints
  - Main endpoint: `/optimize/` (Lines 101-117)
  - Algorithm functions: `milp_optimizer()`, `ga_optimizer()`, `aco_optimizer()`, `rl_optimizer()`
- **`ai_routes.py`**: AI decision API endpoints
- **`live_data_routes.py`**: Real-time train tracking
  - Endpoint: `/live-trains/` (Lines 16-42) with static dummy data
- **`conflict_alerts_routes.py`**: Conflict detection and alerts
- **`trains.py`**: Train CRUD operations

### Key API Endpoints:
```bash
# Run optimization
GET /optimize/?method=ga

# Get live train positions
GET /live-trains/

# AI conflict resolution
POST /api/ai-decisions

# Train management
GET /trains/
POST /trains/
```

---

## 🎨 Frontend Directory (`alogorail-frontend/`)

React TypeScript application with modern UI components.

### Key Files:
- **`src/App.tsx`**: Main application component
- **`src/components/`**: Reusable UI components
  - `ScheduleView.tsx`: Train schedule visualization
  - `Algorithms.tsx`: Algorithm selection interface
  - `QuickActions.tsx`: Common operations
- **`package.json`**: Dependencies and scripts

---

## 📊 Data Directory (`data/`)

CSV files containing railway network data:
- **`trains.csv`**: Train definitions and schedules
- **`stations.csv`**: Station information
- **`sections.csv`**: Track sections between stations
- **`train_sections.csv`**: Train-route mappings
- **`disruptions.csv`**: Historical disruption data

---

## 🚀 Getting Started - Quick Navigation

### 1. **To Run Optimization Algorithms**:
```bash
cd algorithms/
python train_optimizer.py  # Run all algorithms
```

### 2. **To Start Backend Server**:
```bash
cd backend/
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. **To Start Frontend**:
```bash
cd alogorail-frontend/
npm install
npm start
```

### 4. **To Import Data**:
```bash
POST /import-data/  # Triggers CSV import to database
```

---

## 🔍 Key Integration Points

### 1. **Algorithm → Backend Integration**:
- Backend routes call algorithm modules in `/optimize/` endpoints
- Results are converted to API responses in `routes/optimization.py`

### 2. **Data Flow**:
```
CSV Data → Database Import → API Endpoints → Frontend Visualization
```

### 3. **Real-time Updates**:
- `ai_decision_engine.py` handles live conflict resolution
- `live_data_routes.py` provides real-time train positions
- `conflict_alerts_routes.py` manages disruption notifications

---

## 🛠️ Development Tips

### Adding New Algorithms:
1. Create new file in `algorithms/` directory
2. Implement `optimize()` method returning results
3. Add to `TrainOptimizer` class in `train_optimizer.py`
4. Add API endpoint in `backend/app/routes/optimization.py`

### Modifying Priority System:
- Edit `algorithms/priority_engine.py`
- Update train type priorities in `train_type_priority` dictionary
- Modify time-based multipliers in `time_multipliers`

### Database Changes:
- Update models in `backend/app/models.py`
- Run migrations (if using Alembic)
- Update schemas in `backend/app/schemas.py`

---

## 📈 Performance Monitoring

### Algorithm Performance:
- Check `OptimizationResult.fitness_history` for convergence
- Monitor `computation_time` and `total_delay` metrics
- Use visualization tools in `visualization/` directory

### API Performance:
- Monitor response times in FastAPI logs
- Check database query performance
- Use async endpoints for better concurrency

---

## 🎯 **Critical Code Snippets - Quick Reference**

### **Most Important Algorithm Code**:

#### **Genetic Algorithm Core Loop** (`algorithms/train_optimizer.py` Lines 108-124):
```python
for generation in range(self.generations):
    fitness_scores = [self._calculate_fitness(individual, trains_df) for individual in population]
    
    gen_best_fitness = min(fitness_scores)
    if gen_best_fitness < best_fitness:
        best_fitness = gen_best_fitness
        best_individual = population[gen_best_idx].copy()
    
    population = self._evolve_population(population, fitness_scores)
```

#### **Priority Calculation** (`algorithms/priority_engine.py` Lines 35-53):
```python
def get_train_priority(self, train_info: Dict) -> float:
    base_priority = self.train_type_priority.get(train_info.get('train_type', 'Passenger'), 4)
    time_factor = self._get_time_factor(scheduled_time)
    delay_penalty = min(train_info.get('delay_minutes', 0) * 0.01, 0.5)
    final_priority = base_priority * time_factor + delay_penalty
    return final_priority
```

### **Most Important Backend Code**:

#### **AI Decision Engine Core** (`backend/app/ai_decision_engine.py` Lines 66-83):
```python
def score_train(tid):
    train = trains[tid]
    base = train.priority * 10 + train.delay
    weather_delay = weather_delay_map.get(conflict.weather_condition, 0)
    length_penalty = train.length / 100
    passenger_factor = -train.passenger_load / 1000
    return base + weather_delay + length_penalty - passenger_factor
```

#### **Optimization API Endpoint** (`backend/app/routes/optimization.py` Lines 101-117):
```python
@router.get("/optimize/")
async def optimize_schedule(method: Literal["milp", "ga", "aco", "rl"] = Query(...)):
    if method == "milp":
        result = await milp_optimizer(db)
    elif method == "ga":
        result = await ga_optimizer(db)
    # ... other methods
    return {"status": "success", "data": result}
```

---

This guide should help you navigate and understand the key components of your railway AI optimization system. Each directory has a specific purpose, and understanding these relationships will help you extend and maintain the system effectively.
