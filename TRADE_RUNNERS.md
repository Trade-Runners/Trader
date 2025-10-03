Чтобы генерация субмишинов норм отработала, надо всё делать на новых отредаченых файлах:

1)
```bash
poetry run generate-submission --train-file data/processed/corrected_train.csv --test-file data/processed/test_from_train.csv --num-examples 100
```

2)
```bash
poetry run validate-submission
```
тестовый файл можно поменять в файле validate_submission.py в переменной test_path. По умолчанию ```data/processed/test_from_train.csv```

3)
```bash
poetry run calculate-metrics --true data/processed/corrected_train.csv --show-errors 100
```