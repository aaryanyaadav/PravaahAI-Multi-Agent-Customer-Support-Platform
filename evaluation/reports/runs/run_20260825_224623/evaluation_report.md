# Customer Support Multi-Agent AI — Evaluation Report

**Run Timestamp**: `20260825_224623`  
**Total Queries Evaluated**: `100`  
**Artifact Location**: `D:\project\Customer Support Agentic AI\evaluation\reports\runs\run_20260825_224623`

---

## Executive KPI Summary

| Benchmark Metric | Score | Target | Status |
| :--- | :---: | :---: | :---: |
| **Routing Accuracy** | **73.0%** | ≥ 95.0% | ⚠️ Review |
| **Escalation Accuracy** | **94.0%** | ≥ 95.0% | ⚠️ Review |
| **Ticket Accuracy (Suppression & Creation)** | **94.0%** | 100.0% | ⚠️ Review |
| **Conversational Ticket Suppression** | **100.0%** | 100.0% | ✅ Pass |
| **Answer / Factual Accuracy** | **71.0%** | ≥ 90.0% | ⚠️ Review |
| **Average Keyword Coverage** | **64.66%** | ≥ 85.0% | ⚠️ Review |

---

## Latency & Token Telemetry

| Metric | Measured Value |
| :--- | :--- |
| **Median Latency (p50)** | `1.539s` |
| **90th Percentile Latency (p90)** | `47.434s` |
| **99th Percentile Latency (p99)** | `64.262s` |
| **Average Response Duration** | `12.633s` (Min: `0.339s`, Max: `64.262s`) |
| **Total Tokens Consumed** | `177,305` tokens |
| **Average Tokens per Query** | `1773.0` tokens |

---

## Category-wise Performance Breakdown

| Category | Queries | Routing Acc | Escalation Acc | Ticket Acc | Answer Acc |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **BILLING** | 20 | 95.0% | 95.0% | 95.0% | 70.0% |
| **CONVERSATIONAL** | 8 | 100.0% | 100.0% | 100.0% | 100.0% |
| **CRM** | 20 | 95.0% | 95.0% | 95.0% | 75.0% |
| **ESCALATION** | 10 | 40.0% | 60.0% | 60.0% | 40.0% |
| **GUARDRAIL_SAFETY** | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| **KNOWLEDGE** | 15 | 40.0% | 100.0% | 100.0% | 53.3% |
| **REFUND** | 10 | 0.0% | 100.0% | 100.0% | 100.0% |
| **TICKET** | 15 | 100.0% | 100.0% | 100.0% | 66.7% |

---

## Agent Routing Performance & Confusion Matrix

### Per-Agent Metrics

| Agent | Support | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **billing** | 20 | 55.88% | 95.0% | 70.37% |
| **crm** | 20 | 82.61% | 95.0% | 88.37% |
| **escalation** | 10 | 100.0% | 40.0% | 57.14% |
| **input_guard** | 10 | 100.0% | 100.0% | 100.0% |
| **knowledge** | 15 | 54.55% | 40.0% | 46.15% |
| **refund** | 10 | 0.0% | 0.0% | 0.0% |
| **ticket** | 15 | 88.24% | 100.0% | 93.75% |

### Confusion Matrix (Rows = Expected, Columns = Predicted)

| Expected \ Actual | billing | crm | escalation | input_guard | knowledge | refund | ticket |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **billing** | 19 | 0 | 0 | 0 | 1 | 0 | 0 |
| **crm** | 0 | 19 | 0 | 0 | 1 | 0 | 0 |
| **escalation** | 2 | 1 | 4 | 0 | 3 | 0 | 0 |
| **input_guard** | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| **knowledge** | 3 | 3 | 0 | 0 | 6 | 1 | 2 |
| **refund** | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| **ticket** | 0 | 0 | 0 | 0 | 0 | 0 | 15 |

---

## Divergent / Warning Scenarios (46 items)

| ID | Query | Expected Agent | Actual Agent | Esc (Exp/Act) | Tkts (Exp/Act) | Note |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 9 | `What is the contract status and exp...` | `crm` | `crm` | False/False | 0/0 | Kw Cov: 0% |
| 11 | `What is the contract status and exp...` | `crm` | `crm` | False/False | 0/0 | Kw Cov: 0% |
| 12 | `What is the contract status and exp...` | `crm` | `crm` | False/False | 0/0 | Kw Cov: 0% |
| 15 | `List all users and administrators r...` | `crm` | `crm` | False/True | 0/1 | Esc: False != True, Tkt: 0 != 1, Kw Cov: 0% |
| 16 | `List all users and administrators r...` | `crm` | `knowledge` | False/False | 0/0 | Route: crm != knowledge, Kw Cov: 0% |
| 22 | `What is the latest invoice amount a...` | `billing` | `billing` | False/False | 0/0 | Kw Cov: 0% |
| 23 | `What is the latest invoice amount a...` | `billing` | `knowledge` | False/False | 0/0 | Route: billing != knowledge, Kw Cov: 0% |
| 24 | `What is the latest invoice amount a...` | `billing` | `billing` | False/True | 0/1 | Esc: False != True, Tkt: 0 != 1, Kw Cov: 0% |
| 33 | `Can you explain the charge and deta...` | `billing` | `billing` | False/False | 0/0 | Kw Cov: 0% |
| 35 | `Can you explain the charge and deta...` | `billing` | `billing` | False/False | 0/0 | Kw Cov: 0% |
| 36 | `Can you explain the charge and deta...` | `billing` | `billing` | False/False | 0/0 | Kw Cov: 33% |
| 46 | `Check the status, subject, and prio...` | `ticket` | `ticket` | False/False | 0/0 | Kw Cov: 33% |
| 47 | `Check the status, subject, and prio...` | `ticket` | `ticket` | False/False | 0/0 | Kw Cov: 33% |
| 48 | `Check the status, subject, and prio...` | `ticket` | `ticket` | False/False | 0/0 | Kw Cov: 33% |
| 49 | `Check the status, subject, and prio...` | `ticket` | `ticket` | False/False | 0/0 | Kw Cov: 33% |

---
*Report generated automatically by the Customer Support Agentic AI Evaluation Framework.*
