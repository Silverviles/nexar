DECISION ENGINE FOR QUANTUM-CLASSICAL
CODE ROUTER
25-26J-484
Project Proposal Report
Prasad H G A T
(Siriwardhana A H L T S, Hettiarachchi S R , Jayasinghe Y L)
B.Sc. (Hons) Degree in Information Technology
Specializing in Software Engineering
Department of Information Technology
Sri Lanka Institute of Information Technology
Sri Lanka
August 2025

DECISION ENGINE FOR QUANTUM-CLASSICAL
CODE ROUTER
25-26J-484
Project Proposal Report
B.Sc. (Hons) Degree in Information Technology
Specializing in Software Engineering
Department of Information Technology
Sri Lanka Institute of Information Technology
Sri Lanka
August 2025
2

DECLARATION
Id eclare that this is my own work, and this proposal does not incorporate without
acknowledgement any material previously submitted for a degree or diploma in any
other university or Institute of higher learning and to the best of my knowledge and
belief it does not contain any material previously published or written by another
person except where the acknowledgement is made in the text.
Student Name Student ID Signature
Prasad HGAT IT22056870
The above candidates are carrying out research for the undergraduate Dissertation
under my supervision.
Signature of the Date:
Supervisor:
3

# ABSTRACT
The Decision Engine Component of the Quantum-Classical Code Router (QCCR)
system addresses the critical challenge of intelligent workload distribution between
quantum and classical computing resources. This component includes machine
learning models, rule-based systems, and economic analysis to predict optimal
hardware allocation for a specific workload / computational task. The system
integrates learning techniques including gradient boosting and neural networks with
threshold-based decision trees to ensure robust routing decisions. The cost-benefit
analyser incorporates real time hardware costs, execution time predictions and return
on investment calcultations to optimize resource utilization. The Decision Engine aims
to achieve measurable improvements in exectution efficiency, cost effectiveness and
resource optimization for hybrid quantum and classical environments. This research
contributes to emmerging field of quantum-classical hybrid orchestration by providing
an intelligent, effective, adaptive and economically viable solution for workload
management in the NISQ era.
Keywords- Quantum-Classical Code Router (QCCR), Neural networks, Threshold-
based decision trees, Quantum-classical integration, NISQ era (Noisy Intermediate-
Scale Quantum), Hybrid computing, Adaptive workload management
4

TABLE OF CONTENTS
DECLARATION .......................................................................................................... 3
# ABSTRACT ................................................................................................................. 4
# 1. INTRODUCTION ............................................................................................... 7
## 1.1 Background and Literature Survey .............................................................. 8
## 1.2 Research Gap ............................................................................................. 11
## 1.3 Research Problem ...................................................................................... 12
# 2. OBJECTIVES .................................................................................................... 13
## 2.1 Main Objective ................................................................................................ 13
## 2.2 Specific Objectives .................................................................................... 13
# 3. METHODOLOGY ............................................................................................. 14
## 3.1 Overall System Architecture ...................................................................... 14
## 3.2 Decision Engine System Architecture ........................................................ 15
## 3.3 Component Development Approach .......................................................... 17
3.3.1. Initiation And Planning (Month 1-2) ................................................. 17
3.3.2. Foundation and Input Processing (Month 2-3) .................................. 18
3.3.3. ML Deployment and Performance (Month 3-5) ................................ 19
3.3.4. Integration and Testing (Month 6-7) .................................................. 20
3.3.5. Output and Feedback System Development ...................................... 20
## 3.4 Data Requirements and Storage Strategy ................................................... 22
## 3.5 Implementation Technologies and Tools .................................................... 22
## 3.6 Testing and Validation Strategy.................................................................. 23
# 4. PROJECT REQUIREMENTS ........................................................................... 24
## 4.1 Functional Requirements ........................................................................... 24
## 4.2 Non Functional Requirements ................................................................... 25
# 5. REFERENCES ................................................................................................... 26
5

