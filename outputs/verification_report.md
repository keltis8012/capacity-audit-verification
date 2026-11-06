# Independent verification report

- checks: 95
- pass: 95
- warn: 0
- fail: 0

| check | expected | actual | status | note |
|---|---:|---:|---|---|
| manifest sha256 01_DATA/data/oulad_events.csv | 48ea54168ef462c73d2a1befd47fc2beff5b5e3cf755f2789a2eca31841ab6b3 | 48ea54168ef462c73d2a1befd47fc2beff5b5e3cf755f2789a2eca31841ab6b3 | PASS | 2301102 bytes |
| manifest sha256 01_DATA/data/xtx_train_truth.csv | cf3d2d0705b2d12aa1ffb84fe84698695873cb9c37a979c0d5e8aebe49da0858 | cf3d2d0705b2d12aa1ffb84fe84698695873cb9c37a979c0d5e8aebe49da0858 | PASS | 1383691 bytes |
| manifest sha256 01_DATA/data/xtx_agg_train.csv | b7c9459154c557d8f3403bed4dc77d90d1cbce1a790fba26a8290bc59accafc2 | b7c9459154c557d8f3403bed4dc77d90d1cbce1a790fba26a8290bc59accafc2 | PASS | 13822869 bytes |
| manifest sha256 01_DATA/data/kdd_events_train.csv | 41b9a468c642b6489e56d9fb2db75e62fd1395d4553b1d6aec29d38fb7bd4d34 | 41b9a468c642b6489e56d9fb2db75e62fd1395d4553b1d6aec29d38fb7bd4d34 | PASS | 17055215 bytes |
| manifest sha256 04_PREMIUM/data/delta_who_oulad.csv | 00c067d2318701980e99634f6394fe733b43ef325537505121cf9e6fdc3806c4 | 00c067d2318701980e99634f6394fe733b43ef325537505121cf9e6fdc3806c4 | PASS | 3451 bytes |
| manifest sha256 04_PREMIUM/data/delta_who_xtx_clean.csv | 9d96cbdde05ec365851e1b4ce21260a9b0abeb2e998c5d5b6dc681af4bc48aa5 | 9d96cbdde05ec365851e1b4ce21260a9b0abeb2e998c5d5b6dc681af4bc48aa5 | PASS | 1830 bytes |
| manifest sha256 04_PREMIUM/data/decision_map.csv | a53748e192a59b326c62d35aede85300bfc22cdaf24c10d6a05827b6c8b96e0d | a53748e192a59b326c62d35aede85300bfc22cdaf24c10d6a05827b6c8b96e0d | PASS | 149 bytes |
| manifest sha256 04_PREMIUM/reports/full_swap.json | 90402a205ea88eeaa49b8775862d64e836dbf827def8bc7bde645ef378b2d9ff | 90402a205ea88eeaa49b8775862d64e836dbf827def8bc7bde645ef378b2d9ff | PASS | 617 bytes |
| manifest sha256 04_PREMIUM/reports/kdd_prediction.json | d22022e78930de49dc9733d5308211363ce27d090a718c5ee02b467536ee9885 | d22022e78930de49dc9733d5308211363ce27d090a718c5ee02b467536ee9885 | PASS | 435 bytes |
| manifest sha256 04_PREMIUM/reports/kdd_observation.json | 5bb25926fb3a422a7fb14f6aa01556029d17f36f09d335995e08714d82756664 | 5bb25926fb3a422a7fb14f6aa01556029d17f36f09d335995e08714d82756664 | PASS | 639 bytes |
| manifest sha256 05_SIGNAL/data/oulad_scores.csv | 12a38f08e6410821f0c73cff438699af48b680085e01f876018a8ed1fed69558 | 12a38f08e6410821f0c73cff438699af48b680085e01f876018a8ed1fed69558 | PASS | 20456090 bytes |
| manifest sha256 05_SIGNAL/data/xtx_scores_clean.csv | c7672a966b87f53c7225825b85807ef0eb5edbec1c880520227c887c40e17257 | c7672a966b87f53c7225825b85807ef0eb5edbec1c880520227c887c40e17257 | PASS | 37611066 bytes |
| manifest sha256 10_PAPER/figs/fig_manifest.json | d0fc7a8a960371ff4702d59f820efb54ecc93b710456f025718b983acc0e75fc | d0fc7a8a960371ff4702d59f820efb54ecc93b710456f025718b983acc0e75fc | PASS | 4713 bytes |
| manifest sha256 build/manuscript.md | df6a4af89c1498dbb2bc14d6ea7bb7874b0ae4c66b506a039ba1d162ce4ec4c7 | df6a4af89c1498dbb2bc14d6ea7bb7874b0ae4c66b506a039ba1d162ce4ec4c7 | PASS | 59811 bytes |
| OULAD rows (score panel) | 15889 | 15889 | PASS |  |
| OULAD withdrawals (panel) | 3264 | 3264 | PASS |  |
| OULAD reachable (panel) | 2688 | 2688 | PASS |  |
| OULAD horizon E[tau-1] (panel) | 13.0 | 12.962053571428571 | PASS |  |
| OULAD AUC F1 (weekly rows) | 0.6639 | 0.6638933423148083 | PASS |  |
| OULAD AUC F2 (weekly rows) | 0.6815 | 0.6814721040924123 | PASS |  |
| OULAD presentations (panel) | 13 | 13 | PASS |  |
| OULAD presentations (full) | 22 | 22 | PASS |  |
| XTX rows (panel enrollments) | 134032 | 134032 | PASS |  |
| XTX positives (panel) | 96081 | 96081 | PASS |  |
| XTX reachable (panel) | 72094 | 72094 | PASS |  |
| XTX horizon E[tau-1] (panel) | 3.1 | 3.1252670125114435 | PASS |  |
| XTX AUC (weekly rows) | 0.7032 | 0.7031588128560377 | PASS |  |
| XTX course median AUC | 0.6669 | 0.6668960444060492 | PASS |  |
| XTX enrollments (full) | 157943 | 157943 | PASS |  |
| XTX positives (full) | 119817 | 119817 | PASS |  |
| XTX courses (full) | 247 | 247 | PASS |  |
| XTX courses (panel) | 246 | 246 | PASS |  |
| KDD enrollments | 120542 | 120542 | PASS |  |
| KDD positives | 95581 | 95581 | PASS |  |
| KDD reachable | 44777 | 44777 | PASS |  |
| KDD courses | 39 | 39 | PASS |  |
| KDD horizon E[tau-1] | 2.7 | 2.683877883734953 | PASS |  |
| OULAD F1 peak height | 0.14 | 0.1400176678445229 | PASS |  |
| OULAD F1 peak midpoint | 0.0384 | 0.0384092369594303 | PASS |  |
| OULAD F2 peak height | 0.1691 | 0.1690874035989716 | PASS |  |
| OULAD F2 peak midpoint | 0.0385 | 0.03850187059907926 | PASS |  |
| XTX peak height | 0.0615 | 0.0614697478292229 | PASS |  |
| XTX peak midpoint | 0.2722 | 0.272185662838486 | PASS |  |
| OULAD F1 capture at 5% | 0.639 | 0.6386925795053003 | PASS |  |
| OULAD F2 capture at 5% | 0.686 | 0.6857326478149101 | PASS |  |
| XTX capture at 5% | 0.103 | 0.1029073154492745 | PASS |  |
| OULAD F1 random at 5% | 0.524 | 0.523851590106007 | PASS |  |
| OULAD F2 random at 5% | 0.549 | 0.549293059125964 | PASS |  |
| XTX random at 5% | 0.086 | 0.0856645490609481 | PASS |  |
| ratio 1% F1 | 14.75 | 14.74863306676605 | PASS |  |
| ratio 1% F2 | 17.51 | 17.50727912325825 | PASS |  |
| ratio 5% F1 | 6.66 | 6.660241565242278 | PASS |  |
| ratio 5% F2 | 7.91 | 7.9128595502702135 | PASS |  |
| swap base position | 0.431 | 0.431 | PASS |  |
| swap cell (real x estimator) | 0.2 | 0.2 | PASS |  |
| observed position | 0.2722 | 0.272185662838486 | PASS |  |
| input effect | -0.231 | -0.23099999999999998 | PASS |  |
| mechanical effect | 0.0722 | 0.07218566283848599 | PASS |  |
| net gap | -0.1588 | -0.158814337161514 | PASS |  |
| KDD prediction mid | 0.4499 | 0.449884844271924 | PASS |  |
| KDD band lower | 0.3099 | 0.309884844271924 | PASS |  |
| KDD band upper | 0.5899 | 0.589884844271924 | PASS |  |
| KDD observed mid | 0.4114 | 0.41136877529913873 | PASS |  |
| KDD observed lower CI | 0.3076 | 0.3075722810923633 | PASS |  |
| KDD containment gap | 0.0023 | 0.0023125631795606894 | PASS |  |
| fold position spread | 0.0026 | 0.002408849452037604 | PASS |  |
| fold AUC spread | 0.0265 | 0.026510016568760276 | PASS |  |
| fold height spread | 0.208 | 0.2076147689213623 | PASS |  |
| figure fig5 sha256 | 219e1c40e52d47a6cb8b84190bb587cf06a4154db13e9fa7935f19a880f9e56d | 219e1c40e52d47a6cb8b84190bb587cf06a4154db13e9fa7935f19a880f9e56d | PASS | byte hash |
| figure fig6 sha256 | e73d396e89b76a91f8657218dbabbfa6fc0c7f92fc0a036da5d3ffa19edc2054 | e73d396e89b76a91f8657218dbabbfa6fc0c7f92fc0a036da5d3ffa19edc2054 | PASS | byte hash |
| figure fig7 sha256 | a30cb9295b55ae04f6b50c12cb2640646f3c53a12ec1d7cc7490289556befdc8 | a30cb9295b55ae04f6b50c12cb2640646f3c53a12ec1d7cc7490289556befdc8 | PASS | byte hash |
| figure fig8 sha256 | 2c4b4def87f5d5cc91fba723aa31523628f41b29072180c44357744759cdcdc4 | 2c4b4def87f5d5cc91fba723aa31523628f41b29072180c44357744759cdcdc4 | PASS | byte hash |
| figure fig2 sha256 | 4d180622f8d5f9234126db21289430af483e359d6ba8d2297d81c8eb6345874d | 4d180622f8d5f9234126db21289430af483e359d6ba8d2297d81c8eb6345874d | PASS | byte hash |
| figure fig2 data 01_DATA/data/oulad_events.csv | 48ea54168ef462c73d2a1befd47fc2beff5b5e3cf755f2789a2eca31841ab6b3 | 48ea54168ef462c73d2a1befd47fc2beff5b5e3cf755f2789a2eca31841ab6b3 | PASS | byte hash |
| figure fig2 data 05_SIGNAL/data/xtx_scores_clean.csv | c7672a966b87f53c7225825b85807ef0eb5edbec1c880520227c887c40e17257 | c7672a966b87f53c7225825b85807ef0eb5edbec1c880520227c887c40e17257 | PASS | byte hash |
| figure fig3 sha256 | 52ee569a0b4dd64dfbf1ff398c9b5249f425b650e384b5969fa263f3b6e65f20 | 52ee569a0b4dd64dfbf1ff398c9b5249f425b650e384b5969fa263f3b6e65f20 | PASS | byte hash |
| figure fig3 data 05_SIGNAL/data/per_course_auc.csv | 544eab72167c5a164f2e8a2fdc1cb8f72a3010eef91da503cc78458023993877 | 544eab72167c5a164f2e8a2fdc1cb8f72a3010eef91da503cc78458023993877 | PASS | byte hash |
| figure fig4 sha256 | cbc10ef74a3063e153f994b210243590235b5533cc14b3863a59bf22bb11bb9d | cbc10ef74a3063e153f994b210243590235b5533cc14b3863a59bf22bb11bb9d | PASS | byte hash |
| figure fig4 data 04_PREMIUM/data/who_oulad_raw.csv | 17911f266b81eda17c74bbd518883bbb3310c6721dd16704ca468173d46aade7 | 17911f266b81eda17c74bbd518883bbb3310c6721dd16704ca468173d46aade7 | PASS | byte hash |
| figure fig4 data 04_PREMIUM/data/delta_who_xtx_clean.csv | 9d96cbdde05ec365851e1b4ce21260a9b0abeb2e998c5d5b6dc681af4bc48aa5 | 9d96cbdde05ec365851e1b4ce21260a9b0abeb2e998c5d5b6dc681af4bc48aa5 | PASS | byte hash |
| figure fig1 sha256 | 280b1733f02446d1e3725ef66042da9d78e47d2e159caca6b41ec88e48341892 | 280b1733f02446d1e3725ef66042da9d78e47d2e159caca6b41ec88e48341892 | PASS | byte hash |
| figure fig_toy sha256 | 1fa5817d9cd9af68dd8803c49f35765f7b321ad61ba03d9c09f841a21917dfb0 | 1fa5817d9cd9af68dd8803c49f35765f7b321ad61ba03d9c09f841a21917dfb0 | PASS | byte hash |
| verification_v1 script sha256 | b9f993be5ff45693b69bb52a8142d7580a6e581867c9ac551636620532459742 | b9f993be5ff45693b69bb52a8142d7580a6e581867c9ac551636620532459742 | PASS | byte hash |
| verification_v1 result sha256 | f289b72e1341f99351f5f205a4dc5752a144cc8a9bfcb39f2939dddcafa11362 | f289b72e1341f99351f5f205a4dc5752a144cc8a9bfcb39f2939dddcafa11362 | PASS | byte hash |
| text contains Table 1 OULAD panel | True | True | PASS | token '15,889' |
| text contains Table 1 XTX panel | True | True | PASS | token '134,032' |
| text contains Table 1 KDD | True | True | PASS | token '120,542' |
| text contains Table 1 OULAD positives | True | True | PASS | token '3,264' |
| text contains Table 1 OULAD reachable | True | True | PASS | token '2,688' |
| text contains Table 1 XTX positives | True | True | PASS | token '96,081' |
| text contains Table 1 XTX reachable | True | True | PASS | token '72,094' |
| text contains Table 1 KDD reachable | True | True | PASS | token '44,777' |
| text contains OULAD peak | True | True | PASS | token '0.0385' |
| text contains XTX peak | True | True | PASS | token '0.2722' |
| text contains dry-run gap | True | True | PASS | token '0.0023' |
