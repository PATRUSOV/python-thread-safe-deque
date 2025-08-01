# tsdeque — Thread-Safe Deque with Task Tracking ⚙️

---

## English

**tsdeque** is a thread-safe, double-ended queue implementation with built-in task tracking and threshold-based event notifications. Designed for multi-threaded environments, it ensures safe concurrent access and precise control over queue size and task completion status.

### Features
- Thread-safe double-ended queue (`deque`) operations  
- Support for max size limitation with blocking `put` operations  
- Task counting with `task_done()` and `join()` methods, similar to `queue.Queue`  
- Threshold events triggered on hitting min/max counts  
- Customizable blocking timeouts on put/get operations  
- Designed with performance and correctness in mind  

### Installation
```bash
pip install tsdeque
````

### Usage example

```python
from tsdeque import ThreadSafeDeque

deque = ThreadSafeDeque(maxsize=5)
deque.put("item")
item = deque.get()
deque.task_done()
deque.join()
```

### Testing 🧪

Run tests with:

```bash
python -m pytest
```

---

## Русский

**tsdeque** — потокобезопасная двухсторонняя очередь с учетом количества задач и триггерами событий на пороговых значениях. Подходит для многопоточного программирования, гарантирует корректный доступ и управление размером очереди и состоянием задач.

### Возможности

* Потокобезопасные операции с двухсторонней очередью (`deque`)
* Поддержка ограничения по максимальному размеру с блокирующими операциями `put`
* Подсчет задач с методами `task_done()` и `join()`, аналогично `queue.Queue`
* События срабатывают при достижении минимальных и максимальных порогов
* Настраиваемые таймауты блокирующих операций
* Оптимизирован для производительности и надежности

### Установка

```bash
pip install tsdeque
```

### Пример использования

```python
from tsdeque import ThreadSafeDeque

deque = ThreadSafeDeque(maxsize=5)
deque.put("item")
item = deque.get()
deque.task_done()
deque.join()
```

### Тестирование 🧪

Запуск тестов:

```bash
python -m pytest
```

---