LIST OF FIGURES
Figure 3.1.1: System Architecture Diagram ............................................................... 14
Figure 3.2.1: Decision Engine High Level Architecture Diagram ............................. 15
Figure 3.2.2 : Decision Engine - Sequence Diagram ................................................ 16
Figure 3.3.1: Development Work Breakdown Structure ............................................ 17
LIST OF TABLES
Table 1-1: Detailed Comparison Table......................................................................... 9
Table 1-2: System Specific Comparison Table .......................................................... 10
LIST OF ABBREVATIONS
Abbreviation Definition
ACID Atomicity, Consistency, Isolation, Durability
AI Artificial Intelligence
API Application Programming Interface
AWS Amazon Web Services
CI/CD Continuous Integration / Continuous Deployment
HPC High Performance Computing
IBM International Business Machines
ML Machine Learning
NISQ Noisy Intermediate-Scale Quantum
QAOA Quantum Approximate Optimization Algorithm
QCCR Quantum-Classical Code Router
REST Representational State Transfer
ROI Return on Investment
VQE Variational Quantum Eigensolver
6

# 1. INTRODUCTION
The improvement of quantum computing in the Noisy Intermediate-Scale Quantum
(NISQ) era has created many opportunities for solving computationaly intensive
problems [1]. However, the practical integration of quantum resources with classical
computing infrastucture remains a significant challenge. Current quantum systems,
while demonstrating the quantum advantages in specific domains are characterized by
limited qubit counts, short coherance times, and high operational costs [2].
The field hybrid quantum - classical computing has gained a lot of attention as
researches recognize that the optimal approach involves intelligently combining both
computing paradigms rather than treating them as different, competing technologies
[3]. Major cloud providers including IBM Quantum, Amazon Braket, Google
Quantum AI have made quantum resources accessible, yet the lack of intelligent
orchestration systems limits their practical utility [4].
Existing research in quantum - classical hybrid systems primarily focuses on algorithm
development and hardware optimization with limited attention to intelligent workload
distribution [5]. While several frameworks exists for quantum programming and
execution; non provide comprehensive decision making capabilities that considor both
suitability and economic factors in real time routing decision [6].
The quantum resource management includes static scheduling approaches and rule-
based systems that lack sophestication required for dynamic learning based
optimization [7]. Recent advances in machine learning for quantum computing has
demonstrated the potential of having a predictive models in quantum circuit
optimization and resource estimation, providing a foundation for inteligent decision
making systems [8].
This research builds upon previous work in quantum resource estimation and hybrid
system management by introducing adaptive learning mechanisms and economic
optimization into decision making aspect addressing the limitations of current
approaches through comprehensive performance prediction and cost benefit analysis.
7

## 1.1 Background and Literature Survey
Quantum Computing Foundation
Quantum computing provides quantum mechanical phenomina including
superposition, entanglement and quantum interference to process information in
fundementally different ways than classical computers [9]. The current NISQ era is
characterized by quantum processers containing 50 – 1000 qubits that are not fault
tollarant but can demonstrate quantum advantages for a specific problem [10].
Hybrid Quantum-Classical Systems
Tannu and Qureshi [11] introduced the concept of quantum aware resource
management highlighting the need for intelligent allocation strategies in a hybrid
system. Their work demonstrated the naïve shedule approach results in significant
resource under-utilization and high operational cost. Salavatov and Palacios [12]
developed Pilot-Quantum, a middleware solution for quantum HPS integration, but
their approach lacks predective capabilities and economic optimizations.
Machine Learning and Quantum Computing
Recent research by Simsek et al. [13] demonstrated the effectiveness of machine
learning approaches in quantum algorithms providing foundational work for predicting
quantum execution requirements. However their research was limited to algorithm
analysis and does not incorperate with real time system conditions or echonomic
factors into decision making process.
Economic Models for Quantum Computing
Current pricing models for quantum cloud services are primary time-based with
limited consideration for algorithmic complexity or expected performance gains [15].
This creates opportunities for optimization through intelligent cost benefit analysis and
considers both computational and economic constraints.
8

