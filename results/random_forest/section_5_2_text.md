# Section 5.2: Random Forest (text for the workspace doc)

Numbers from `notebooks/03_random_forest.ipynb` (this repo, `src/common.py`). Validation only; the test days were not used.

I fitted a Random Forest on the five weather inputs, with City encoded as 16 yes/no columns. Scaling is not needed for trees, so the inputs were not standardized. The City encoding sits inside the model pipeline, so it learns from each fold's training days only. I varied the maximum depth of each tree over 4, 8, 12 and no limit, the minimum number of days in a leaf over 5, 20 and 50, and the class weights over none and balanced, which gives twenty-four settings with 200 trees each. For the best of these I then compared 100, 200 and 500 trees. The number of inputs tried at each split was fixed at the square root of the number of inputs, and the random state at 42. Each setting was scored on the five time-ordered folds inside the training days. The test days were not used.

The table below gives the score of each setting, averaged over the five folds.

| Max depth | Min days in leaf | Class weight | Trees | Macro F1 (core 3) | Danger recall | Danger precision |
|---|---|---|---|---|---|---|
| 4 | 5 | none | 200 | 0.465 | 0.000 | 0.000 |
| 4 | 20 | none | 200 | 0.465 | 0.000 | 0.000 |
| 4 | 50 | none | 200 | 0.464 | 0.000 | 0.000 |
| 8 | 5 | none | 200 | 0.548 | 0.137 | 0.542 |
| 8 | 20 | none | 200 | 0.547 | 0.129 | 0.562 |
| 8 | 50 | none | 200 | 0.533 | 0.103 | 0.657 |
| 12 | 5 | none | 200 | 0.577 | 0.204 | 0.545 |
| 12 | 20 | none | 200 | 0.574 | 0.186 | 0.556 |
| 12 | 50 | none | 200 | 0.555 | 0.142 | 0.653 |
| no limit | 5 | none | 200 | 0.586 | 0.224 | 0.563 |
| no limit | 20 | none | 200 | 0.580 | 0.203 | 0.565 |
| no limit | 50 | none | 200 | 0.556 | 0.144 | 0.597 |
| 4 | 5 | balanced | 200 | 0.606 | 0.760 | 0.320 |
| 4 | 20 | balanced | 200 | 0.603 | 0.780 | 0.314 |
| 4 | 50 | balanced | 200 | 0.599 | 0.784 | 0.304 |
| 8 | 5 | balanced | 200 | 0.637 | 0.724 | 0.363 |
| 8 | 20 | balanced | 200 | 0.628 | 0.755 | 0.343 |
| 8 | 50 | balanced | 200 | 0.622 | 0.782 | 0.335 |
| 12 | 5 | balanced | 200 | 0.650 | 0.650 | 0.397 |
| 12 | 20 | balanced | 200 | 0.633 | 0.758 | 0.355 |
| 12 | 50 | balanced | 200 | 0.622 | 0.782 | 0.333 |
| no limit | 5 | balanced | 200 | 0.644 | 0.597 | 0.412 |
| no limit | 20 | balanced | 200 | 0.639 | 0.771 | 0.361 |
| no limit | 50 | balanced | 200 | 0.624 | 0.781 | 0.333 |
| 12 | 5 | balanced | 100 | 0.647 | 0.650 | 0.396 |
| 12 | 5 | balanced | 500 | 0.653 | 0.672 | 0.402 |

The best setting is a maximum depth of 12, at least 5 days per leaf, balanced class weights and 500 trees. It has the highest macro F1 over the three core levels (0.653 ± 0.039) of the twenty-six settings. Its Danger recall is 0.672 ± 0.193 and its Danger precision is 0.402 ± 0.113. Class weights made the largest difference. Without them, no setting catches more than a quarter of the Danger days (recall 0.00 to 0.22), and the depth 4 forests never predict Danger at all. Balanced weights raise Danger recall to between 0.60 and 0.78, but Danger precision falls to between 0.30 and 0.41. Deeper trees and smaller leaves gave the higher macro F1, while larger leaves raised Danger recall at the cost of macro F1. The number of trees made almost no difference (0.647, 0.650 and 0.653 for 100, 200 and 500 trees). The best setting sits at the edge of the grid for leaf size, so a leaf smaller than 5 days was not checked.

Over the five folds, the chosen setting has accuracy 0.794 ± 0.035, macro F1 over all levels 0.589 ± 0.103, macro F1 over the three core levels 0.653 ± 0.039, and Danger recall 0.672 ± 0.193. The copy-today rule scores 0.679 on the core levels, 0.620 on all levels, 0.846 on accuracy, 0.518 on Danger recall and 0.527 on Danger precision. The Random Forest is therefore higher than the rule only on Danger recall, where it is ahead in all 5 folds (by 0.045 to 0.325). It is lower on core-level macro F1 (ahead in only 1 of the 5 folds, fold 5, by 0.007), on macro F1 over all levels, on accuracy and on Danger precision (behind in every fold). Compared with Logistic Regression (core macro F1 0.632, Danger recall 0.276, accuracy 0.858, Danger precision 0.655) and Gradient Boosting (0.643, 0.670, 0.790, 0.381), it has the highest core macro F1 of the three models, a Danger recall about equal to Gradient Boosting's and a slightly higher Danger precision. The differences between the three models are smaller than the fold-to-fold spread (SD about 0.04), so they are not a clear ranking.

The table below is the confusion matrix for the chosen setting, summed over the five check blocks. Rows are the true level and columns are the predicted level. The 40 Not Hazardous days (all predicted as Caution) and the 3 Caution days predicted as Not Hazardous are left out of the table.

| True / predicted | Caution | Extreme Caution | Danger |
|---|---|---|---|
| Caution | 1,990 | 555 | 0 |
| Extreme Caution | 1,530 | 12,216 | 1,473 |
| Danger | 0 | 382 | 1,171 |

The model catches most Danger days. Of the 1,553 true Danger days, 1,171 are predicted as Danger (a pooled recall of about 75%) and 382 as Extreme Caution; none is predicted as Caution. The cost is false alarms: 1,473 Extreme Caution days are predicted as Danger, so only 1,171 of the 2,644 days called Danger really were (a pooled precision of about 44%). Caution and Extreme Caution are also confused with each other: 1,530 Extreme Caution days are called Caution and 555 Caution days are called Extreme Caution. Today's heat index is by far the most important input. Shuffling it lowers core macro F1 by 0.267 on the last fold, against 0.086 for Temp_Min, 0.069 for solar radiation and 0.023 for pressure; City and rainfall each lower it by about 0.01. In the fitted forest, today's heat index also has the highest importance (0.38), and all 16 city columns together add only 0.03. Danger scores vary a lot between folds: recall rises from 0.36 in the first fold, which learns from only about eight months, to 0.81 in the last fold, because Danger is seasonal and changes from year to year. Like Gradient Boosting, the Random Forest catches more Danger days than the copy-today rule, but it does so with many false alarms and it does not beat the rule on core macro F1, accuracy or Danger precision. Whether the group selects it depends on how the cost of a missed Danger day is weighed against a false alarm in Section 6.
