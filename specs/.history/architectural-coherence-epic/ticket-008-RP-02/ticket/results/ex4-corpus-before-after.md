# RP-02 ex4 corpus regeneration -- before and after

## BEFORE (epic tip 506e0e0, unmodified generator)
```
 330             params={'i': UNCHECKED},
```
cases.py sha256: 33e07e0de5360fae105466c0ea7869a4face3c3dfa116de63452888c78be6f97
(matches evidence/corpus_fingerprint.txt of record: 33e07e0de5360fae105466c0ea7869a4face3c3dfa116de63452888c78be6f97)

## AFTER (RP-02 set-membership recovery)
```
 165             params={'i': 'i1'},
 165             params={'i': 'i2'},
```
cases.py sha256 run 1: 944189052623960aea36dd9277c9d714c76ce18d584a67d8ed5b498170648f2e
cases.py sha256 run 2: 944189052623960aea36dd9277c9d714c76ce18d584a67d8ed5b498170648f2e

## Determinism: two independent regenerations, every artifact
```
IDENTICAL  cases.py  944189052623960aea36dd9277c9d714c76ce18d584a67d8ed5b498170648f2e
IDENTICAL  types.py  e741372b2ea4b48c6973bb8046e99b46469c6ae865f17c0dc563122d5be1fcfa
IDENTICAL  validators.py  871aa336b6b59f097ac64fe89d1cb665a09716a9b008b34c34502266d40577d1
IDENTICAL  doubles.py  8a14e70da7e508d9a6db6537cf402b783703c780e7f3236756d5e9740062332b
IDENTICAL  __init__.py  a02e8442b83ffc6cfd51b59cdaf78bc6c92f5e477456bfef208a5343f986b291
IDENTICAL  param_recovery_audit.md  a4070dc5d02be99baa032f481401991144c53c48f3c1b2000ff4a797b2971a33
IDENTICAL  docs.md  4fd6fd500421ee9f6116eb0ba5882d9f3ea1c28aca069bb95e5b02bdc44df5a5
DIFFER     case_coverage.json  ba0fd97abd04bc1af6dfe380d91a072a6be026af2dfceb0258e099d134abfc37  01449d5f64ce9858a8d05b5b0b6b7d6efbf0c458959872593463570ee30e61d7
```

## Corpus shape: are there any rejected inputs to catch a guard with?
```
Traceback (most recent call last):
  File "/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage/specs/tickets/RP-02/results/harness/corpus_shape.py", line 23, in <module>
    spec.loader.exec_module(module)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 755, in exec_module
  File "<frozen importlib._bootstrap_external>", line 892, in get_code
  File "<frozen importlib._bootstrap_external>", line 950, in get_data
FileNotFoundError: [Errno 2] No such file or directory: '/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage/specs/tickets/RP-02/results/harness/after-gen/spec-unit/pipeline_cases/__init__.py'
cases: 330
expected output statuses: {'applied': 330}

action      cases  arg ENABLED  arg REJECTED
Accept         22           22             0
Deliver        66           66             0
Enqueue       110          110             0
Fail           88           88             0
Record         44           44             0
TOTAL         330          330             0

argument/before-state pairs the model would REFUSE that a corpus COULD have emitted: 220 (over 330 cases x 2 items)
emitted by the generator: 0 -- a state graph has no edge for a refused argument.
```