Table 1-1: Detailed Comparison Table
Aspect Existing Systems Proposed Decision Engine
Decision Making Limited integration; Unified framework combining ML
Models primarily static rules or models, rule-based systems, and
predetermined thresholds economic analysis
Learning Static configurations without Adaptive learning with continuous
Capabilities feedback mechanisms improvement based on execution
outcomes
Machine Basic ML approaches limited Ensemble methods (Random Forest,
Learning to algorithm analysis only XGBoost, Neural Networks) with
Integration confidence scoring
Economic Time-based pricing models Real-time cost-benefit analysis with
Integration with limited cost ROI calculations and budget
optimization constraints
Multi-Objective Single metric optimization Multi-objective optimization
Optimization (execution time or accuracy) considering cost, performance, and
reliability simultaneously
Real-time Static configurations; cannot Dynamic adaptation to hardware
Adaptability adapt to changing conditions conditions, workload characteristics,
and pricing models
Performance Limited predictive ML-based performance prediction
Prediction capabilities for workload with 85%+ accuracy target for
suitability hardware recommendations
Cost Analysis Basic time-based cost Comprehensive cost analysis
calculations including static costs, execution time
predictions, and ROI analysis
Rule-Based Basic compatibility checking Sophisticated rule-based system with
Validation threshold-based decision trees and
safety constraints
Hardware Limited quantum cloud Multi-cloud support (IBM Quantum,
Integration provider support Amazon Braket, Google Quantum AI)
Decision Latency Variable, often high latency Target <2mins for standard routing
decisions
Throughput Limited concurrent Support for 100+ concurrent routing
processing requests
Feedback Loop No systematic feedback Comprehensive feedback processing
mechanism with automated model retraining
Architecture Monolithic or loosely Multi-layered modular architecture
coupled components with clear component separation
9

Table 1-2: System Specific Comparison Table
System Capabilities Limitations Proposed
Improvements
Pilot- Quantum Basic quantum HPC Lacks predictive Adds ML-based
Middleware integration capabilities and prediction, cost
echonomic analysis, and adaptive
optimization learning
IBM Quantum Quantum resource Static scheduling, Intelligent workload
Network access no intelligent distribution with
routing performance
prediction
Amazon Braket Multi-vendor Limited decision Comprehensive
quantum access support for optimal decision engine with
routing cost-benefit analysis
Current ML Algorithm-specific Limited to algorithm Full system
Approaches optimization analysis, no system integration with real-
integration time conditions and
economic factors
10

## 1.2 Research Gap
Despite significant advances in quantum computing and hybrid systems, several
critical gaps remain in the field of intelligent workload distribution.
I. Absense of Decision Making Models
Current systems lack integrated models that combines computational analysis,
perfomance prediction and economic optimization in a unified decision making
framework.
II. Limited Adaptive Learning Capabilities
Existing solutions primarily rely on static rules and predeterminated thresholds
without incorperating feedback mechanisms that enables continuous
improvements based on execution outcomes.
III. Inadequate Economic Integration
While technical performance metrics are well-studied, the integration of real-time
cost analysis and return-on-investment calculations into routing decisions remains
underdeveloped.
IV. Lack of Multi-Objective Optimization
Current approaches typically optimize for single metrics (e.g., execution time or
accuracy) rather than considering multiple competing objectives including cost,
performance, and reliability.
V. Insufficient Real time Adaptibility
Most existing systems operate with static configurations and cannot adapt to
changing hardware conditions, workload characteristics, or pricing models in real-
time.
This research addresses these gaps by developing a Decision Engine that integrates
machine learning, rule-based reasoning, and economic analysis to provide
comprehensive, adaptive, and cost-effective workload routing decisions.
11

