
# Производительность индексов

### Входные параметры
1. Macbook Pro, Apple M2 Pro, 32 GB
2. Количество записей в таблице users: 999_931
3. Количество запросов: 5_000

### Без использования индексов

| Потоков | RPS   | Avg latency | Min latency | Max latency  | Total time |
|---------|-------|-------------|-------------|--------------|------------|
| 1       | 31.19 | 32.05ms     | 28.111ms    | 73.313ms     | 160.29s    |
| 10      | 90.12 | 108.93ms    | 31.952ms    | 285.223ms    | 55.48s     |
| 100     | 96.73 | 1008.82ms   | 32.079ms    | 2988.776ms   | 51.69s     |
| 1000    | 95.08 | 9246.22ms   | 61.66ms     | 31337.478ms  | 52.59s     |


### С использованием инекса B-Tree по полям (first_name, last_name, id)

| Потоков | RPS    | Avg latency | Min latency | Max latency | Total time |
|---------|--------|-------------|-------------|-------------|------------|
| 1       | 287.52 | 3.48ms      | 1.335ms     | 62.438ms    | 17.39s     |
| 10      | 593.12 | 16.82ms     | 3.674ms     | 62.259ms    | 8.43s      |
| 100     | 534.76 | 177.52ms    | 1.634ms     | 1137.092ms  | 9.35s      |
| 1000    | 543.48 | 1489.56ms   | 8.819ms     | 7853.208ms  | 9.2s       |


### Explain запросов после индекса

```
Sort  (cost=324.38..324.44 rows=25 width=978) (actual time=3.193..3.240 rows=1164 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 270kB
  ->  Index Scan using users_name_id_idx on users  (cost=0.42..323.80 rows=25 width=978) (actual time=0.038..2.389 rows=1164 loops=1)
        Index Cond: (((first_name)::text >= 'Ник'::text) AND ((first_name)::text < 'Нил'::text) AND ((last_name)::text >= 'Але'::text) AND ((last_name)::text < 'Алж'::text))
        Filter: (((first_name)::text ~~ 'Ник%'::text) AND ((last_name)::text ~~ 'Але%'::text))
Planning Time: 0.183 ms
Execution Time: 3.281 ms
```

### Oбъяснение почему индекс именно такой

В PostgreSQL, для эффективного поиска поиск по префиксу с `LIKE 'xxx%'` 
по колонкам `first_name`, `last_name` и сортировкой по `id`
подойдет составной B-Tree индекс. 
- Префикс `LIKE 'xxx%` планировкик преобразует в диапазон `WHERE first_name >= 'xxx' AND first_name < 'xxx'`
а так как B-Tree индекс — это сбалансированное дерево, то такой поиск работает эффективно, 
PostgreSQL находит стартовую точку и итерирует по отсортированным значениям.
- так же эффективно рабоатет сортировка `ORDER BY id` так как `id` это часть составного индекса
- при создании таблицы для полей `first_name` и `last_name` нужно указать `COLLATE "C"` для байтового сравнения

Для подстрочных поисков лучше всего использовать GIN-индексы с расширением pg_trgm, 
которое позволяет эффективно искать по шаблонам в стиле %substring%.
