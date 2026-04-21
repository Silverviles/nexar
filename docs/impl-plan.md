2.7.1 Implementation Process

The Decision Engine was implemented in five phases that followed the proposal's work breakdown structure. Each phase produced a working increment of the system that was tested before work on the next phase began.

---

Phase 1 - Foundation and Input Processing

The first implementation phase focused on the interfaces by which the Decision Engine receives its inputs. The Feature Extractor module was built to consume the structured output of the Code Analysis Engine, operating on six raw code metrics: lines of code, cyclomatic complexity, token frequency, AST depth, dependency count, and comment ratio. These metrics are passed through three normalization stages — Min-Max scaling, Z-Score standardization, and log transformation — before being fed into a feature engineering layer that computes interaction terms, polynomial features, and applies PCA dimensionality reduction. The resulting output is a 128-dimensional dense feature vector ready for the machine learning layer. A lightweight hardware status monitor was implemented to poll the IBM Quantum and Amazon Braket status endpoints every sixty seconds and cache the results in Redis. A pricing connector was built in parallel to retrieve current per-shot and per-task cost data from the same providers and cache it alongside the status data.

[ Figure 4: Feature Extraction Pipeline - insert diagram showing raw code metrics being normalized into an ML-ready feature vector ]

Figure 4 - Feature Extraction Pipeline

---

Phase 2 - ML Model Development

With inputs flowing reliably, attention turned to the machine learning layer. The training dataset was assembled from three sources: synthetic circuits generated across a range of depths and widths, a catalogue of benchmark problems (QAOA for MaxCut, VQE for small molecules, Grover's search, and instances of Shor's factorization at small scales), and historical execution records contributed by the wider research community. Approximately 4,200 labelled examples were collected in total. A Random Forest (n_estimators=200), an XGBoost model (max_depth=6, learning_rate=0.1), and a three-hidden-layer MLP feedforward network (256→128→64 units) were trained on 70% of the data, validated on 15%, and reserved a held-out 15% for final testing. Hyperparameters were tuned using Bayesian optimization, which reduced the tuning time compared to grid search while achieving comparable or better accuracy. The ensemble was formed by soft voting on predicted class probabilities, with weights of 0.35 for the Random Forest, 0.40 for XGBoost, and 0.25 for the neural network. A confidence score was computed as one minus the standard deviation of the three model predictions.

[ Figure 5: Ensemble ML Model Architecture - insert diagram showing Random Forest, XGBoost, and Neural Network feeding into a soft voting layer ]

Figure 5 - Ensemble ML Model Architecture

---

Phase 3 - Rule System Implementation

In parallel with ML development, the rule-based validator was implemented as a configurable decision tree. Rules were organized into three sequential validation categories: compatibility rules (e.g. minimum qubits, maximum circuit depth per device), safety rules (e.g. reject any circuit whose depth exceeds the coherence budget of the target device), and budget rules (e.g. reject quantum routings when the remaining budget is below the per-shot price). A recommendation failing any compatibility or safety check is immediately rejected. Budget rule failures follow a two-path resolution: if no override flag is set the recommendation is rejected outright; if an override flag is present the recommendation is escalated with a warning rather than dropped, allowing a human reviewer to make the final call. Each rule has an explicit justification and a priority, so that when rules conflict the higher-priority rule wins. The rule configuration is stored in a YAML file that is version-controlled and hot-reloadable without restarting the service.

[ Figure 6: Rule-Based Validation Flow - insert diagram showing incoming recommendation being checked against compatibility, safety, and budget rules ]

Figure 6 - Rule-Based Validation Flow

---

Phase 4 - Cost Analyzer Development

The cost analyzer was implemented as a combination of static price lookup and dynamic execution-time prediction. For each candidate hardware target, the analyzer retrieves the current per-shot or per-task price from the cached pricing snapshot, then estimates the number of shots required and the total payload size based on the workload's feature vector. A queue load weighting factor λ is applied to the base cost to account for queue congestion, yielding a weighted projected cost C_w = C_base × λ. A return-on-investment score is then computed as ROI = (Expected Gain − C_w) / C_w × 100%, where Expected Gain is the predicted performance improvement relative to the best classical alternative. If the ROI meets the configured threshold the recommendation is approved along with a full cost report; otherwise the analyzer substitutes a cheaper alternative target. This ROI score becomes the cost analyzer's contribution to the decision merger.

[ Figure 7: Cost Analyzer Workflow - insert diagram showing pricing lookup, shot estimation, queue-weighted cost, and ROI calculation ]

Figure 7 - Cost Analyzer Workflow

---

Phase 5 - Integration and Decision Merger

The final implementation phase integrated the three decision layers into a unified pipeline. The Decision Merger takes the three recommendations (ML probability, rule verdict, cost ROI), applies confidence-weighted voting to the technical layers (ML and rules), and combines the result with the cost-based ranking according to the selected decision mode (cost-optimized gives more weight to the cost analyzer; performance-optimized gives more weight to the ML layer; balanced uses equal weights). When layers produce incompatible recommendations, an explicit conflict resolution routine selects the option that satisfies the hard safety constraints and has the highest confidence-weighted score. The merger output includes the primary recommendation, at least one alternative, a confidence score, a projected cost, and a textual explanation of the decision, which is useful both for debugging and for audit purposes.