## 1.3 Research Problem
How can we develop a decision making system that optimally routes computational
workloads between quantum and classical resources while considering performance
predictions, real-time costs and system constraints to maximize effiency and cost
effectiveness in hybrid computing environments?
Performance Prediction Challenge
Accurately predicting whether a given computational task will benefit from quantum
execution based on code characteristics and algorithm patterns.
Cost Optimization Challenge
Balancing potential performance gains against the high cost of quantum execution
while respecting budget constraints and maximizing return on investment.
Multi-objective Decision Making
Simultatiously optimizing for execution time, accuracy, cost and resource availability
while handling conflicting objectives and trade-offs.
Real-time Adaptation Challenge
Continuously learning from excecution outcomes and adapting decision models to
changing conditions, hardware capabilities, and workload characteristics.
12

# 2. OBJECTIVES
## 2.1 Main Objective
To develop a Decision Engine that optimally routes computational workloads between
quantum and classical resources using machine learning-based performance
prediction, rule-based validation, and real-time cost-benefit analysis to maximize
execution efficiency and cost-effectiveness in hybrid computing environments.
## 2.2 Specific Objectives
SO1: Core Decision Model Development
Develop and train machine learning models capable of predicting optimal hardware
allocation based on code analysis features, achieving minimum 85% accuracy in
hardware recommendation for standard benchmark problems.
SO2: Rule-based Validation System
Implement a basic rule-based system with threshold-based rules for handling clear-cut
routing cases and enforcing essential safety constraints, ensuring hardware
compatibility validation for supported quantum and classical systems.
SO3: Cost Analysis Framework
Design and implement a cost analysis component that incorporates static hardware
costs and basic execution time predictions to enable cost-aware routing decisions
within predefined budget categories.
SO4: System Integration and Testing
Integrate all components into a functional Decision Engine prototype and validate
performance through systematic testing, demonstrating measurable improvement over
random or simple rule-based routing approaches.
SO5: Evaluation and Future Work Identification
Conduct comprehensive evaluation of the integrated system, document performance
metrics, identify limitations, and propose specific enhancements for advanced adaptive
learning and real-time optimization.
13

# 3. METHODOLOGY
## 3.1 Overall System Architecture
Figure 3.1.1: System Architecture Diagram
As shown in Figure 3.1.1, The Decision Engine operates as the central intelligence
component within the Quantum-Classical Code Router system, receiving processed
code analysis from the Code Analysis Engine and making routing decisions for the
Hardware Abstraction Layer.
14

## 3.2 Decision Engine System Architecture
Figure 3.2.1: Decision Engine High Level Architecture Diagram
The Decision Engine operates as a multi-layered routing system within the Quantum-
Classical Code Router. As illustrated in the Figure 3.2.1, it processes inputs from three
primary sources and generates comprehensive hardware recommendations through
multiple processing layers.
The architecture consists of five main processing layers.
1. Feature Extractor
2. ML Model for Performance Prediction
3. Rule System
4. Cost Analyzer
5. Decision Merger
15

Figure 3.2.2 : Decision Engine - Sequence Diagram
The sequence diagram in Figure 3.2.2 illustrates the complete operational flow of the
Decision Engine module, demonstrating how all components interact to produce
intelligent hardware routing decisions. The process begins when a user or system
submits code to the Code Analysis Engine, which performs comprehensive code
analysis and forwards the results to the Feature Extractor for transformation into
machine learning-ready feature vectors. Simultaneously, the Hardware Status
component retrieves real-time quantum and classical system availability information
and sends it to the Validation Processor for compatibility checking, while Cloud
Provider APIs gather current pricing data and forward it to the Cost Analyzer for
economic feasibility assessment.
The decision-making phase involves three parallel analytical processes: the ML Model
receives extracted features and generates quantum advantage predictions, the Rule
System applies deterministic rules and compatibility constraints using validated input
data, and the Cost Analyzer performs comprehensive cost calculations based on current
pricing information. All three components then send their respective recommendations
to the Decision Merger, which intelligently combines these inputs through confidence
scoring and conflict resolution algorithms to produce the final hardware
recommendation. The Decision Merger returns both the primary hardware
recommendation and alternative options to the user, providing comprehensive routing
guidance with trade-off analysis.
The diagram also illustrates the critical feedback loop that enables continuous system
improvement. Post-execution, the system collects actual performance results and uses
this data to update all three decision models: the ML Model undergoes retraining with
new performance data, the Rule System receives threshold adjustments based on real-
world outcomes, and the Cost Analyzer updates its pricing models with actual
execution costs. This feedback mechanism ensures that the Decision Engine
16

