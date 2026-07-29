# Доказательная база

Дата актуализации: 2026-07-28.

Источники ниже использованы только в пределах их назначения. Reporting
guidelines не интерпретированы как доказательство качества конкретной модели,
а правовые документы — как автоматическая классификация продукта.

## 1. Model и datasets

1. Hugging Face, публичный профиль `trpakov`, models.
   https://huggingface.co/trpakov/models  
   Применимость: текущий публичный список model artifacts автора. На дату
   проверки видны две модели, не включая указанную malaria-модель.

2. NIH/NLM, официальный malaria data index.
   https://data.lhncbc.nlm.nih.gov/public/Malaria/  
   Применимость: официальный перечень разных malaria datasets и mapping
   files. Наличие данных не доказывает, что они использованы текущей моделью.

3. NIH/NLM Thin Blood Smears Pf.
   https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/  
   Применимость: whole-smear resource, статистика и license agreement; не
   смешивать с cropped `cell_images.zip`.

4. Rajaraman S. et al. Pre-trained convolutional neural networks as feature
   extractors toward improved malaria parasite detection in thin blood smear
   images. PeerJ. 2018;6:e4568. DOI: 10.7717/peerj.4568.
   https://doi.org/10.7717/peerj.4568  
   Применимость: исходная постановка malaria cell classification и данные.
   Не является evidence для неизвестной Hugging Face модели.

5. Poostchi M. et al. Malaria parasite detection and cell counting for human
   and mouse using thin blood smear microscopy. Journal of Medical Imaging.
   2018;5(4):044506. DOI: 10.1117/1.JMI.5.4.044506.
   https://doi.org/10.1117/1.JMI.5.4.044506  
   Применимость: detection/counting в thin smears; подчёркивает отличие
   whole-smear workflow от isolated-cell classification.

5a. WHO. Malaria parasite counting, microscopy SOP 09. 2016.
    https://www.who.int/publications/i/item/HTM-GMP-MM-SOP-09
    Применимость: counting thick/thin films является отдельной процедурой;
    single-cell classifier её не реализует.

5b. WHO/TDR. Microscopy for detection, identification and quantification of
    malaria parasites on stained thick and thin blood films in research
    settings. 2015.
    https://apo.who.int/publications/i/item/2015-04-28-microscopy-for-the-detection-identification-and-quantification-of-malaria-parasites-on-stained-thick-and-thin-blood-films-in-research-settings
    Применимость: research microscopy quality and reporting standards.

5c. NLM. NIH-NLM Thin Blood Smears Pf ReadMe.
    https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/ReadMe.pdf
    Применимость: отдельный whole thin-smear detection resource с patient
    directories; не смешивать с cropped `cell_images.zip`.

## 2. Reporting и risk of bias

6. Tejani A.S. et al. Checklist for Artificial Intelligence in Medical
   Imaging (CLAIM): 2024 Update. Radiology: Artificial Intelligence.
   2024;6(4):e240300. DOI: 10.1148/ryai.240300.
   https://doi.org/10.1148/ryai.240300  
   Применимость: прозрачность и воспроизводимость medical imaging AI.

7. Collins G.S. et al. TRIPOD+AI statement: updated guidance for reporting
   clinical prediction models that use regression or machine learning
   methods. BMJ. 2024;385:e078378. DOI: 10.1136/bmj-2023-078378.
   https://doi.org/10.1136/bmj-2023-078378  
   Применимость: reporting development/evaluation studies. Сами авторы
   указывают, что checklist не является quality appraisal tool.

8. Moons K.G.M. et al. PROBAST+AI: an updated quality, risk of bias, and
   applicability assessment tool for prediction models using regression or
   artificial intelligence methods. BMJ. 2025;388:e082505.
   DOI: 10.1136/bmj-2024-082505.
   https://doi.org/10.1136/bmj-2024-082505  
   Применимость: formal risk-of-bias/applicability assessment после появления
   study package.

9. Sounderajah V. et al. The STARD-AI reporting guideline for diagnostic
   accuracy studies using artificial intelligence. Nature Medicine.
   2025;31:3283–3289. DOI: 10.1038/s41591-025-03953-8.
   https://doi.org/10.1038/s41591-025-03953-8  
   Применимость: diagnostic accuracy study reporting.

10. Lekadir K. et al. FUTURE-AI: international consensus guideline for
    trustworthy and deployable artificial intelligence in healthcare. BMJ.
    2025;388:e081554. DOI: 10.1136/bmj-2024-081554.
    https://doi.org/10.1136/bmj-2024-081554  
    Применимость: lifecycle principles fairness, universality, traceability,
    usability, robustness и explainability.

11. Vasey B. et al. DECIDE-AI: reporting guideline for early-stage clinical
    evaluation of decision support systems driven by artificial intelligence.
    Nature Medicine. 2022. DOI: 10.1038/s41591-022-01772-9.
    https://doi.org/10.1038/s41591-022-01772-9

12. Liu X. et al. CONSORT-AI extension. Nature Medicine. 2020.
    DOI: 10.1038/s41591-020-1034-x.
    https://doi.org/10.1038/s41591-020-1034-x

13. Cruz Rivera S. et al. SPIRIT-AI extension. Nature Medicine. 2020.
    DOI: 10.1038/s41591-020-1037-7.
    https://doi.org/10.1038/s41591-020-1037-7