continuously learns from each routing decision, improving its accuracy and
effectiveness over time while adapting to changing quantum hardware capabilities and
pricing structures.
## 3.3 Component Development Approach
Figure 3.3.1: Development Work Breakdown Structure
3.3.1. Initiation And Planning (Month 1-2)
Project Charter & Stakeholders
• Establish project governance structure and stakeholder identification
• Define project scope, objectives, and success criteria
• Create communication protocols and reporting mechanisms
Initial Risks & Requirements
• Conduct comprehensive risk assessment for quantum-classical integration
• Identify technical, operational, and resource-related risks
• Establish mitigation strategies and contingency plans
• Finalize functional and non-functional requirements
17

Technical Architecture
• Design comprehensive system architecture for Decision Engine
• Define component interfaces and data flow specifications
• Establish integration protocols with external quantum cloud providers
• Create detailed technical specifications and API contracts
Resource/Team Setup
• Configure development environments and infrastructure
• Set up cloud provider accounts (IBM Quantum, Amazon Braket)
• Establish version control, CI/CD pipelines, and testing frameworks
• Allocate team resources and define role responsibilities
Detailed Work Plan
• Create granular task breakdowns for each development phase
• Establish milestone checkpoints and deliverable schedules
• Define quality gates and acceptance criteria
• Plan resource allocation and timeline dependencies
3.3.2. Foundation and Input Processing (Month 2-3)
Input Component Integration
• Code Analysis Engine Interface: Develop APIs to receive code complexity
metrics, algorithm patterns, resource requirements, and quantum operation
indicators
• Hardware Status Monitor: Implement real-time monitoring of quantum
system availability (IBM Quantum, Amazon Braket), classical system
loads, queue times, and maintenance schedules
• Cloud Provider API Integration: Create interfaces for real-time pricing
data, cost per operation calculations, budget status tracking, and service
availability monitoring
Feature Extractor Development
• Transform raw code analysis into ML-ready feature vectors.
• Implement complexity metric normalization algorithms.
• Develop pattern extraction mechanisms for quantum advantage
indications.
18

• Create feature selection algorithms for optimal model performance.
Validation Processor Implementation
• Develop data quality validation frameworks
• Implement hardware compatibility checking mechanisms
• Create safety constraint enforcement systems
• Build input filtering for invalid or dangerous requests
3.3.3. ML Deployment and Performance (Month 3-5)
Machine Learning Model Development
Phase I: Model Architecture (Month 3)
• Implement ensemble methods including:
o Random Forest classifiers for robustness
o XGBoost for gradient boosting performance
o Neural Networks for complex pattern recognition
• Develop confidence scoring mechanisms
• Create feature importance analysis tools
Phase II: Training and Optimization (Month 4)
• Generate training datasets from synthetic and benchmark problems
• Perform hyperparameter optimization using Bayesian optimization
• Implement cross-validation for model selection
• Develop quantum advantage probability prediction algorithms
Phase III: Model Integration (Month 5)
• Create ensemble combination strategies
• Implement online learning capabilities
• Develop model updating procedures for continuous improvement
Rule System Implementation (Month 4-5)
• Decision Trees: Define rule hierarchies based on domain expertise
and hardware constraints
• Threshold Rules: Implement clear-cut decision criteria
19

• Compatibility Check: Develop comprehensive hardware compatibility
matrices
• Create deterministic decision paths for safety-critical scenarios
Cost Analyzer Development (Months 4-5)
• Static Cost Calculation: Implement execution cost estimation for
different hardware options
• Time Estimation: Develop workload-based execution time prediction
models
• Budget Check: Create budget constraint validation and tracking
systems
• ROI Analysis: Implement cost vs expected benefit calculation
frameworks
3.3.4. Integration and Testing (Month 6-7)
Decision Merger Development
• Confidence Scoring: Implement weighted decision combination based
on confidence levels
• Conflict Resolution: Develop algorithms to resolve disagreements
between decision models
• Final Recommendation: Create comprehensive decision synthesis
mechanisms
• Alternative Generation: Implement backup option generation with
trade-off analysis
3.3.5. Output and Feedback System Development
I. Hardware Recommendation Engine
• Generate final hardware choices (Quantum/Classical/Hybrid)
with confidence scores
• Provide expected performance metrics and cost estimates
• Create detailed recommendation explanations
20

II. Alternative Options Generator
• Develop secondary recommendation algorithms
• Implement trade-off analysis (cost vs performance vs time)
• Create fallback option generation for primary choice failures
Learning and Feedback Layer
I. Feedback Processor Implementation
• Collect actual execution results from Hardware Abstraction Layer
• Implement prediction accuracy analysis
• Develop performance comparison frameworks
• Create improvement opportunity identification systems
II. Learning Manager Development
• Implement automated ML model retraining workflows
• Develop rule threshold adjustment mechanisms
• Create cost model updates based on real execution data
• Build system performance tracking dashboards
3.3.6. Closeout (Month 8)
Final Evaluation & Documentation
• Conduct comprehensive system performance evaluation
• Document all components, APIs, and operational procedures
• Create user manuals and technical documentation
• Perform final system validation against project objectives
Closure & Handover
• Finalize project deliverables and conduct stakeholder review
• Transfer knowledge to operational teams
• Archive project artifacts and lessons learned
• Conduct post-project review and recommendations
21

## 3.4 Data Requirements and Storage Strategy
Data Collection Strategy
I. Training Data Sources:
• Synthetic computational problems across different complexity classes
• Benchmark quantum and classical algorithms (QAOA, VQE, Shor's,
Grover's)
• Historical execution data from various hardware configurations
• Real-time cost and performance data from quantum cloud providers
II. Data Storage Architecture:
• Cost Models: Historical pricing data, budget tracking, cost predictions
• Performance Metrics: Accuracy scores, response times, prediction
success rates
• Execution History: Past decisions, outcomes, lessons learned for
continuous improvement.
III. Evaluation Datasets
• Standard quantum computing benchmarks
• Classical optimization problems
• Mixed workload scenarios for hybrid system evaluation
• Edge case scenarios for robustness testing
## 3.5 Implementation Technologies and Tools
Core Technologies
• Programming Languages: Python 3.9+ with specialized scientific computing
libraries
• Machine Learning: scikit-learn, XGBoost, TensorFlow/PyTorch for ensemble
methods
• Quantum Frameworks: Qiskit for quantum execution characteristic analysis
• API Integration: RESTful APIs for cloud provider integration (IBM Quantum
Network, Amazon Braket)
22

• Data Management: PostgreSQL for execution history, Redis for real-time data
caching
• Development Environment: Docker containers for reproducible development
environments
Infrastructure:
• Cloud Integration: Multi-cloud support for quantum provider diversity
• Monitoring: Real-time system performance monitoring and alerting
• Scalability: Horizontal scaling capabilities for high-throughput scenarios
## 3.6 Testing and Validation Strategy
Testing Framework
• Unit Testing: Individual component validation with 90%+ code coverage
across all layers
• Integration Testing: End-to-end workflow validation including feedback loops
• Performance Testing: Scalability testing under various load conditions
• Decision Quality Testing: Validation against known optimal routing decisions
23

# 4. PROJECT REQUIREMENTS
## 4.1 Functional Requirements
1. Code Analysis Processing
• The system shall receive and process code analysis results including
complexity metrics, algorithm patterns, and resource requirements
• Input validation and error handling for malformed analysis data
2. Performance Prediction
• The system shall predict execution performance for both quantum and
classical hardware options
• Confidence scoring for prediction reliability
• Multiple prediction scenarios (optimistic, pessimistic, realistic)
3. Hardware Recommendation
• The system shall recommend optimal hardware allocation
(quantum/classical/hybrid)
• Support for preference-based routing (cost-optimized, performance-
optimized, balanced)
• Alternative recommendation provision when primary choice is
unavailable
4. Code Analysis
• Real-time cost calculation for different execution options
• Budget tracking and constraint enforcement
• ROI analysis and cost-benefit reporting
5. Adaptive Learning
• Feedback processing from execution outcomes
• Model retraining and performance improvement
• A/B testing capabilities for decision validation
6. Rule-based Validation
• Hardware compatibility checking
• Safety constraint enforcement
• Fallback decision mechanisms
24

## 4.2 Non Functional Requirements
1. Performance
• Decision latency: < 500ms for standard routing decisions
• Throughput: Support for 100+ concurrent routing requests
• ML model inference time: < 100ms per prediction
2. Reliability
• System availability: 99.5% uptime
• Error handling: Graceful degradation for component failures
• Data consistency: ACID properties for execution history
3. Scalability
• Horizontal scaling support for increased workload
• Model updating without service interruption
• Dynamic resource allocation based on demand
4. Security
• Encrypted communication with external APIs
• Secure storage of execution history and performance data
• Authentication and authorization for system access
5. Maintainability
• Modular architecture for component independence
• Comprehensive logging and monitoring
• Automated testing and deployment pipelines
25

# 5. REFERENCES
[1] J. Preskill, "Quantum Computing in the NISQ era and beyond," Quantum, vol. 2,
p. 79, 2018.
[2] IBM Quantum Network, "IBM Quantum Systems," 2024. [Online]. Available:
https://quantum-computing.ibm.com/
[3] S. S. Tannu and M. K. Qureshi, "A case for quantum-aware resource management
in hybrid quantum-classical systems," Cluster Computing, vol. 23, no. 2, pp. 1041-
1056, 2020.
[4] Amazon Web Services, "Amazon Braket - Quantum Computing Service," 2024.
[Online]. Available: https://aws.amazon.com/braket/
[5] V. Salavatov and A. Palacios, "Pilot-Quantum: A quantum-HPC middleware for
resource, workload and task management," in Proc. IEEE Int. Conf. Quantum Softw.
(QSW), pp. 1-8, Jul. 2023.
[6] A. JavadiAbhari et al., "Quantum computing with Qiskit," in Proc. IEEE Int. Conf.
Quantum Comput. Eng. (QCE), pp. 429-430, Oct. 2021.
[7] N. Khammassi et al., "OpenQL: A portable quantum programming framework for
quantum accelerators," in Proc. IEEE Int. Conf. Quantum Comput. Eng. (QCE), pp.
139-146, Sep. 2018.
[8] S. Simsek, A. Ceran, and F. Yildiz, "Quantum circuit optimization using machine
learning," arXiv preprint arXiv:2305.06585, May 2023.
[9] M. A. Nielsen and I. L. Chuang, Quantum Computation and Quantum Information,
Cambridge University Press, 2010.
[10] F. Arute et al., "Quantum supremacy using a programmable superconducting
processor," Nature, vol. 574, pp. 505-510, 2019.
[11] S. S. Tannu and M. K. Qureshi, "A case for quantum-aware resource management
in hybrid quantum-classical systems," Cluster Computing, vol. 23, no. 2, pp. 1041-
1056, Jun. 2020.
[12] V. Salavatov and A. Palacios, "Pilot-Quantum: A quantum-HPC middleware for
resource, workload and task management," in Proc. IEEE Int. Conf. Quantum Softw.
(QSW), Jul. 2023, pp. 1-8.
26

[13] S. Simsek, A. Ceran, and F. Yildiz, "Quantum circuit optimization using machine
learning," arXiv preprint arXiv:2305.06585, May 2023.
[14] J. Kim, J. Lee, and S. Kim, "Quantum resource estimation for quantum
algorithms," in Proc. IEEE Int. Conf. Quantum Comput. Eng. (QCE), Sep. 2022, pp.
512-519.
[15] IBM, "IBM Quantum Pricing," 2024. [Online]. Available: https://quantum-
computing.ibm.com/pricing
27