## 3. Calibration, uncertainty и OOD

14. Guo C. et al. On Calibration of Modern Neural Networks. ICML 2017.
    https://proceedings.mlr.press/v70/guo17a.html  
    Применимость: temperature scaling и измерение miscalibration.

15. Geifman Y., El-Yaniv R. Selective Classification for Deep Neural
    Networks. NeurIPS 2017.
    https://papers.nips.cc/paper/7073-selective-classification-for-deep-neural-networks  
    Применимость: risk-coverage и отказ от решения.

16. Lakshminarayanan B. et al. Simple and Scalable Predictive Uncertainty
    Estimation using Deep Ensembles. NeurIPS 2017.
    https://papers.nips.cc/paper/7219-simple-and-scalable-predictive-uncertainty-estimation-using-deep-ensembles  
    Применимость: uncertainty baseline; не предписание обязательной
    архитектуры.

17. Hendrycks D., Gimpel K. A Baseline for Detecting Misclassified and
    Out-of-Distribution Examples in Neural Networks. ICLR 2017.
    https://arxiv.org/abs/1610.02136  
    Применимость: baseline OOD detection; maximum softmax не считается
    достаточным clinical control.

## 4. ML documentation и статистика

18. Mitchell M. et al. Model Cards for Model Reporting. FAT* 2019.
    DOI: 10.1145/3287560.3287596.
    https://doi.org/10.1145/3287560.3287596

19. Gebru T. et al. Datasheets for Datasets. Communications of the ACM.
    2021;64(12):86–92. DOI: 10.1145/3458723.
    https://doi.org/10.1145/3458723

20. DeLong E.R. et al. Comparing the Areas under Two or More Correlated
    Receiver Operating Characteristic Curves: A Nonparametric Approach.
    Biometrics. 1988;44(3):837–845. DOI: 10.2307/2531595.
    https://doi.org/10.2307/2531595

21. Vickers A.J., Elkin E.B. Decision Curve Analysis: A Novel Method for
    Evaluating Prediction Models. Medical Decision Making.
    2006;26(6):565–574. DOI: 10.1177/0272989X06295361.
    https://doi.org/10.1177/0272989X06295361

## 5. Risk management и secure development

22. NIST AI RMF 1.0, NIST AI 100-1. DOI: 10.6028/NIST.AI.100-1.
    https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10  
    Примечание: NIST сообщает, что версия 1.0 находится в процессе revision;
    аудит использует именно опубликованную 1.0.

23. NIST SP 800-218, Secure Software Development Framework v1.1.
    DOI: 10.6028/NIST.SP.800-218.
    https://csrc.nist.gov/pubs/sp/800/218/final

24. OWASP API Security Top 10 — 2023.
    https://owasp.org/API-Security/editions/2023/en/0x11-t10/

25. IMDRF/FDA Good Machine Learning Practice for Medical Device Development.
    Финальный IMDRF документ опубликован в январе 2025.
    https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles

## 6. Европейские официальные источники

26. Regulation (EU) 2024/1689, Artificial Intelligence Act.
    https://eur-lex.europa.eu/eli/reg/2024/1689/oj

27. Regulation (EU) 2017/746 on in vitro diagnostic medical devices,
    consolidated text.
    https://eur-lex.europa.eu/eli/reg/2017/746/2025-01-10

28. European Commission, MDCG endorsed guidance. На дату проверки перечень
    включает MDCG 2025-6 по взаимодействию MDR/IVDR и AI Act, MDCG 2020-1 по
    clinical/performance evaluation software и MDCG 2019-16 rev.1 по
    cybersecurity.
    https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en

## 7. Дополнительные официальные источники, проверенные 2026-07-28

29. ISO 13485:2016, Medical devices — Quality management systems —
    Requirements for regulatory purposes, edition 3.
    https://www.iso.org/standard/59752.html

30. ISO 14971:2019, Medical devices — Application of risk management to
    medical devices, edition 3, confirmed.
    https://www.iso.org/standard/72704.html

31. IEC 62304:2006+A1:2015, Medical device software — Software life cycle
    processes, consolidated edition 1.1.
    https://webstore.iec.ch/en/publication/22794

32. IEC 62366-1:2015+A1:2020, Application of usability engineering to medical
    devices.
    https://webstore.iec.ch/en/publication/59980

33. IEC 81001-5-1:2021, Security — Activities in the product life cycle.
    https://webstore.iec.ch/en/publication/63293

34. ISO/IEC 27001:2022, Information security management systems, edition 3.
    https://www.iso.org/standard/27001

35. WHO, Malaria microscopy quality assurance manual, version 2.
    https://www.who.int/publications/i/item/9789241549394

36. FDA, Software as a Medical Device (SaMD).
    https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd

37. FDA, Transparency for Machine Learning-Enabled Medical Devices: Guiding
    Principles.
    https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles

38. GitHub Docs, policy for requiring actions pinned to full-length commit SHA.
    https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository

## 8. Что не следует выводить из источников

- Публикация о NIH dataset не доказывает происхождение текущей модели.
- Высокая accuracy из другой статьи не переносится на данный artifact.
- Compliance с checklist не равен clinical validity.
- Общий framework не заменяет конкретные risk controls и verification.
- Наличие EU/FDA документов не определяет автоматически класс продукта.
- Formula/sample-size illustration не заменяет protocol биостатистика.
